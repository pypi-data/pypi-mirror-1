import mmap
import re
import os
import sys
import tempfile
import array
import process

from processing import synchronize
from struct import pack as _pack, unpack as _unpack, calcsize as _calcsize

__all__ = [ 'LocalManager' ]


#
# Heap implementation
#

class Heap(object):
    '''
    Class for allocating and freeing memory from an mmap
    '''
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
            self._set_pos(8)
            
            if sys.platform in ('win32', 'cygwin'):
                def close_mmap(mmap, name):
                    import os
                    mmap.close()
                    os.unlink(name)
                process.Finalize(
                    self, close_mmap, args=[self._mmap, self._name],
                    atexit=True
                    )
            else:
                os.unlink(self._name)
                
    def malloc(self, bytes):
        '''
        Allocate chunk of memory of given size
        '''
        bytes += 4                              # extra room for header info
        bytes = ((bytes + 3) // 4) * 4          # round up to multiple of 4

        self._lock.acquire()
        try:
            offset = self._malloc(bytes)
            return offset + 4
        finally:
            self._lock.release()

    def free(self, offset):
        '''
        Free a chunk of memory previously allocated by malloc
        '''
        self._lock.acquire()
        try:
            self._free(offset - 4)
        finally:
            self._lock.release()
    
    def _malloc(self, bytes):
        '''
        Allocate chunk of memory -- `bytes` must be multiple of 4.
        First 4 bytes are occupied by header info so bytes must be at least 4
        '''
        self._lock.acquire()
        try:
            # resize mmap if the file has been enlarged by other process
            if self._size < self._mmap.size():
                self._mmap.resize(self._mmap.size())
                self._size = len(self._mmap)
                
            start = stop = None
            
            # iterate over empty chunks
            for start, stop in self._get_empty_chunks():
                # if chunk is large enough
                if stop - start >= bytes:
                    # write header for the chunk we are creating
                    self._set_chunk_info(start, start + bytes, True)
                    
                    # write header for following empty chunk if necessary
                    if start + bytes < stop:
                        self._set_chunk_info(start + bytes, stop, False)
                        
                    # update position of last empty chunk
                    if start == self._get_pos():
                        try:
                            pos, _ = self._get_empty_chunks().next()
                        except StopIteration:
                            pos = self._size
                        self._set_pos(pos)
                        
                    return start
                
            # get position of memory just after last occupied chunk
            if stop == self._size:
                pos = start
            else:
                pos = self._size
                
            # work out how much space we need and resize mmap
            while pos + bytes > self._size:
                self._size *= 2
            if self._size > len(self._mmap):
                self._mmap.resize(self._size)
                
            # mark chunk as occupied and update position of last empty chunk
            self._set_chunk_info(pos, pos + bytes, True)
            if pos == self._get_pos():
                self._set_pos(pos + bytes)
            
            return pos
        finally:
            self._lock.release()

    def _free(self, start):
        '''
        Free chunk of memory -- must have been allocated by _malloc
        '''
        stop, occ = self._get_chunk_info(start)
        assert occ
        # mark chunk as not occupied
        self._mmap[start:stop] = '\0' * (stop - start)
        self._set_chunk_info(start, stop, False)

        # if this chunk is before previous first empty chunk
        if self._get_pos() > start:
            # record start as position of first empty chunk
            self._set_pos(start)
            
    def _get_chunks(self, start=8):
        '''
        Iterator over chunks of memory.
        Returns (start, stop, occupied) tuples.
        '''
        while start < self._size:
            stop, occ = self._get_chunk_info(start)
            yield start, stop, occ
            start = stop

    def _get_empty_chunks(self):
        '''
        Iterator over empty chunks of memory.
        When possible adjacent empty chunks are merged.
        Returns (start, stop) pairs.
        '''
        pos = self._get_pos()
        it = self._get_chunks(pos)
        
        for start, stop, occ in it:
            if not occ:
                merge = False
                
                for nstart, nstop, occ in it:
                    if occ:
                        break
                    stop = nstart = nstop
                    merge = True
                    
                if merge:
                    self._mmap[start:stop] = '\0' * (stop - start)
                    self._set_chunk_info(start, stop, False)
                    
                yield start, stop

    def _get_pos(self):
        '''
        Return offset of first empty chunk of memory (or self._size if none)
        '''
        return _unpack('i', self._mmap[0:4])[0]

    def _set_pos(self, pos):
        '''
        Set offset of first empty chunk of memory
        '''
        self._mmap[0:4] = _pack('i', pos)

    def _get_chunk_info(self, start):
        '''
        Get info at beginning of a chunk of memory starting at start
        Returns (stop, isoccupied) pair
        '''
        info = _unpack('i', self._mmap[start:start+4])[0]
        stop = abs(info)
        isoccupied = info > 0
        
        if stop == 0:
            assert not isoccupied
            return self._size, False
        return stop, isoccupied

    def _set_chunk_info(self, start, stop, occ):
        '''
        Set info at begining of a chunk of memory
        '''
        assert stop > 0
        if not occ:
            stop = -stop
        self._mmap[start:start+4] = _pack('i', stop)
        
    def _dump(self):
        '''
        Print hex dump of mmap
        '''
        assert len(self._mmap) % 4 == 0
        for i in range(len(self._mmap) // 4):
            if i % 8 == 0:
                print
            print '%08x' % _unpack('I', self._mmap[4*i:4*i+4]),
        print

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
            process.Finalize(
                self, self._heap.free, args=[self._start], atexit=True
                )
            
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
            self._length = _length

        self._stop = self._start + self._itemsize * self._length
        self._lock = _lock or self._heap._lock

        self._acquire = self._lock.acquire
        self._release = self._lock.release
        self._mmap = self._heap._mmap

        if _start is None:
            self[:] = sequence
            process.Finalize(
                self, self._heap.free, args=[self._start], atexit=True
                )

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

    def tostring(self):
        self._acquire()
        try:
            return self._mmap[self._start:self._stop]
        finally:
            self._release()

    def tolist(self):
        self._acquire()
        try:
            s = self._mmap[self._start:self._stop]
            arr = array.array(self._format, s)
            return list(arr)
        finally:
            self._release()

    def __repr__(self):
        if self._format == 'c':
            return '%s(%r, %r)' % \
                   (type(self).__name__, self._format, self.tostring())
        else:
            return '%s(%r, %r)' % \
                   (type(self).__name__, self._format, self.tolist())

    if sys.platform == 'win32':

        def __reduce__(self):
            return type(self), (self._heap, self._format, None,
                                self._lock, self._start, self._length)

#
# LocalManager
#

class LocalManager(object):
    
    def __init__(self, size=256):
        self._lock = synchronize.RLock()
        self._size = size

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
                self._heap = Heap(size=self._size, _lock=self._lock)
            return self._heap
        finally:
            self._lock.release()
            
    def SharedValue(self, format, value):
        return SharedValue(self._getheap(), format, value)
    
    def SharedStruct(self, format, value):
        return SharedStruct(self._getheap(), format, value)
    
    def SharedArray(self, format, sequence):
        return SharedArray(self._getheap(), format, sequence)
    
#
# Test
#

def test0():
    m = LocalManager()

    a = []
    for i in range(10):
        a.append(m.SharedValue('i', i))

    print list(m._heap._get_empty_chunks())
    del a[3:8]
    print list(m._heap._get_empty_chunks())

    for i in range(100):
        a.append(m.SharedValue('i', 0x100 + i))

    print list(m._heap._get_empty_chunks())

    m._heap._dump()


def test():
    '''
    Randomly create and delete shared arrays of chars
    
    Check no corruption caused
    '''
    import random
    
    manager = LocalManager()
    
    L = []
    maxcount = 10
    
    for k in range(1000):
        i = random.randrange(100)
        arr = ''.join([chr(j) for j in range(i)])
        sarr = manager.SharedArray('c', arr)
        L.append((arr, sarr))
        
        if len(L) > maxcount:
            j = random.randrange(maxcount)
            del L[j]
            
    print 'Heap size =', manager._heap._size
    print 'Empty chunks =', list(manager._getheap()._get_empty_chunks())
    
    for arr, sarr in L:
        assert arr == ''.join(sarr)
        
    print 'Tests passed'
    
    
if __name__ == '__main__':
    test()
