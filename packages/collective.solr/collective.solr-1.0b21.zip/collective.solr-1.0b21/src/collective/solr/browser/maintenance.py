from logging import getLogger
from time import time, clock, strftime
from zope.interface import implements
from zope.component import queryUtility
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.solr.interfaces import ISolrConnectionManager
from collective.solr.interfaces import ISolrMaintenanceView
from collective.solr.interfaces import ISearch
from collective.solr.indexer import indexable, handlers, SolrIndexProcessor
from collective.solr.utils import findObjects
from collective.solr.utils import prepareData

logger = getLogger('collective.solr.maintenance')


def timer(func=time):
    """ set up a generator returning the elapsed time since the last call """
    def gen(last=func()):
        while True:
            elapsed = func() - last
            last = func()
            yield '%.3fs' % elapsed
    return gen()


def checkpointIterator(function, interval=100):
    """ the iterator will call the given function for every nth invocation """
    counter = 0
    while True:
        counter += 1
        if counter % interval == 0:
            function()
        yield None


def notimeout(func):
    """ decorator to prevent long-running solr tasks from timing out """
    def wrapper(*args, **kw):
        manager = queryUtility(ISolrConnectionManager)
        manager.setTimeout(None, lock=True)
        try:
            return func(*args, **kw)
        finally:
            manager.setTimeout(None, lock=False)
    return wrapper


def solrDataFor(uids):
    """ fetch existing index data from solr for object with given uids """
    manager = queryUtility(ISolrConnectionManager)
    search = queryUtility(ISearch)
    schema = manager.getSchema()
    # set up data converters
    converters = {}
    for field in schema.fields():
        name = field['name']
        handler = handlers.get(field.class_, None)
        if handler is not None:
            converters[name] = handler
        elif not field.multiValued:
            separator = getattr(field, 'separator', ' ')
            def conv(value):
                if isinstance(value, (list, tuple)):
                    value = separator.join(value)
                return value
            converters[name] = conv
    # query & convert data for given uids
    key = schema.uniqueKey
    query = '+%s:(%s)' % (key, ' OR '.join(uids))
    flares = {}
    for flare in search(query, rows=len(uids)):
        uid = getattr(flare, key)
        assert uid, 'empty unique key?'
        for name, conv in converters.items():
            if name in flare:
                flare[name] = conv(flare[name])
        flares[uid] = flare
    return flares


class SolrMaintenanceView(BrowserView):
    """ helper view for indexing all portal content in Solr """
    implements(ISolrMaintenanceView)

    def mklog(self):
        """ helper to prepend a time stamp to the output """
        write = self.request.RESPONSE.write
        def log(msg, timestamp=True):
            if timestamp:
                msg = strftime('%Y/%m/%d-%H:%M:%S ') + msg
            write(msg)
        return log

    def optimize(self):
        """ optimize solr indexes """
        manager = queryUtility(ISolrConnectionManager)
        conn = manager.getConnection()
        conn.setTimeout(None)
        conn.commit(optimize=True)
        return 'solr indexes optimized.'

    def clear(self):
        """ clear all data from solr, i.e. delete all indexed objects """
        manager = queryUtility(ISolrConnectionManager)
        uniqueKey = manager.getSchema().uniqueKey
        conn = manager.getConnection()
        conn.setTimeout(None)
        conn.deleteByQuery('%s:[* TO *]' % uniqueKey)
        conn.commit()
        return 'solr index cleared.'

    @notimeout
    def reindex(self, batch=100, skip=0, cache=10000, attributes=None):
        """ find all contentish objects (meaning all objects derived from one
            of the catalog mixin classes) and (re)indexes them """
        manager = queryUtility(ISolrConnectionManager)
        proc = SolrIndexProcessor(manager)
        db = self.context.getPhysicalRoot()._p_jar.db()
        log = self.mklog()
        log('reindexing solr catalog...\n')
        if skip:
            log('skipping indexing of %d object(s)...\n' % skip)
        real = timer()          # real time
        lap = timer()           # real lap time (for intermediate commits)
        cpu = timer(clock)      # cpu time
        processed = 0
        conn = manager.getConnection()
        key = manager.getSchema().uniqueKey
        updates = {}            # list to hold data to be updated
        def checkPoint():
            uids = updates.keys()
            flares = solrDataFor(uids)
            for uid, values in updates.items():
                flare = flares.get(uid, {key: uid})
                flare.update(values)
                conn.add(**flare)
            updates.clear()     # clear pending updates
            log('intermediate commit (%d items processed, '
                'last batch in %s)...\n' % (processed, lap.next()))
            conn.commit()
            manager.getConnection().reset()     # force new connection
            if cache:
                size = db.cacheSize()
                if size > cache:
                    log('minimizing zodb cache with %d objects...\n' % size)
                    db.cacheMinimize()
        single = timer()        # real time for single object
        cpi = checkpointIterator(checkPoint, batch)
        count = 0
        if attributes is not None:
            if not key in attributes:
                attributes.append(key)
            for field in manager.getSchema().fields():
                if not field.stored:    # fields not stored need to be added
                    log('adding non-stored field "%s" to attribute list...\n'
                        % field.name)
                    attributes.append(field.name)
        for path, obj in findObjects(self.context):
            if indexable(obj):
                count += 1
                if count <= skip:
                    continue
                data, missing = proc.getData(obj, attributes)
                prepareData(data)
                if data.get(key, None) is not None and not missing:
                    log('indexing %r' % obj)
                    updates[data[key]] = data
                    processed += 1
                    log(' (%s).\n' % single.next(), timestamp=False)
                    cpi.next()
                    single.next()   # don't count commit time here...
                else:
                    log('missing data, skipping indexing of %r.\n' % obj)
        checkPoint()            # make sure to process the last batch
        log('solr index rebuilt.\n')
        msg = 'processed %d items in %s (%s cpu time).'
        msg = msg % (processed, real.next(), cpu.next())
        log(msg)
        logger.info(msg)

    def metadata(self, index, key, func=lambda x: x, path='/'):
        """ build a mapping between a unique key and a given attribute from
            the portal catalog; catalog metadata must exist for the given
            index """
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog._catalog      # get the real catalog...
        pos = cat.schema[index]
        data = {}
        for uid, rids in cat.getIndex(key).items():
            for rid in rids:
                value = cat.data[rid][pos]
                if value is not None and cat.paths[rid].startswith(path):
                    data[uid] = func(value)
        return data

    def diff(self, path):
        """ determine objects that need to be indexed/reindex/unindexed by
            diff'ing the records in the portal catalog and solr """
        key = queryUtility(ISolrConnectionManager).getSchema().uniqueKey
        uids = self.metadata('modified', key=key,
            func=lambda x: x.millis(), path=path)
        search = queryUtility(ISearch)
        reindex = []
        unindex = []
        rows = len(uids) * 10               # sys.maxint makes solr choke :(
        query = '+%s:[* TO *] +parentPaths:%s' % (key, path)
        for flare in search(query, rows=rows, fl='%s modified' % key):
            uid = getattr(flare, key)
            assert uid, 'empty unique key?'
            if uid in uids:
                if uids[uid] > flare.modified.millis():
                    reindex.append(uid)     # item isn't current
                del uids[uid]               # remove from the list in any case
            else:
                unindex.append(uid)         # item doesn't exist in catalog
        index = uids.keys()
        return index, reindex, unindex

    @notimeout
    def sync(self, batch=100, cache=10000):
        """ sync the solr index with the portal catalog;  records contained
            in the catalog but not in solr will be indexed and records not
            contained in the catalog can be optionally removed;  this can
            be used to ensure consistency between zope and solr after the
            solr server has been unavailable etc """
        manager = queryUtility(ISolrConnectionManager)
        proc = SolrIndexProcessor(manager)
        db = self.context.getPhysicalRoot()._p_jar.db()
        log = self.mklog()
        real = timer()          # real time
        lap = timer()           # real lap time (for intermediate commits)
        cpu = timer(clock)      # cpu time
        path = '/'.join(self.context.getPhysicalPath())
        log('determining differences between portal catalog and solr '
            '(from "%s")...' % path)
        index, reindex, unindex = self.diff(path)
        log(' (%s).\n' % lap.next(), timestamp=False)
        log('operations needed: %d "index", %d "reindex", %d "unindex"\n' % (
            len(index), len(reindex), len(unindex)))
        processed = 0
        def checkPoint():
            msg = 'intermediate commit (%d objects processed, ' \
                  'last batch in %s)...\n' % (processed, lap.next())
            log(msg)
            logger.info(msg)
            proc.commit(wait=True)
            manager.getConnection().reset()     # force new connection
            if cache:
                size = db.cacheSize()
                if size > cache:
                    log('minimizing zodb cache with %d objects...\n' % size)
                    db.cacheMinimize()
        single = timer()        # real time for single object
        cpi = checkpointIterator(checkPoint, batch)
        lookup = getToolByName(self.context, 'reference_catalog').lookupObject
        log('processing %d "index" operations next...\n' % len(index))
        for uid in index:
            obj = lookup(uid)
            if indexable(obj):
                log('indexing %r' % obj)
                proc.index(obj)
                processed += 1
                log(' (%s).\n' % single.next(), timestamp=False)
                cpi.next()
                single.next()   # don't count commit time here...
            else:
                log('not indexing unindexable object %r.\n' % obj)
        log('processing %d "reindex" operations next...\n' % len(reindex))
        for uid in reindex:
            obj = lookup(uid)
            if indexable(obj):
                log('reindexing %r' % obj)
                proc.reindex(obj)
                processed += 1
                log(' (%s).\n' % single.next(), timestamp=False)
                cpi.next()
                single.next()   # don't count commit time here...
            else:
                log('not reindexing unindexable object %r.\n' % obj)
        log('processing %d "unindex" operations next...\n' % len(unindex))
        conn = proc.getConnection()
        for uid in unindex:
            obj = lookup(uid)
            if obj is None:
                log('unindexing %r' % uid)
                conn.delete(id=uid)
                processed += 1
                log(' (%s).\n' % single.next(), timestamp=False)
                cpi.next()
                single.next()   # don't count commit time here...
            else:
                log('not unindexing existing object %r (%r).\n' % (obj, uid))
        proc.commit(wait=True)      # make sure to commit in the end...
        log('solr index synced.\n')
        msg = 'processed %d object(s) in %s (%s cpu time).'
        msg = msg % (processed, real.next(), cpu.next())
        log(msg)
        logger.info(msg)
