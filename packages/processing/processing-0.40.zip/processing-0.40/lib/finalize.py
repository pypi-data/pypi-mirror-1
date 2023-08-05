#
# Module supporting finaliztion using weakrefs
#
# processing/finalize.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#

import weakref
import itertools


__all__ = ['Finalize', '_run_finalizers']


class Finalize(object):
    '''
    Class which supports object finalization using weakrefs
    '''
    _registry = {}
    _counter = itertools.count()
    
    def __init__(self, obj, callback, args=(), kwargs=None, exitpriority=None):
        assert exitpriority is None or type(exitpriority) is int
        
        if obj is not None:
            self._weakref = weakref.ref(obj, self)
        else:
            assert exitpriority is not None

        self._callback = callback
        self._args = args
        self._kwargs = kwargs or {}
        self._key = (exitpriority, self._counter.next())
        
        self._registry[self._key] = self
        
    def __call__(self, wr=None):
        '''
        Run the callback unless it has already been called or cancelled

        Returns True if callback was run otherwise returns False
        '''
        try:
            del self._registry[self._key]
        except KeyError:
            return False
        else:
            self._callback(*self._args, **self._kwargs)
            self._weakref = self._callback = self._args = self._kwargs = None
            return True

    def cancel(self):
        '''
        Cancel finalization of the object
        '''
        try:
            del self._registry[self._key]
        except KeyError:
            pass

    def still_active(self):
        '''
        Return whether this finalizer is still waiting to invoke callback
        '''
        return self._key in self._registry


def _run_finalizers(minpriority=None):
    '''
    Run all finalizers whose exit priority is not None and at least minpriority
    
    Finalizers with highest priority are called first; finalizers with
    the same priority will be called in reverse order of creation.
    '''
    if minpriority is None:
        f = lambda p : p[0][0] is not None
    else:
        f = lambda p : p[0][0] is not None and p[0] >= minpriority
    items = filter(f, Finalize._registry.iteritems())
    items.sort(reverse=True)

    for key, finalizer in items:
        try:
            finalizer()
        except Exception:
            import traceback
            traceback.print_exc()
            
    Finalize._registry.clear()


if __name__ == '__main__':
    result = []

    class Foo(object):
        pass
    
    a = Foo()
    Finalize(a, result.append, args=('a',))
    del a               # triggers callback for a
    
    b = Foo()
    close_b = Finalize(b, result.append, args=('b',))    
    close_b()           # triggers callback for b
    close_b()           # does nothing because callback has already been called
    del b               # does nothing because callback has already been called

    c = Foo()
    Finalize(c, result.append, args=('c',))
    
    d10 = Foo()
    Finalize(d10, result.append, args=('d10',), exitpriority=1)
    
    d01 = Foo()
    Finalize(d01, result.append, args=('d01',), exitpriority=0)
    d02 = Foo()
    Finalize(d02, result.append, args=('d02',), exitpriority=0)
    d03 = Foo()
    Finalize(d03, result.append, args=('d03',), exitpriority=0)
    
    _run_finalizers()   # triggers callbacks for d10, d03, d02, d01 in that
                        # order; the callback for c will not be called
                        
    expected = ['a', 'b', 'd10', 'd03', 'd02', 'd01']
    assert result == expected, '%s != %s' % (result, expected)
    print 'got expected result: %s' % result
    
