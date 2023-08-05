#
# Module implementing synchronization primitives
#
# processing/synchronize.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Condition',
            'Event']

import threading
import os
import sys
import itertools

from processing import process, _processing

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

    def __init__(self, kind, value):
        counter = _nextid()
        name = '/pys-%s-%s' % (os.getpid(), counter)
        self._block = _processing.Blocker(
            name=name, create=True, kind=kind, value=value
            )
        process.debug('creating blocker with name %r' % name)

        if sys.platform != 'win32':
            # On Unix we immediately unlink the name of the
            # semaphore since otherwise the semaphore might not
            # get removed (till the next reboot) if python gets
            # killed.  This means that `Blocker` objects are not
            # picklable on Unix, but that does not prevent a child
            # process from using a `Blocker` object inherited from
            # its parent.
            self._block._unlink()

        state = (kind, value, name)
        self.__setstate__(state)

    def __getstate__(self):
        if sys.platform != 'win32':
            raise NotImplemented
        return self._state
            
    def __setstate__(self, state):
        (kind, value, name) = self._state = state
        self._initvalue = value
        if not hasattr(self, '_block'):
            process.debug('opening blocker with name %r' % name)
            self._block = _processing.Blocker(
                name=name, create=False, kind=kind, value=value
                )

        if kind in (MUTEX, RECURSIVE_MUTEX) and sys.platform != 'win32':
            # On Unix a semaphore masquerading as a mutex will not be
            # automatically released when the process that owns it is
            # terminated by `os._exit()`.  To be safe we try to make sure
            # `self._block._close()` will be called before `os._exit()`.
            process.Finalize(
                self, self._block._close, atexit=True, priority=-10
                )

        self.acquire = self._block.acquire
        self.release = self._block.release

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, t, v, tb):
        self.release()

#
# Semaphore
#

class Semaphore(Blocker):

    def __init__(self, value=1):
        Blocker.__init__(self, SEMAPHORE, value)

    def getValue(self):
        return self._block._getvalue()

    def __repr__(self):
        try:
            return '<Semaphore(value=%r)>' % self._block._getvalue()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            return object.__repr__(self)

#
# Bounded semaphore
#

class BoundedSemaphore(Semaphore):

    def __init__(self, value=1):
        Blocker.__init__(self, BOUNDED_SEMAPHORE, value)

    def __repr__(self):
        try:
            return '<BoundedSemaphore(value=%r, maxvalue=%r)>' % \
                   (self._block._getvalue(), self._initvalue)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            return object.__repr__(self)

#
# Non-recursive lock -- releasing an unowned lock raises AssertionError
#

class Lock(Blocker):

    def __init__(self):
        Blocker.__init__(self, MUTEX, 1)

    def __repr__(self):
        try:
            return '<Lock(ismine=%r)>' % bool(self._block._ismine())
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            return object.__repr__(self)

#
# Recursive lock
#

class RLock(Blocker):

    def __init__(self, _name=None):
        Blocker.__init__(self, RECURSIVE_MUTEX, 1)

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

#
# Condition variable
#

class Condition(object):

    def __init__(self, lock=None):
        state = (lock or RLock(), Semaphore(0), Semaphore(0), Semaphore(0))
        self.__setstate__(state)

    def __setstate__(self, state):
        (self._lock, self._sleeping_count,
         self._woken_count, self._wait_semaphore) = self._state = state
        self.acquire = self._lock.acquire
        self.release = self._lock.release

    def __getstate__(self):
        return self._state

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
            # wait for notification or timeout
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

