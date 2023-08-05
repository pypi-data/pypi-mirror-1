import mmap
import re
import os
import sys
import tempfile
import processing
import array
import synchronize

from struct import pack as _pack, unpack as _unpack, calcsize as _calcsize

__all__ = [ 'LocalManager' ]

#
# Class for allocating and freeing memory from an mmap
#
# XXX Currently freed memory does not get recycled
#

class Heap(object):
    
    def __init__(self, size=256, _name=None, _lock=None):
        assert size >= 256
        if _name is None:
            fd, self._name = tempfile.mkstemp(prefix='pym-')
            remaining = size
            while remaining > 0:
                remaining -= os.write(fd, '\0' * remaining)
            self._lock = _lock or RLock()
            
        else:
            assert _lock is not None
            self._lock = _lock
            self._name = _name
            fd = os.open(_name, os.O_RDWR, 0600)
            
        self._size = size
        self._mmap = mmap.mmap(fd, self._size)        
        os.close(fd)
        
        if _name is None:            
            self.__setpos(4)
            
            if sys.platform in ('win32', 'cygwin'):
                def f(mmap, name):
                    import os
                    mmap.close()
                    os.unlink(name)
                processing.Finalize(self, f, args=[self._mmap, self._name])
            else:
                os.unlink(self._name)
                
    def malloc(self, bytes):
        self._lock.acquire()
        try:
            if self._size < self._mmap.size():
                self._mmap.resize(self._mmap.size())
                self._size = len(self._mmap)
                
            pos = self.__getpos()
            while pos + bytes > self._size:
                self._size *= 2
                
            if self._size > len(self._mmap):
                self._mmap.resize(self._size)
                
            self.__setpos(pos + bytes)
            return pos
        finally:
            self._lock.release()
            
    def free(self, offset):
        pass
    
    def __getpos(self):
        return _unpack('I', self._mmap[0:4])[0]
    
    def __setpos(self, value):
        self._mmap[0:4] = _pack('I', value)
        
    if sys.platform == 'win32':
        
        def __reduce__(self):
            return type(self), (self._size, self._name, self._lock)
        
#
# Class for a struct which lives in shared memory
#

class SharedStruct(object):
    
    def __init__(self, heap, format, value, _lock=None, _start=None):
        self._heap = heap
        self._format = format
        size = _calcsize(format)
        if _start is None:
            self._start = heap.malloc(size)
            assert format is not None
        else:
            self._start = _start
        self._stop = self._start + size
        
        self._lock = _lock or self._heap._lock
        
        self._acquire = self._lock.acquire
        self._release = self._lock.release
        self._mmap = self._heap._mmap
        
        if _start is None:
            self.set(value)
                
    def get(self):
        self._acquire()
        try:
            return _unpack(self._format, self._mmap[self._start:self._stop])
        finally:
            self._release()
            
    def set(self, value):
        self._acquire()
        try:
            self._mmap[self._start:self._stop] = _pack(self._format, *value)
        finally:
            self._release()

    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self._format, self.get())
    
    value = property(get, set)

    if sys.platform == 'win32':

        def __reduce__(self):
            return type(self), (self._heap, self._format, None,
                                self._lock, self._start)
    
#
# Class for a length 1 struct which lives in shared memory
#

class SharedValue(SharedStruct):
    
    def __init__(self, heap, format, value, _lock=None, _start=None):
        assert re.match('(\d+[sp]|[@=<>!]?[cbBhHiIlLqQfdP])$', format), \
               'format must have length 1'
        SharedStruct.__init__(self, heap, format, value, _lock, _start)
        
    def get(self):
        self._acquire()
        try:
            return _unpack(self._format, self._mmap[self._start:self._stop])[0]
        finally:
            self._release()
            
    def set(self, value):
        self._acquire()
        try:
            self._mmap[self._start:self._stop] = _pack(self._format, value)
        finally:
            self._release()
            
    value = property(get, set)

#
# Class for a shared array which lives in shared memory
#

class SharedArray(object):
    
    def __init__(self, heap, format, sequence,
                 _lock=None, _start=None, _length=None):
        self._heap = heap
        self._format = format
        self._itemsize = _calcsize(format)

        if _start is None:
            sequence = tuple(sequence)
            self._length = len(sequence)
            self._start = heap.malloc(self._itemsize * self._length)
        else:
            self._start = _start
            self._length = length
            
        self._stop = self._start + self._itemsize * self._length
        self._lock = _lock or self._heap._lock
            
        self._acquire = self._lock.acquire
        self._release = self._lock.release
        self._mmap = self._heap._mmap
        
        if _start is None:
            self[:] = sequence
                
    def __len__(self):
        return self._length

    def __iter__(self):
        return iter(array.array(self._format,
                                self._mmap[self._start:self._stop]))

    def __getitem__(self, i):
        self._acquire()
        try:
            t = self._start + self._itemsize * i
            assert self._start <= t < self._stop
            return _unpack(self._format, self._mmap[t:t+self._itemsize])[0]
        finally:
            self._release()
            
    def __setitem__(self, i, value):
        self._acquire()
        try:
            t = self._start + self._itemsize * i
            assert self._start <= t < self._stop
            self._mmap[t:t+self._itemsize] = _pack(self._format, value)
        finally:
            self._release()
            
    def __getslice__(self, a, b):
        self._acquire()
        try:
            at = self._start + self._itemsize * a
            bt = self._start + self._itemsize * b
            bt = min(bt, self._stop)
            return array.array(self._format, self._mmap[at:bt])
        finally:
            self._release()        

    def __setslice__(self, a, b, seq):
        self._acquire()
        try:
            at = self._start + self._itemsize * a
            bt = self._start + self._itemsize * b
            bt = min(bt, self._stop)
            self._mmap[at:bt] = array.array(self._format, seq).tostring()
        finally:
            self._release()

    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self._format, list(self))

    if sys.platform == 'win32':

        def __reduce__(self):
            return type(self), (self._heap, self._format, None,
                                self._lock, self._start)

#
# LocalManager
#

class LocalManager(object):
    
    def __init__(self, *args, **kwds):
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
    Queue = synchronize.Queue
    Lock = synchronize.Lock
    RLock = synchronize.RLock
    Semaphore = synchronize.Semaphore
    BoundedSemaphore = synchronize.BoundedSemaphore
    Condition = synchronize.Condition

    def _getheap(self):
        self._lock.acquire()
        try:
            if not hasattr(self, '_heap'):
                self._heap = Heap(_lock=self._lock)
            return self._heap
        finally:
            self._lock.release()
            
    def SharedValue(self, format, value):
        return SharedValue(self._getheap(), format, value)

    def SharedStruct(self, format, value):
        return SharedStruct(self._getheap(), format, value)

    def SharedArray(self, format, sequence):
        return SharedArray(self._getheap(), format, sequence)

