# -*- test-case-name: anymeta.test.test_queue -*-
#
# Copyright (c) 2009 Mediamatic Lab
# See LICENSE for details.

"""
Module containing a submit queue. The L{PersistentQueue} class is a
generic class for the submission of items to an online service.

The queue can be saved on program exit and retrieved on startup.
Items in the queue are processed L{PersistentQueue.processItems} through a
user-defined callback function which is expected to return a deferred
result. On the failure of this deferred, the corresponding item gets
placed back in the queue for later retry. On the deferred's success,
the item gets removed from the queue.

There is no order preservation: On an item's failure, it is pushed
back to the end of the queue and thus is retried on a later moment.

A locking mechanism is in place so that L{PersistentQueue.processItems} is
called only once.
"""

import os

import simplejson

from twisted.internet import defer
from twisted.python import log



class PersistentQueue(object):
    """
    Implementation of a queue for the failsafe processing of items
    through an API call.

    Note that L{PersistentQueue.save} needs explicitly be called for
    the queue to be saved.
    """

    # Private variables
    _queue = None
    _state_file = None
    _lock = None

    def __init__(self, state_file = None):
        self._queue = []
        self._lock = defer.DeferredLock()

        if state_file:
            self._state_file = state_file
        self._state_file = os.path.expanduser(self._state_file)
        if os.path.exists(self._state_file):
            self._queue = simplejson.load(open(self._state_file, 'r'))

        
    def save(self):
        """
        Saves the current queue to the state file. When the queue is
        empty, it is not saved and the state file is thrown away.
        """
        if len(self._queue):
            log.msg("Saving submit queue state.")
            simplejson.dump( self._queue, open(self._state_file, 'w'))
            
        elif os.path.exists(self._state_file):
            os.unlink(self._state_file)


        
    def add(self, item):
        """
        Adds an item to the queue.
        """
        self._queue.append(item)


    def size(self):
        """
        Returns the current size of the queue.
        """
        return len(self._queue)
    
    
    def processBatch(self, callable, max=10):
        """
        Process the next batch of items which are waiting to be
        sent. For every item, the callable is called which is expected
        to return a deferred.

        This function itself returns a deferred which will fire when
        the entire current batch has completed. Return value of this
        deferred is a (success count, fail count) tuple.
        """

        l = self._lock.acquire()
        l.addCallback(self._processBatch, callable, max)
        return l
    

    def _processBatch(self, lock, callable, max=10):

        if not self._queue:
            log.msg("Nothing in the queue...")
            lock.release()
            return defer.succeed(True)

        items, self._queue = self._queue[:max], self._queue[max:]
        log.msg("Submitting %d item(s)" % len(items))
        
        ds = []
        for item in items:
            ds.append(callable(item))

        l = defer.DeferredList(ds, consumeErrors = True)

        def cb(result):
            i = 0
            success_count = 0
            fail_count    = 0
            
            for state, r in result:
                if not state or not r:
                    # submission of item failed, re-add it to queue
                    self._queue.append(items[i])
                    log.err("Submit of %s failed!" % items[i])
                    log.err(r)
                    fail_count += 1
                else:
                    # submission succeeded
                    success_count += 1
                i += 1
                
            lock.release()
            return success_count, fail_count

        l.addErrback(lambda _: lock.release())
        l.addCallback(cb)
        return l



