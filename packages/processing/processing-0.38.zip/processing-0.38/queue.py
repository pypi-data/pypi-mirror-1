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

from processing import _processing, process, Pipe
from processing.synchronize import Lock, BoundedSemaphore
from processing.process import debug, Finalize
from Queue import Empty, Full

#
# Ensure cleanup func of `processing` runs before that of `threading`
#

atexit._exithandlers.remove((process._exit_func, (), {}))
atexit._exithandlers.append((process._exit_func, (), {}))

#
# Queue type based on a pipe -- uses a buffer and a thread
#

class Queue(object):

    def __init__(self, maxsize=0):
        if sys.platform == 'win32':
            from processing.connection import Listener, Client
            l = Listener()
            reader = Client(l.address)
            writer = l.accept()
        else:
            rfd, wfd = os.pipe()
            reader = _processing.SocketConnection(rfd)
            writer = _processing.SocketConnection(wfd)
            os.close(rfd), os.close(wfd)

        rlock = Lock()
        wlock = Lock()
        if maxsize == 0:
            sem = None
        else:
            sem = BoundedSemaphore(maxsize)

        state = maxsize, reader, writer, rlock, wlock, sem, os.getpid()
        self.__setstate__(state)

    def __setstate__(self, state):
        (self._maxsize, self._reader, self._writer,
         self._rlock, self._wlock, self._sem, self._opid) = state
        self._closed = False
        self._close = None
        self._jointhread = None
        self._send = self._writer.send
        self._recv = self._reader.recv
        self._poll = self._reader.poll
        self._notempty = threading.Condition(threading.Lock())
        self._buffer = collections.deque()
        self._thread = None

    def __getstate__(self):
        return (self._maxsize, self._reader, self._writer,
                self._rlock, self._wlock, self._sem, self._opid)

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

    def qsize(self):
        raise NotImplementedError

    def empty(self):
        return not self._poll()

    def full(self):
        return bool(self._wsem) and self._wsem._block._getvalue() == 0

    def get_nowait(self, obj):
        return self.get(obj, False)

    def put_nowait(self, obj):
        return self.put(obj, False)

    def close(self):
        if self._close:
            self._close()
        self._closed = True

    def jointhread(self):
        assert self._closed
        if self._jointhread:
            self._jointhread()

    def canceljoin(self):
        self._jointhread.cancel()

    def _startthread(self):
        # Start thread which transfers data from buffer to pipe
        self._thread = threading.Thread(
            target=Queue._feed,
            args=[self._buffer, self._notempty, self._send, self._wlock]
            )
        self._thread.setDaemon(True)
        self._thread.start()

        # Send sentinel to the thread queue object is garbage collected
        self._close = Finalize(
            self, Queue._finalize_close,
            [self._buffer, self._notempty],
            priority=10, atexit=True
            )
        
        # Flush data to pipe
        self._jointhread = Finalize(
            self._thread, Queue._finalize_join,
            [weakref.ref(self._thread)],
            atexit=True
            )

        # Don't bother joining on exit if this process created the queue
        if self._opid == os.getpid():
            self._jointhread.cancel()
        
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

_sentinel = object()

#
# Simplified Queue type -- really just a locked pipe
#

class SimpleQueue(object):

    def __init__(self):
        if sys.platform == 'win32':
            from processing.connection import Listener, Client
            l = Listener()
            reader = Client(l.address)
            writer = l.accept()
            state = reader, writer, Lock(), None
        else:
            rfd, wfd = os.pipe()
            reader = _processing.SocketConnection(rfd)
            writer = _processing.SocketConnection(wfd)
            os.close(rfd), os.close(wfd)
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
        # state will only be picklable on windows
        return self._reader, self._writer, self._rlock, self._wlock

#
# Queue type based on a posix queue
#

if hasattr(_processing, 'Queue'):

    class PosixQueue(_processing.Queue):

        _count = 0
        _count_lock = threading.RLock()
        _defaults = None

        def __init__(self, maxsize=0, msgsize=0):
            assert maxsize >= 0 and msgsize >= 0

            PosixQueue._count_lock.acquire()
            try:
                PosixQueue._count += 1
                count = PosixQueue._count
            finally:
                PosixQueue._count_lock.release()

            _name = '/pyq-%s-%s' % (os.getpid(), count)

            if (maxsize, msgsize) != (0, 0):
                defmaxsize, defmsgsize = self.getdefaults()
                maxsize = maxsize or defmaxsize
                msgsize = msgsize or defmsgsize

            _processing.Queue.__init__(self, maxsize, msgsize, _name, True)

            # We immediately unlink the name of the queue since
            # otherwise the queue might not get removed (till the next
            # reboot) if python gets killed.  This means that `Queue`
            # objects are not picklable, but that does not prevent a
            # child process from using a `Queue` object inherited from
            # its parent.
            self._unlink()

        def get_nowait(self):
            return self.get(False)

        def put_nowait(self, item):
            return self.put(item, False)

        @staticmethod
        def getdefaults():
            PosixQueue._count_lock.acquire()
            try:
                if PosixQueue._defaults is None:
                    temp = PosixQueue()
                    PosixQueue._defaults = (temp._maxmsg, temp._msgsize)
                    temp._close()
                return PosixQueue._defaults
            finally:
                PosixQueue._count_lock.release()

    __all__ += ['PosixQueue']
