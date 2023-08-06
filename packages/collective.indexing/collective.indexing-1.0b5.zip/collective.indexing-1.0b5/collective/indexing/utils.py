from zope.component import queryUtility, getUtilitiesFor
from collective.indexing.interfaces import IIndexing
from collective.indexing.interfaces import IIndexQueueSwitch
from collective.indexing.queue import getQueue
from collective.indexing.config import AUTO_FLUSH


def isActive():
    return queryUtility(IIndexQueueSwitch) is not None


def getIndexer():
    """ look for and return an indexer """
    if isActive():                  # when switched on...
        return getQueue()           # return a (thread-local) queue object...
    indexers = list(getUtilitiesFor(IIndexing))
    if len(indexers) == 1:
        return indexers[0][1]       # directly return unqueued indexer...
    elif not indexers:
        return None                 # or none...
    else:
        assert len(indexers) < 1, 'cannot use multiple direct indexers; please enable queueing'


def autoFlushQueue():
    """ process the queue (for this thread) immediately if the
        auto-flushing feature was enabled """
    if isActive() and AUTO_FLUSH:
        return getQueue().process()

