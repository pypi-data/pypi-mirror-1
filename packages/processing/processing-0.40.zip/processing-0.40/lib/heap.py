#
# Module which supports allocation of memory from an mmap
#
# processing/heap.py
#
# Copyright (c) 2007, R Oudkerk --- see COPYING.txt
#

import bisect
import mmap
import tempfile
import os
import sys
import thread
import struct

from processing import _processing, currentProcess
from processing.finalize import Finalize

__all__ = ['BufferWrapper']

#
# Class representing an mmap - can be inherited by child processes
#

class MMapWrapper(object):

    __slots__ = ('__data', '__weakref__')
    
    mmap = property(lambda self: self.__data[0])
    size = property(lambda self: self.__data[1])
    name = property(lambda self: self.__data[2])
                
    def __init__(self, size):
        fd, name = tempfile.mkstemp(prefix='pym-')
        remaining = size
        while remaining > 0:
            remaining -= os.write(fd, '\0' * remaining)
        mmap_ = mmap.mmap(fd, size)
        os.close(fd)
        self.__data = (mmap_, size, name)

        if sys.platform in ('win32', 'cygwin'):
            Finalize(
                self, MMapWrapper._finalize_heap, args=[mmap_, name],
                exitpriority=-10
                )
        else:
            os.unlink(name)

    def __getstate__(self):
        assert sys.platform == 'win32'
        return (self.name, self.size)
    
    def __setstate__(self, state):
        assert getattr(currentProcess(), '_unpickling', False), \
               'mmaps should only be shared using process inheritance'
        name, size = state
        fd = os.open(name, os.O_RDWR | os.O_BINARY, int('0600', 8))
        mmap_ = mmap.mmap(fd, size)        
        os.close(fd)
        self.__data = (mmap_, size, name)
        
    @staticmethod
    def _finalize_heap(mmap, name):
        import os
        mmap.close()
        os.unlink(name)
        
#
# Class allowing allocation of (unmovable) chunks of memory from mmaps
#

class Heap(object):

    _alignment = struct.calcsize('P')
    
    def __init__(self, size=1024):
        self._lastpid = os.getpid()
        self._lock = thread.allocate_lock()
        self._size = size
        self._lengths = []
        self._len_to_seq = {}
        self._start_to_location = {}
        self._stop_to_location = {}
        self._allocated_locations = set()
        self._mmaps = []
        
    def _roundup(self, n):
        n = max(1, n)
        q, r = divmod(n, self._alignment)
        if r:
            q += 1
        return q * self._alignment
    
    def _malloc(self, size):
        # returns a large enough block -- it might be much larger
        i = bisect.bisect_left(self._lengths, size)
        if i == len(self._lengths):
            length = max(self._size, size)
            self._size *= 2
            mmap = MMapWrapper(length)
            self._mmaps.append(mmap)
            return (mmap, 0, length)
        else:
            length = self._lengths[i]
            seq = self._len_to_seq[length]
            location = seq.pop()
            if not seq:
                del self._len_to_seq[length], self._lengths[i]
        
        (mmap, start, stop) = location
        del self._start_to_location[(mmap, start)]
        del self._stop_to_location[(mmap, stop)]
        return location
    
    def _free(self, location):        
        # free location and try to merge with neighbours
        (mmap, start, stop) = location
        
        try:
            prev_location = self._stop_to_location[(mmap, start)]
        except KeyError:
            pass
        else:
            start, _ = self._absorb(prev_location)
            
        try:
            next_location = self._start_to_location[(mmap, stop)]
        except KeyError:
            pass
        else:
            _, stop = self._absorb(next_location)
            
        location = (mmap, start, stop)
        length = stop - start
        
        try:
            self._len_to_seq[length].append(location)
        except KeyError:
            self._len_to_seq[length] = [location]
            bisect.insort(self._lengths, length)
            
        self._start_to_location[(mmap, start)] = location
        self._stop_to_location[(mmap, stop)] = location

    def _absorb(self, location):
        # deregister this block so it can be merged with a neighbour
        (mmap, start, stop) = location
        del self._start_to_location[(mmap, start)]
        del self._stop_to_location[(mmap, stop)]
        
        length = stop - start
        seq = self._len_to_seq[length]
        seq.remove(location)
        if not seq:
            del self._len_to_seq[length]
            self._lengths.remove(length)

        return start, stop

    def free(self, location):
        # free a block returned by malloc()
        self._lock.acquire()
        try:
            self._allocated_locations.remove(location)
            self._free(location)
        finally:
            self._lock.release()
        
    def malloc(self, size):
        # return a block of right size (possibly rounded up)
        self._lock.acquire()
        try:
            if os.getpid() != self._lastpid:
                self.__init__()                     # reinitialize after fork
            size = self._roundup(size)
            (mmap, start, stop) = self._malloc(size)
            new_stop = start + size
            if new_stop < stop:
                self._free((mmap, new_stop, stop))
            location = (mmap, start, new_stop)
            self._allocated_locations.add(location)
            return location
        finally:
            self._lock.release()
    
    def _dump(self):
        self._verify(dump=True)

    def _verify(self, dump=False):
        all = []
        occupied = 0
        for L in self._len_to_seq.values():
            for mmap, start, stop in L:
                all.append((self._mmaps.index(mmap), start, stop,
                            stop-start, 'free'))
        for mmap, start, stop in self._allocated_locations:
            all.append((self._mmaps.index(mmap), start, stop,
                        stop-start, 'occupied'))
            occupied += (stop-start)

        all.sort()

        if dump:
            for line in all:
                print '%8s%8s%8s%8s  %s' % line
            lengths = [len(w.mmap) for w in self._mmaps]
            print 'mmap sizes =', lengths
            print 'total size =', sum(lengths)

        for i in range(len(all)-1):
            (mmap, start, stop) = all[i][:3]
            (nmmap, nstart, nstop) = all[i+1][:3]
            assert ((mmap != nmmap and nstart == 0) or (stop == nstart))

#
# Class representing a chunk of an mmap -- can be inherited
#

class BufferWrapper(object):

    __slots__ = ('__data', '__weakref__')
    _heap = Heap()

    location = property(lambda self : self.__data[0])
    size = property(lambda self : self.__data[1])

    def __init__(self, size):
        assert 0 <= size <= sys.maxint
        location = BufferWrapper._heap.malloc(size)
        self.__setstate__((location, size))
        Finalize(self, BufferWrapper._heap.free, args=[self.location])

    def getaddress(self):
        w, start, stop = self.location
        address, length = _processing.address_of_buffer(w.mmap)
        assert self.size <= length        
        return address + start
        
    def getview(self):
        w, start, stop = self.location
        return _processing.rwbuffer(w.mmap, start, self.size)
    
    def __getstate__(self):
        assert sys.platform == 'win32'
        return self.__data
    
    def __setstate__(self, state):
        self.__data = state
        
#
# Test
#

def test():
    import random

    iterations = 10000
    maxblocks = 50
    blocks = []

    maxsize = 0
    occ = 0
    maxocc = 0

    for i in xrange(iterations):
        size = int(random.lognormvariate(0, 1) * 1000)
        b = BufferWrapper(size)
        occ += size
        maxocc = max(maxocc, occ)
        maxsize = max(maxsize, size)
        blocks.append(b)

        if len(blocks) > maxblocks:
            i = random.randrange(maxblocks)
            del blocks[i]
            occ -= size

    BufferWrapper._heap._dump()
    print 'max size of a block =', maxsize
    print 'max size occupied =', maxocc
    print 'currently occupied =', occ

if __name__ == '__main__':
    test()
