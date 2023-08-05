#
# Module providing the `Pool` class for managing a process pool
#
# processing/pool.py
#
# Copyright (c) 2007, R Oudkerk --- see COPYING.txt
#

__all__ = ['Pool']

#
# Imports
#

import processing
import threading
import Queue
import itertools
import collections

#
# Miscellaneous
#

newjobid = itertools.count().next

def mapstar(args):
    return map(*args)

def applystar(args):
    return apply(*args)

#
# Code run by worker processes
#

def worker(inqueue, outqueue):
    while 1:
        job, i, func, args, kwds = inqueue.get()
        if job is None:
            return
        try:
            result = (True, func(*args, **kwds))
        except Exception, e:
            result = (False, e)
        outqueue.put((job, i, result))

#
# Class representing a process pool
#
        
class Pool(object):
    '''
    Class which supports an async version of the `apply()` builtin
    '''
    def __init__(self, processes=None):
        self._inqueue = processing.PipeQueue()
        self._outqueue = processing.PipeQueue()
        self._taskqueue = Queue.Queue()
        self._cache = {}
        
        if processes is None:
            try:
                processes = processing.cpuCount()
            except NotImplementedError:
                processes = 1
            
        self._pool = [
            processing.Process(target=worker,
                               args=[self._inqueue, self._outqueue])
            for i in range(processes)
            ]
        
        for w in self._pool:
            w.setDaemon(True)
            w.start()
            
        self._result_handler = threading.Thread(target=self._handle_results)
        self._result_handler.setDaemon(True)
        self._result_handler.start()

        self._task_handler = threading.Thread(target=self._handle_tasks)
        self._task_handler.setDaemon(True)
        self._task_handler.start()

        self.shutdown = processing.Finalize(
            self, Pool._finalize,
            args=(self._taskqueue, self._outqueue), atexit=True
            )
        
    def apply(self, func, args=(), kwds={}):
        '''
        Equivalent of `apply()` builtin
        '''
        return self.apply_async(func, args, kwds).get()

    def map(self, func, seq, chunksize=None):
        '''
        Equivalent of `map()` builtin
        '''
        return self.map_async(func, seq, chunksize).get()

    def imap(self, func, seq):
        '''
        Equivalent of `itertool.imap()` -- can be MUCH slower than `Pool.map()`
        '''
        result = IMapIterator(self._cache)
        job = result._job
        self._taskqueue.put((((job, i, func, (x,), {})
                              for i, x in enumerate(seq)), result._setlength))
        return result

    def imap_unordered(self, func, seq):
        '''
        Like `imap()` method but ordering of results is arbitrary
        '''
        result = IMapUnorderedIterator(self._cache)
        job = result._job
        self._taskqueue.put((((job, i, func, (x,), {})
                              for i, x in enumerate(seq)), result._setlength))
        return result

    def apply_async(self, func, args=(), kwds={}):
        '''
        Asynchronous equivalent of `apply()` builtin
        '''
        result = ApplyResult(self._cache)
        job = result._job
        self._taskqueue.put(([(job, None, func, args, kwds)], None))
        return result
    
    def map_async(self, func, seq, chunksize=None):
        '''
        Asynchronous equivalent of `map()` builtin
        '''
        if not hasattr(seq, '__len__'):
            seq = list(seq)
        
        if chunksize is None:
            chunksize, extra = divmod(len(seq), len(self._pool) * 4)
            if extra:
                chunksize += 1
                
        task_batches = Pool._gettasks(func, seq, chunksize)
        result = MapResult(self._cache, chunksize, len(seq))
        job = result._job
        self._taskqueue.put((((job, i, mapstar, (x,), {})
                              for i, x in enumerate(task_batches)), None))
        return result
    
    def _handle_tasks(self):
        put = self._inqueue._put
        for taskseq, setlength in iter(self._taskqueue.get, None):
            for i, task in enumerate(taskseq):
                put(task)
            if setlength:
                setlength(i+1)
        for p in self._pool:
            put((None, None, None, None, None))

    def _handle_results(self):
        cache = self._cache        
        for job, i, obj in iter(self._outqueue._get, None):
            try:
                cache[job]._set(i, obj)
            except KeyError:
                pass

    def join(self):
        self.shutdown()
        for p in self._pool:
            p.join()
            
    # staticmethod
    def _finalize(taskqueue, outqueue):
        taskqueue.not_empty.acquire()
        try:
            taskqueue.queue.clear()
        finally:
            taskqueue.not_empty.release()
        taskqueue.put(None)
        outqueue.put(None)
    _finalize = staticmethod(_finalize)

    # staticmethod
    def _gettasks(func, it, size):
        it = iter(it)
        while 1:
            x = tuple(itertools.islice(it, size))
            if not x:
                return
            yield (func, x)
    _gettasks = staticmethod(_gettasks)
            
#
# Class whose instances are returned by `Pool.apply_async()`
#

class ApplyResult(object):

    def __init__(self, cache):
        self._cond = threading.Condition(threading.Lock())
        self._job = newjobid()
        self._cache = cache
        self._ready = False
        cache[self._job] = self
        
    def ready(self):
        return self._ready
    
    def successful(self):
        assert self._ready
        return self._success
    
    def wait(self, timeout=None):
        self._cond.acquire()
        try:
            if not self._ready:
                self._cond.wait(timeout)
        finally:
            self._cond.release()

    def get(self, timeout=None):
        self.wait(timeout)
        if not self._ready:
            raise processing.TimeoutError
        if self._success:
            return self._value
        else:
            raise self._value

    def _set(self, i, obj):
        self._success, self._value = obj
        self._cond.acquire()
        try:
            self._ready = True
            self._cond.notify()
        finally:
            self._cond.release()
        del self._cache[self._job]

#
# Class whose instances are returned by `Pool.map_async()`
#

class MapResult(ApplyResult):
    
    def __init__(self, cache, chunksize, length):
        ApplyResult.__init__(self, cache)
        self._success = True
        self._value = [None]*length
        self._chunksize = chunksize
        self._number_left = length//chunksize + bool(length % chunksize)
        
    def _set(self, i, (success, result)):
        if success:
            self._value[i*self._chunksize:(i+1)*self._chunksize] = result
            self._number_left -= 1
            if self._number_left == 0:
                self._cond.acquire()
                try:
                    self._ready = True
                    self._cond.notify()
                finally:
                    self._cond.release()
                del self._cache[self._job]

        else:
            self._success = False
            self._value = result
            self._cond.acquire()
            try:
                self._ready = True
                self._cond.notify()
            finally:
                self._cond.release()
            del self._cache[self._job]

#
# Class whose instances are returned by `Pool.imap()`
#

class IMapIterator(object):

    def __init__(self, cache):
        self._cond = threading.Condition(threading.Lock())
        self._job = newjobid()
        self._cache = cache
        self._items = collections.deque()
        self._index = 0
        self._length = None
        self._unsorted = {}
        cache[self._job] = self
        
    def __iter__(self):
        return self
    
    def next(self, timeout=None):
        self._cond.acquire()
        try:
            try:
                success, value = self._items.popleft()
            except IndexError:
                if self._index == self._length:
                    raise StopIteration
                self._cond.wait(timeout)
                try:
                    success, value = self._items.popleft()
                except IndexError:
                    raise processing.TimeoutError
        finally:
            self._cond.release()

        if success:
            return value
        raise value
    
    def _set(self, i, obj):
        self._cond.acquire()
        try:
            if self._index == i:
                self._items.append(obj)
                self._index += 1
                while self._index in self._unsorted:
                    obj = self._unsorted.pop(self._index)
                    self._items.append(obj)
                    self._index += 1
                self._cond.notify()
            else:
                self._unsorted[i] = obj
                
            if self._index == self._length:
                del self._cache[self._job]
        finally:
            self._cond.release()
            
    def _setlength(self, length):
        self._cond.acquire()
        try:
            self._length = length
            if self._index == self._length:
                self._cond.notify()
                del self._cache[self._job]
        finally:
            self._cond.release()

#
# Class whose instances are returned by `Pool.imap_unordered()`
#

class IMapUnorderedIterator(IMapIterator):

    def _set(self, i, obj):
        self._cond.acquire()
        try:
            self._items.append(obj)
            self._index += 1
            self._cond.notify()
            if self._index == self._length:
                del self._cache[self._job]
        finally:
            self._cond.release()
