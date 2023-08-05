#
# Module providing the `LocalManager` class for dealing
# with shared objects in shared memory
#
# processing/localmanager.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#

import mmap
import re
import os
import sys
import tempfile

from processing import synchronize, process, queue, heap, _processing
from struct import pack as _pack, unpack as _unpack, calcsize as _calcsize
from array import array

__all__ = [ 'LocalManager' ]

#
#
#

try:
    from struct import Struct
    from functools import partial
    _struct_cache = {}
except ImportError:
    Struct = None

#
# Class for a struct which lives in shared memory
#

class SharedStruct(object):
    
    def __init__(self, format, value, lock):
        wrapper = heap.BufferWrapper(_calcsize(format))
        self.__setstate__((wrapper, format, lock))
        self.set(value)

    def __getstate__(self):
        assert sys.platform == 'win32'
        return self._wrapper, self._format, self._lock
    
    def __setstate__(self, state):
        self._wrapper, self._format, self._lock = state
        self._buffer = self._wrapper.getview()
        self._acquire = self._lock.acquire
        self._release = self._lock.release
        if Struct:
            try:
                s = _struct_cache[self._format]
            except KeyError:
                s = Struct(self._format)
            self._get = partial(s.unpack_from, self._buffer)
            self._set = partial(s.pack_into, self._buffer, 0)
        
    def _get(self):
        return _unpack(self._format, self._buffer[:])
    
    def _set(self, *args):
        self._buffer[:] = _pack(self._format, *args)
        
    def get(self):
        self._acquire()
        try:
            return self._get()
        finally:
            self._release()

    def set(self, value):
        self._acquire()
        try:
            self._set(*value)
        finally:
            self._release()

    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self._format, self.get())

    value = property(get, set)

#
# Class for a length 1 struct which lives in shared memory
#

class SharedValue(SharedStruct):

    def get(self):
        self._acquire()
        try:
            return self._get()[0]
        finally:
            self._release()

    def set(self, value):
        self._acquire()
        try:
            self._set(value)
        finally:
            self._release()

    value = property(get, set)

#
# Class for a shared array which lives in shared memory
#

class SharedArray(object):
    
    def __init__(self, format, sequence, lock):
        wrapper = heap.BufferWrapper(_calcsize(format) * len(sequence))
        self.__setstate__((wrapper, format, lock))
        self[:] = sequence

    def __getstate__(self):
        assert sys.platform == 'win32'
        return self._wrapper, self._format, self._lock

    def __setstate__(self, state):
        self._wrapper, self._format, self._lock = state
        self._buffer = self._wrapper.getview()
        self._acquire = self._lock.acquire
        self._release = self._lock.release
        self._itemsize = _calcsize(self._format)
        self._length, rem = divmod(len(self._buffer), self._itemsize)
        assert rem == 0

    def __len__(self):
        return self._length

    def __getitem__(self, i):
        self._acquire()
        try:
            a = i * self._itemsize
            b = a + self._itemsize
            return _unpack(self._format, self._buffer[a:b])[0]
        finally:
            self._release()
            
    def __setitem__(self, i, value):
        self._acquire()
        try:
            a = i * self._itemsize
            b = a + self._itemsize
            self._buffer[a:b] = _pack(self._format, value)
        finally:
            self._release()

    def __getslice__(self, a, b):
        self._acquire()
        try:
            at = self._itemsize * a
            bt = self._itemsize * b
            return array(self._format, self._buffer[at:bt])
        finally:
            self._release()

    def __setslice__(self, a, b, seq):
        self._acquire()
        try:
            at = self._itemsize * a
            bt = self._itemsize * b
            self._buffer[at:bt] = array(self._format, seq).tostring()
        finally:
            self._release()

    def tostring(self):
        self._acquire()
        try:
            return self._buffer[:]
        finally:
            self._release()

    def tolist(self):
        self._acquire()
        try:
            arr = array(self._format, self._buffer[:])
        finally:
            self._release()
        return list(arr)

    def __repr__(self):
        if self._format == 'c':
            return '%s(%r, %r)' % \
                   (type(self).__name__, self._format, self.tostring())
        else:
            return '%s(%r, %r)' % \
                   (type(self).__name__, self._format, self.tolist())

#
# LocalManager
#

class LocalManager(object):
    
    def __init__(self):
        self._lock = synchronize.RLock()

    def start(self):
        pass

    def shutdown(self):
        pass

    def join(self):
        pass

    def _debug_info(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    Event = synchronize.Event
    Queue = queue.Queue
    Lock = synchronize.Lock
    RLock = synchronize.RLock
    Semaphore = synchronize.Semaphore
    BoundedSemaphore = synchronize.BoundedSemaphore
    Condition = synchronize.Condition
    
    def SharedValue(self, format, value):
        return SharedValue(format, value, self._lock)
    
    def SharedStruct(self, format, value):
        return SharedStruct(format, value, self._lock)
    
    def SharedArray(self, format, sequence):
        return SharedArray(format, sequence, self._lock)
    
#
# Test
#

def _test(x, y, z):
    x.value = 42
    y.value = (1729, 3.1415927)
    for i in range(len(z)):
        z[i] *= 2
    
def test():
    from processing import Process
    
    m = LocalManager()
    
    x = m.SharedValue('i', 0)
    y = m.SharedStruct('id', (0, 0))
    z = m.SharedArray('d', range(10))
    
    p = Process(target=_test, args=(x, y, z))
    p.start()
    p.join()
    
    print x
    print y
    print z
    
if __name__ == '__main__':
    test()
