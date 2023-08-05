#
# Module implementing synchronization primitives and queues.
#
# processing/synchronize.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#
# The C extension `_processing` will be used if available.
#

__all__ = [ 'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Condition',
            'Event', 'PipeQueue', 'BufferedPipeQueue' ]

import threading
import os
import sys
import process
import _processing
import collections
import itertools

from Queue import Full, Empty
from struct import pack as _pack, unpack as _unpack, calcsize as _calcsize
from time import time as _time, sleep as _sleep

#
# Constants to describe the kind of blocker
#

MUTEX = 0
RECURSIVE_MUTEX = 1
SEMAPHORE = 2
BOUNDED_SEMAPHORE = 3

#
# Globals used for generating names
#

_nextid = itertools.count().next

#
# Base class for semaphores and mutexes; wraps `_processing.Blocker`
#

class Blocker(object):

    def __init__(self, kind, value, name):
        counter = _nextid()

        if name is None:
            name = '/pys-%s-%s' % (os.getpid(), counter)
            self._block = _processing.Blocker(
                name=name, create=True, kind=kind, value=value
                )
            process.debug('Creating blocker with name %r' % name)

            if sys.platform != 'win32':
                # On Unix we immediately unlink the name of the
                # semaphore since otherwise the semaphore might not
                # get removed (till the next reboot) if python gets
                # killed.  This means that `Blocker` objects are not
                # picklable on Unix, but that does not prevent a child
                # process from using a `Blocker` object inherited from
                # its parent.
                self._block._unlink()
        else:
            self._block = _processing.Blocker(
                name=name, create=False, kind=kind, value=value
                )

        self._name = name
        if kind == BOUNDED_SEMAPHORE:
            self._maxvalue = value
        else:
            self._maxvalue = -1
        self._kind = kind

        if kind in (MUTEX, RECURSIVE_MUTEX) and sys.platform != 'win32':
            # On Unix a semaphore masquerading as a mutex will not be
            # automatically released when the process that owns it is
            # terminated by `os._exit()`.  To be safe we try to make sure
            # `self._block._close()` will be called before `os._exit()`.
            process.Finalize(self, self._block._close, atexit=True)

        self.acquire = self._block.acquire
        self.release = self._block.release

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, t, v, tb):
        self.release()

    def __reduce__(self):
        raise NotImplementedError

#
# Semaphore
#

class Semaphore(Blocker):

    def __init__(self, value=1, _name=None):
        Blocker.__init__(self, SEMAPHORE, value, _name)

    def getValue(self):
        return self._block._getvalue()

    def __repr__(self):
        try:
            return '<Semaphore(value=%r)>' % self._block._getvalue()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            return object.__repr__(self)

    if sys.platform == 'win32':

        def __reduce__(self):
            return (type(self), (-1, self._name))

#
# Bounded semaphore
#

class BoundedSemaphore(Semaphore):

    def __init__(self, value=1, _name=None):
        Blocker.__init__(self, BOUNDED_SEMAPHORE, value, _name)

    def __repr__(self):
        try:
            return '<BoundedSemaphore(value=%r, maxvalue=%r)>' % \
                   (self._block._getvalue(), self._maxvalue)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            return object.__repr__(self)

    if sys.platform == 'win32':

        def __reduce__(self):
            return (type(self), (self._maxvalue, self._name))

#
# Non-recursive lock -- releasing an unowned lock raises AssertionError
#

class Lock(Blocker):

    def __init__(self, _name=None):
        Blocker.__init__(self, MUTEX, 1, _name)

    def __repr__(self):
        try:
            return '<Lock(ismine=%r)>' % bool(self._block._ismine())
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            return object.__repr__(self)

    if sys.platform == 'win32':

        def __reduce__(self):
            return (type(self), (self._name,))

#
# Recursive lock
#

class RLock(Blocker):

    def __init__(self, _name=None):
        Blocker.__init__(self, RECURSIVE_MUTEX, 1, _name)

    def __repr__(self):
        try:
            if self._block._ismine():
                name = process.currentProcess().getName()
                if threading.currentThread().getName() != 'MainThread':
                    name += '|' + threading.currentThread().getName()
                return '<RLock(%s, %s)>' % (name, self._block._count())
            elif self._block._getvalue() == 1:
                return '<RLock(None, 0)>'
            elif self._block._count() > 0:
                return '<RLock(SomeOtherThread, nonzero)>'
            else:
                return '<RLock(SomeOtherProcess, nonzero)>'
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            raise
            return object.__repr__(self)

    if sys.platform == 'win32':

        def __reduce__(self):
            return (type(self), (self._name,))

#
# Condition variable
#

class Condition(object):

    def __init__(self, lock=None, _extra=None):
        self._lock = lock or RLock()
        if _extra is None:
            _extra = (Semaphore(0), Semaphore(0), Semaphore(0))
        self._sleeping_count, self._woken_count, self._wait_semaphore = _extra
        self.acquire = self._lock.acquire
        self.release = self._lock.release

    def __repr__(self):
        try:
            num_waiters = (self._sleeping_count._block._getvalue() -
                           self._woken_count._block._getvalue())
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            num_waiters = 'unkown'
        return '<Condition(%r, %s)>' % (self._lock, num_waiters)

    def wait(self, timeout=None):
        assert self._lock._block._ismine(), \
               'must acquire() condition before using wait()'

        # get number of times the lock has been acquired by this thread
        count = self._lock._block._count()

        # indicate that this thread will soon be waiting for notification
        self._sleeping_count.release()

        # release lock
        for i in xrange(count):
            self._lock.release()

        try:
            # wait for notification
            if timeout is None:
                self._wait_semaphore.acquire()
            else:
                self._wait_semaphore._block.acquire_timeout(timeout)
        finally:
            # indicate that this thread is no longer waiting
            self._woken_count.release()

            # reacquire lock
            for i in xrange(count):
                self._lock.acquire()

    def notify(self, n=1):
        assert self._lock._block._ismine(), \
               'must acquire() condition before using notify()'

        # wake up `count` waiting threads where `count` is the minimum of
        # `n` and the value of the `self._sleeping_count` semaphore
        # (which gets reduced by `count`)
        count = 0
        while count < n and self._sleeping_count.acquire(False):
            self._wait_semaphore.release()
            count += 1
            
        for i in xrange(count):
            self._woken_count.acquire()

    def notifyAll(self):
        self.notify(sys.maxint)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, t, v, tb):
        self.release()

    if sys.platform == 'win32':

        def __reduce__(self):
            return Condition, (self._lock, (self._sleeping_count,
                               self._woken_count, self._wait_semaphore))

#
# Event
#

class Event(object):

    def __init__(self):
        self._cond = Condition(Lock())
        self._flag = Semaphore(0)

    def isSet(self):
        return bool(self._flag._block._getvalue())

    def set(self):
        self._cond.acquire()
        try:
            if not self.isSet():
                self._flag.release()
            self._cond.notifyAll()
        finally:
            self._cond.release()

    def clear(self):
        self._cond.acquire()
        try:
            self._flag.acquire(False)
            assert not self.isSet()
        finally:
            self._cond.release()

    def wait(self, timeout=None):
        self._cond.acquire()
        try:
            if not self.isSet():
                self._cond.wait(timeout)
        finally:
            self._cond.release()

#
# A Queue bases on a pipe
#

class PipeQueue(object):

    def __init__(self, maxsize=0, _extra=None):
        self._maxsize = maxsize

        if _extra is None:
            if sys.platform == 'win32':
                from processing.connection import Listener, Client
                l = Listener()
                reader = Client(l.address)
                writer = l.accept()
            else:
                rfd, wfd = os.pipe()
                reader = _processing.SocketConnection(rfd)
                writer = _processing.SocketConnection(wfd)

            rlock = RLock()
            wlock = RLock()
            if maxsize <= 0:
                wsem = None
            else:
                wsem = BoundedSemaphore(maxsize)

            self._extra = reader, writer, rlock, wlock, wsem
        else:
            self._extra = reader, writer, rlock, wlock, wsem = _extra

        self._wsem = wsem
        self._read_acquire = rlock.acquire
        self._read_acquire_timeout = rlock._block.acquire_timeout
        self._read_release = rlock.release
        self._write_acquire = wlock.acquire
        self._write_acquire_timeout = wlock._block.acquire_timeout
        self._write_release = wlock.release
        self._put = writer.send
        self._get = reader.recv
        self._poll = reader.poll

    def get(self, block=1, timeout=None):

        if block == 1 and timeout is None:
            self._read_acquire()
            try:
                res = self._get()
                if self._wsem:
                    self._wsem.release()
                return res
            finally:
                self._read_release()

        else:
            if block == 0:
                timeout = 0.0
            else:
                timeout = max(0.0, timeout)
            deadline = _time() + timeout

            if not self._read_acquire_timeout(timeout):
                raise Empty
            try:
                timeout = max(0.0, deadline - _time())
                if not self._poll(timeout):
                    raise Empty
                res = self._get()
                if self._wsem:
                    self._wsem.release()
                return res
            finally:
                self._read_release()

    def put(self, obj, block=1, timeout=None):

        if block == 1 and timeout is None:
            self._write_acquire()
            try:
                if self._wsem:
                    self._wsem.acquire()
                self._put(obj)
            finally:
                self._write_release()

        else:
            if block == 0:
                timeout = 0.0
            else:
                timeout = max(0.0, timeout)
            deadline = _time() + timeout

            if not self._write_acquire_timeout(timeout):
                raise Full
            try:
                if self._wsem:
                    timeout = max(0.0, deadline - _time())
                    if not self._wsem._block.acquire_timeout(timeout):
                        raise Full
                self._put(obj)
            finally:
                self._write_release()

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

    if sys.platform == 'win32':

        def __reduce__(self):
            return type(self), (self._maxsize, self._extra)

Queue = PipeQueue

#
# Queue based on a posix message queue
#

if hasattr(_processing, 'Queue'):

    class PosixQueue(_processing.Queue):

        _count = 0
        _count_lock = threading.RLock()
        _defaults = None

        def __init__(self, maxsize=0, msgsize=0, _name=None):
            assert maxsize >= 0 and msgsize >= 0

            PosixQueue._count_lock.acquire()
            try:
                PosixQueue._count += 1
                count = PosixQueue._count
            finally:
                PosixQueue._count_lock.release()

            if _name is None:
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

        # staticmethod
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
        getdefaults = staticmethod(getdefaults)

    Queue = PosixQueue
    __all__ += ['PosixQueue', 'BufferedPosixQueue']

#
# Buffered versions of queues
#

_sentinel = object()

class _BufferedQueue(object):

    def __init__(self, _queue, **kwds):
        self._queue = _queue
        self._notempty = threading.Condition(threading.Lock())
        self._buffer = collections.deque()
        self._thread = None
        
        for attr in ('get', 'empty', 'full', 'qsize',
                     'put_nowait', 'get_nowait'):
            method = getattr(self._queue, attr)
            setattr(self, attr, method)

    def put(self, obj):
        self._buffer.append(obj)
        self._notempty.acquire()
        try:
            if self._thread is None:
                self._startthread()
            self._notempty.notify()
        finally:
            self._notempty.release()

    def putmany(self, iterable):
        self._buffer.extend(iterable)
        self._notempty.acquire()
        try:
            if self._thread is None:
                self._startthread()
            self._notempty.notify()
        finally:
            self._notempty.release()

    def close(self):            # will be overwritten by _startthread()
        pass

    def _startthread(self):
        self._thread = threading.Thread(
            target=_BufferedQueue._feed,
            args=[self._buffer, self._notempty, self._queue.put]
            )
        
        self.close = process.Finalize(
            self, _BufferedQueue._finalize_queue,
            [self._buffer, self._notempty, self._thread],
            atexit=True
            )

        # We make the thread daemonic only to prevent the exit handler
        # of `threading` from trying to join it before the finalizer
        # `self.close()` gets a chance to stop and join it.
        self._thread.setDaemon(True)
        self._thread.start()
        
    # staticmethod 
    def _finalize_queue(buffer, notempty, thread):
        process.debug('closing thread used by buffered queue')
        notempty.acquire()
        try:
            buffer.append(_sentinel)
            notempty.notify()
        finally:
            notempty.release()
        thread.join()
        
    _finalize_queue = staticmethod(_finalize_queue)

    # staticmethod
    def _feed(buffer, notempty, put):
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
                        return
                    put(obj)
            except IndexError:
                pass

    _feed = staticmethod(_feed)


class BufferedPipeQueue(_BufferedQueue):
    def __init__(self, maxsize=0, _queue=None):
        self._queue = _queue or PipeQueue(maxsize)
        self._maxsize = maxsize
        _BufferedQueue.__init__(self, self._queue)
    def __reduce__(self):
        return (BufferedPipeQueue, (self._maxsize, self._queue))
    

if hasattr(_processing, 'Queue'):

    class BufferedPosixQueue(_BufferedQueue):
        def __init__(self, maxsize=0, msgsize=0):
            _BufferedQueue.__init__(self, PosixQueue(maxsize, msgsize))

