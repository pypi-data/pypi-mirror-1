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
"""

import os

import simplejson

from twisted.internet import defer
from twisted.python import log
from twisted.internet import error



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

    def __init__(self, state_file = None):
        self._queue = []

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

        if not self._queue:
            log.msg("Nothing in the queue...")
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
            return success_count, fail_count

        l.addCallback(cb)
        return l


class Task(object):
    value = None
    status = 'new'

    def __init__(self, value):
        self.value = value


class TaskNotAssociatedError(Exception):
    """
    This task is not associated with this queue.
    """


class TaskQueue(object):
    """
    An event driven task queue.

    Values may be added as usual to this queue. When an attempt is
    made to retrieve a value when the queue is empty, a Deferred is
    returned which will fire when a value becomes available.
    """

    def __init__(self):
        self.waiting = []
        self._tasks = set()
        self.pending = []

    def createTask(self, value):
        task = Task(value)
        task.queue = self
        self._tasks.add(task)
        return task


    def _enqueue(self, task):
        """
        Enqueue a task.

        If a consumer is waiting, its callback is called with the task,
        otherwise it is in the queue of pending tasks.
        """
        if self.waiting:
            task.status = 'in_progress'
            self.waiting.pop(0).callback(task)
        else:
            self.pending.append(task)


    def put(self, value):
        """
        Create a new task and add it the queue.

        When retrieving the enqueued task, the value is stored in the
        C{value} attribute of the task instance.

        @param value: The value that represents the task.
        @return: The new task.
        """
        task = self.createTask(value)
        self._enqueue(task)
        return task


    def get(self):
        """
        Attempt to retrieve and remove a task from the queue.

        The returned task will contain the value as it was queued with L{put}
        in the C{value} attribute. As the queue keeps track of created tasks,
        it is required to call L{retry}, L{fail} or L{done} after
        processing the task.

        @return: A Deferred which fires with the next task available in the
            queue.
        """
        if self.pending:
            task = self.pending.pop(0)
            task.status = 'in_progress'
            return defer.succeed(task)
        else:
            d = defer.Deferred()
            self.waiting.append(d)
            return d


    def retry(self, task):
        """
        Retry a task.

        The task, gotten through L{get}, is requeued for later retry.
        """
        if not task in self._tasks:
            raise TaskNotAssociatedError()

        task.status = 'retryable'
        self._enqueue(task)


    def fail(self, task):
        """
        Fail a task.

        The task, gotten through L{get}, is not requeued for later retry,
        but kept in L{tasks} for later inspection. The task can be retried
        by calling L{retry}.
        """

        if not task in self._tasks:
            raise TaskNotAssociatedError()

        task.status = 'failed'


    def succeed(self, task):
        """
        Succeed a task.

        The task, gotten through L{get}, is not requeued and removed from
        its record of tasks in L{tasks}.
        """

        if not task in self._tasks:
            raise TaskNotAssociatedError()

        task.status = 'done'
        self._tasks.remove(task)



class SQLiteTaskQueue(object):
    """
    An event driven task queue.

    Values may be added as usual to this queue. When an attempt is
    made to retrieve a value when the queue is empty, a Deferred is
    returned which will fire when a value becomes available.
    """

    def __init__(self, connection):
        self._connection = connection
        self._cursor = connection.cursor()

        self.waiting = []
        self.pending = []

        self.fillQueue()


    def fillQueue(self):
        try:
            self._cursor.execute("""SELECT rowid, value, status FROM tasks
                                    WHERE status != 'failed'""")
        except self._connection.OperationalError:
            # table does not exist. Try to create it
            self._cursor.execute("""CREATE TABLE tasks (value text,
                                                        status text)""")
            self._connection.commit()
        else:
            for rowid, value, status in self._cursor:
                try:
                    task = Task(simplejson.loads(value))
                except ValueError:
                    log.msg("Invalid task in storage: %d, %r" % (rowid, value))
                    continue

                task.identifier = rowid
                task.status = status
                task.queue = self
                self._enqueue(task)


    def createTask(self, value):
        task = Task(value)
        self._cursor.execute("""INSERT INTO tasks (value, status)
                                VALUES (?, 'new')""",
                             (simplejson.dumps(value),))
        self._connection.commit()
        task.identifier = self._cursor.lastrowid
        task.queue = self
        return task


    def _enqueue(self, task):
        """
        Enqueue a task.

        If a consumer is waiting, its callback is called with the task,
        otherwise it is in the queue of pending tasks.
        """
        if self.waiting:
            task.status = 'in_progress'
            self.waiting.pop(0).callback(task)
        else:
            self.pending.append(task)


    def put(self, value):
        """
        Create a new task and add it the queue.

        When retrieving the enqueued task, the value is stored in the
        C{value} attribute of the task instance.

        @param value: The value that represents the task.
        @return: The new task.
        """
        task = self.createTask(value)
        self._enqueue(task)
        return task


    def get(self):
        """
        Attempt to retrieve and remove a task from the queue.

        The returned task will contain the value as it was queued with L{put}
        in the C{value} attribute. As the queue keeps track of created tasks,
        it is required to call L{retry}, L{fail} or L{done} after
        processing the task.

        @return: A Deferred which fires with the next task available in the
            queue.
        """
        if self.pending:
            task = self.pending.pop(0)
            task.status = 'in_progress'
            return defer.succeed(task)
        else:
            d = defer.Deferred()
            self.waiting.append(d)
            return d


    def retry(self, task):
        """
        Retry a task.

        The task, gotten through L{get}, is requeued for later retry.
        """
        if task.queue != self:
            raise TaskNotAssociatedError()

        self._cursor.execute("""UPDATE tasks SET status='retryable'
                                WHERE rowid=?""",
                             (task.identifier,))
        if self._cursor.rowcount < 1:
            raise TaskNotAssociatedError()

        self._connection.commit()

        task.status = 'retryable'
        self._enqueue(task)


    def fail(self, task):
        """
        Fail a task.

        The task, gotten through L{get}, is not requeued for later retry,
        but kept in L{tasks} for later inspection. The task can be retried
        by calling L{retry}.
        """

        if task.queue != self:
            raise TaskNotAssociatedError()

        self._cursor.execute("UPDATE tasks SET status='failed' WHERE rowid=?",
                             (task.identifier,))
        if self._cursor.rowcount < 1:
            raise TaskNotAssociatedError()

        self._connection.commit()

        task.status = 'failed'


    def succeed(self, task):
        """
        Succeed a task.

        The task, gotten through L{get}, is not requeued and removed from
        its record of tasks in L{tasks}.
        """

        if task.queue != self:
            raise TaskNotAssociatedError()

        self._cursor.execute("""DELETE FROM tasks WHERE rowid=?""",
                             (task.identifier,))
        if self._cursor.rowcount < 1:
            raise TaskNotAssociatedError()

        self._connection.commit()

        task.status = 'done'



class RetryError(Exception):
    """
    Container of a failure to signal that retries are possible.
    """
    def __init__(self, failure):
        Exception.__init__(self, failure)
        self.subFailure = failure



class TaskQueueRunner(object):
    """
    Basic submission queue runner.

    This runner makes no assumptions on the types of tasks and retry
    behaviour. Once L{run} is called, it reschedules itself according
    to L{delay}.
    """

    clock = None
    delay = 0

    def __init__(self, queue, callable):
        self.queue = queue
        self.callable = callable

        if self.clock is None:
            from twisted.internet import reactor
            self.clock = reactor

        self.run()


    def run(self):
        def succeed(_, task):
            self.queue.succeed(task)

        def retry(failure, task):
            failure.trap(RetryError)
            log.err(failure.value.subFailure.value, "Retrying task")
            self.queue.retry(task)

        def fail(failure, task):
            log.err(failure.value, "Failing task")
            self.queue.fail(task)


        def call(task):
            d = self.callable(task.value)
            d.addCallback(succeed, task)
            d.addErrback(retry, task)
            d.addErrback(fail, task)
            return d

        d = self.queue.get()
        d.addCallback(call)
        d.addCallback(lambda _: self.clock.callLater(self.delay, self.run))



class APIQueuer(object):

    def __init__(self, queue, controller):
        self.queue = queue
        self.controller = controller
        self.runner = TaskQueueRunner(self.queue, self.doMethod)


    def add(self, method, args):
        value = (method, args)
        task = self.queue.put(value)


    def doMethod(self, value):
        def trapConnectError(failure):
            failure.trap(error.ConnectError,
                         error.TimeoutError,
                         error.ConnectionClosed)
            self.runner.delay = 5
            raise RetryError(failure)

        def succeeded(result):
            self.runner.delay = 0
            
        method, args = value
        d = defer.maybeDeferred(getattr(self.controller, method), args)
        d.addCallback(succeeded)
        d.addErrback(trapConnectError)
        return d
