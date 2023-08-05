#
# Module implementing queues
#
# processing/queue.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#

__all__ = ['Queue', 'SimpleQueue']

import sys
import os
import threading
import collections
import time
import atexit
import weakref

from Queue import Empty, Full

from processing import _processing, Pipe
from processing.synchronize import Lock, BoundedSemaphore
from processing.logger import debug
from processing.finalize import Finalize
from processing.process import _exit_func, _register_afterfork

#
# Ensure cleanup func of `processing` runs before that of `threading`
#

atexit._exithandlers.remove((_exit_func, (), {}))
atexit._exithandlers.append((_exit_func, (), {}))

#
# Queue type based on a pipe -- uses a buffer and a thread
#

class Queue(object):

    def __init__(self, maxsize=0):
        reader, writer = Pipe(duplex=False)
        rlock = Lock()
        wlock = Lock()
        if maxsize == 0:
            sem = None
        else:
            sem = BoundedSemaphore(maxsize)

        state = maxsize, reader, writer, rlock, wlock, sem, os.getpid()
        self.__setstate__(state)
        
        if sys.platform != 'win32':
            _register_afterfork(self, Queue._afterfork)

    def __setstate__(self, state):
        (self._maxsize, self._reader, self._writer,
         self._rlock, self._wlock, self._sem, self._opid) = state
        self._send = self._writer.send
        self._recv = self._reader.recv
        self._poll = self._reader.poll
        self._afterfork()

    def __getstate__(self):
        assert sys.platform == 'win32'
        assert not self._closed
        return (self._maxsize, self._reader, self._writer,
                self._rlock, self._wlock, self._sem, self._opid)

    def _afterfork(self):
        debug('Queue._afterfork()')
        self._notempty = threading.Condition(threading.Lock())
        self._buffer = collections.deque()
        self._thread = None
        self._jointhread = None
        self._joincancelled = False
        self._closed = False
        self._close = None
        
    def put(self, obj, block=True, timeout=None):
        assert not self._closed
        if self._maxsize:
            if block and timeout is None:
                if self._sem:
                    self._sem.acquire()
            else:
                if not block:
                    timeout = 0.0
                else:
                    timeout = max(0.0, timeout)
                if not self._sem._block.acquire_timeout(timeout):
                    raise Full

        self._notempty.acquire()
        try:
            if self._thread is None:
                self._startthread()
            self._buffer.append(obj)
            self._notempty.notify()
        finally:
            self._notempty.release()

    def putmany(self, iterable):
        assert not self._closed
        assert self._maxsize == 0

        self._notempty.acquire()
        try:
            if self._thread is None:
                self._startthread()
            self._buffer.extend(iterable)
            self._notempty.notify()
        finally:
            self._notempty.release()
        
    def get(self, block=1, timeout=None):
        if block and timeout is None:
            self._rlock.acquire()
            try:
                res = self._recv()
                if self._sem:
                    self._sem.release()
                return res
            finally:
                self._rlock.release()

        else:
            if not block:
                timeout = 0.0
            else:
                timeout = max(0.0, timeout)
            deadline = time.time() + timeout

            if not self._rlock._block.acquire_timeout(timeout):
                raise Empty
            try:
                timeout = max(0.0, deadline - time.time())
                if not self._poll(timeout):
                    raise Empty
                res = self._recv()
                if self._sem:
                    self._sem.release()
                return res
            finally:
                self._rlock.release()

    def empty(self):
        return not self._poll()

    def full(self):
        return bool(self._sem) and self._sem._block._getvalue() == 0

    def get_nowait(self):
        return self.get(False)

    def put_nowait(self, obj):
        return self.put(obj, False)

    def close(self):
        self._closed = True
        if self._close:
            self._close()

    def jointhread(self):
        debug('Queue.jointhread()')
        assert self._closed
        if self._jointhread:
            self._jointhread()
            
    def canceljoin(self):
        debug('Queue.canceljoin()')
        self._joincancelled = True
        try:
            self._jointhread.cancel()
        except AttributeError:
            pass

    def _startthread(self):
        debug('Queue._startthread()')
        
        # Start thread which transfers data from buffer to pipe
        self._buffer.clear()
        self._thread = threading.Thread(
            target=Queue._feed,
            args=[self._buffer, self._notempty, self._send, self._wlock],
            name='QueueFeederThread'
            )
        self._thread.setDaemon(True)

        debug('doing self._thread.start() %s' % self._thread)
        self._thread.start()
        debug('... done self._thread.start()')

        # On process exit we will wait for data to be flushed to pipe.
        #
        # However, if this process created the queue then all
        # processes which use the queue will be descendants of this
        # process.  Therefore waiting for the queue to be flushed
        # is pointless once all the child processes have been joined.
        created_by_this_process = (self._opid == os.getpid())
        if not self._joincancelled and not created_by_this_process:
            self._jointhread = Finalize(
                self._thread, Queue._finalize_join,
                [weakref.ref(self._thread)],
                exitpriority=-5
                )
            
        # Send sentinel to the thread queue object when garbage collected
        self._close = Finalize(
            self, Queue._finalize_close,
            [self._buffer, self._notempty],
            exitpriority=10
            )
        
    @staticmethod
    def _finalize_join(twr):
        debug('joining queue thread')
        thread = twr()
        if thread is not None:
            thread.join()
            debug('... queue thread joined')
        else:
            debug('... queue thread already dead')
            
    @staticmethod 
    def _finalize_close(buffer, notempty):
        debug('telling thread used by a buffered queue to quit')
        notempty.acquire()
        try:
            buffer.append(_sentinel)
            notempty.notify()
        finally:
            notempty.release()              

    @staticmethod
    def _feed(buffer, notempty, send, writelock):
        debug('starting thread to feed data to pipe')
        try:
            while 1:
                notempty.acquire()
                try:
                    if not buffer:
                        notempty.wait()
                finally:
                    notempty.release()
                try:
                    while 1:
                        obj = buffer.popleft()
                        if obj is _sentinel:
                            debug('feeder thread got sentinel -- exiting')
                            return

                        writelock.acquire()
                        try:
                            send(obj)
                        finally:
                            writelock.release()
                except IndexError:
                    pass
        except Exception, e:
            # Since this runs in a daemon thread the objects it uses
            # may be become unusable while the process is cleaning up.
            # We ignore errors which happen after the process has
            # started to cleanup.
            debug('error in queue thread: %s', e)
            if not Finalize._exiting:
                raise

_sentinel = object()

#
# Simplified Queue type -- really just a locked pipe
#

class SimpleQueue(object):

    def __init__(self):
        reader, writer = Pipe(duplex=False)
        if sys.platform == 'win32':
            state = reader, writer, Lock(), None
        else:
            state = reader, writer, Lock(), Lock()
        self.__setstate__(state)

    def empty(self):
        return not self._reader.poll()

    def __setstate__(self, state):
        self._reader, self._writer, self._rlock, self._wlock = state

        recv = self._reader.recv
        racquire, rrelease = self._rlock.acquire, self._rlock.release
        def get():
            racquire()
            try:
                return recv()
            finally:
                rrelease()
        self.get = get

        if self._wlock is None:
            # writes to a message oriented win32 pipe are atomic
            self.put = self._writer.send
        else:
            send = self._writer.send
            wacquire, wrelease = self._wlock.acquire, self._wlock.release
            def put(obj):
                wacquire()
                try:
                    return send(obj)
                finally:
                    wrelease()
            self.put = put
        
    def __getstate__(self):
        assert sys.platform == 'win32'
        return self._reader, self._writer, self._rlock, self._wlock

