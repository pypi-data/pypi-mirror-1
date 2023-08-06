#
# Module implementing queues
#
# processing/queue.py
#
# Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
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

from processing import _processing, Pipe, currentProcess
from processing.synchronize import Lock, BoundedSemaphore
from processing.logger import debug, subwarning
from processing.finalize import Finalize
from processing.process import _exit_func, _register_afterfork
from processing.forking import PicklableOnlyForInheritance

#
# Cleanup function of `processing` should run before that of `threading`
#

atexit._exithandlers.remove((_exit_func, (), {}))
atexit._exithandlers.append((_exit_func, (), {}))

#
# Queue type using a pipe, buffer and thread
#

class Queue(PicklableOnlyForInheritance):

    def __init__(self, maxsize=0):
        reader, writer = Pipe(duplex=False)
        rlock = Lock()
        if sys.platform == 'win32':
            wlock = None
        else:
            wlock = Lock()
        if maxsize < 0:
            maxsize = 0
        if maxsize == 0:
            sem = None
        else:
            sem = BoundedSemaphore(maxsize)

        state = maxsize, reader, writer, rlock, wlock, sem, os.getpid()
        self._setstate(state)
        
        if sys.platform != 'win32':
            _register_afterfork(self, Queue._afterfork)

    def _setstate(self, state):
        (self._maxsize, self._reader, self._writer,
         self._rlock, self._wlock, self._sem, self._opid) = self._state = state
        self._send = self._writer.send
        self._recv = self._reader.recv
        self._poll = self._reader.poll
        self._afterfork()

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
        if self._sem is not None:
            if not self._sem.acquire(block, timeout):
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
        
    def get(self, block=True, timeout=None):
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
            if block:
                deadline = time.time() + timeout
            if not self._rlock.acquire(block, timeout):
                raise Empty
            try:
                if not self._poll(block and (deadline-time.time()) or 0.0):
                    raise Empty
                res = self._recv()
                if self._sem:
                    self._sem.release()
                return res
            finally:
                self._rlock.release()

    def empty(self):
        # Even more unreliable than Queue.Queue.empty(): True can be
        # returned when enqueued items are buffered but none are
        # yet in the pipe
        return not self._poll()

    def full(self):
        return bool(self._sem) and self._sem._semlock._getvalue() == 0

    def get_nowait(self):
        return self.get(False)

    def put_nowait(self, obj):
        return self.put(obj, False)

    def close(self):
        self._closed = True
        self._reader.close()
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
            args=(self._buffer, self._notempty, self._send,
                  self._wlock, self._writer.close),
            name='QueueFeederThread'
            )
        self._thread.setDaemon(True)

        debug('doing self._thread.start()')
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
        debug('telling queue thread to quit')
        notempty.acquire()
        try:
            buffer.append(_sentinel)
            notempty.notify()
        finally:
            notempty.release()              

    @staticmethod
    def _feed(buffer, notempty, send, writelock, close):
        debug('starting thread to feed data to pipe')

        nacquire = notempty.acquire
        nrelease = notempty.release
        nwait = notempty.wait
        bpopleft = buffer.popleft
        sentinel = _sentinel
        if sys.platform != 'win32':
            wacquire = writelock.acquire
            wrelease = writelock.release
        else:
            wacquire = None
        
        try:
            while 1:
                nacquire()
                try:
                    if not buffer:
                        nwait()
                finally:
                    nrelease()
                try:
                    while 1:
                        obj = bpopleft()
                        if obj is sentinel:
                            debug('feeder thread got sentinel -- exiting')
                            close()
                            return

                        if wacquire is None:
                            send(obj)
                        else:
                            wacquire()
                            try:
                                send(obj)
                            finally:
                                wrelease()                        
                except IndexError:
                    pass
        except Exception, e:
            # Since this runs in a daemon thread the objects it uses
            # may be become unusable while the process is cleaning up.
            # We ignore errors which happen after the process has
            # started to cleanup.
            if getattr(currentProcess(), '_exiting', False):
                subwarning('error in queue thread: %s', e)
            else:
                raise

_sentinel = object()

#
# Simplified Queue type -- really just a locked pipe
#

class SimpleQueue(PicklableOnlyForInheritance):

    def __init__(self):
        reader, writer = Pipe(duplex=False)
        if sys.platform == 'win32':
            state = reader, writer, Lock(), None
        else:
            state = reader, writer, Lock(), Lock()
        self._setstate(state)

    def empty(self):
        return not self._reader.poll()

    def _setstate(self, state):
        (self._reader, self._writer, self._rlock, self._wlock) \
                       = self._state = state

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
