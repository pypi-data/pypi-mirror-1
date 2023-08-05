#
# Module which supports allocation of ctypes objects from shared memory
#
# processing/sharedctypes.py
#
# Copyright (c) 2007, R Oudkerk --- see COPYING.txt
#

import weakref
import ctypes
import sys

from processing import heap, Lock

__all__ = ['new_value', 'new_array', 'copy']

#
#
#
    
def _new_value(type_):
    size = ctypes.sizeof(type_)
    wrapper = heap.BufferWrapper(size)
    return rebuild_ctype(type_, wrapper, None)

def new_value(fmt_or_type, *args):
    type_ = gettype(fmt_or_type)
    obj = _new_value(type_)
    ctypes.memset(ctypes.addressof(obj), 0, ctypes.sizeof(obj))
    obj.__init__(*args)
    return obj

def new_array(fmt_or_type, size_or_initializer):
    type_ = gettype(fmt_or_type)
    if isinstance(type_, str):
        type_ = _fmt_to_type[type_]
    if isinstance(size_or_initializer, int):
        type_ = type_ * size_or_initializer
        return new_value(type_)
    else:
        type_ = type_ * len(size_or_initializer)
        result = _new_value(type_)
        result.__init__(*size_or_initializer)
        return result

def copy(obj):
    new_obj = _new_value(type(obj))
    ctypes.pointer(new_obj)[0] = obj
    return new_obj
    
#
# Functions for pickling/unpickling
#

def reduce_ctype(obj):
    assert sys.platform == 'win32'
    if isinstance(obj, ctypes.Array):
        return rebuild_ctype, (obj._type_, obj._wrapper, obj._length_)
    else:
        return rebuild_ctype, (type(obj), obj._wrapper, None)
    
def rebuild_ctype(type_, wrapper, length):
    if length is not None:
        type_ = type_ * length
    fixup(type_)
    obj = type_.from_address(wrapper.getaddress())
    obj._wrapper = wrapper
    return obj

def fixup(type_):
    if (sys.platform == 'win32' and type_.__reduce__ is not reduce_ctype):
        type_.__reduce__ = reduce_ctype
    
#
# Function which converts format strings to ctype types
#

def gettype(fmt_or_type, mapping={}):
    if not mapping:
        for name in dir(ctypes):
            if name[:2] == 'c_':
                T = getattr(ctypes, name)
                if hasattr(T, '_type_'):
                    mapping[T._type_] = T
        mapping.update(i=ctypes.c_int, I=ctypes.c_uint,
                       l=ctypes.c_long, L=ctypes.c_ulong)
    return mapping.get(fmt_or_type, fmt_or_type)

#
# Tests
#

class _Foo(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_int),
        ('y', ctypes.c_double)
        ]

def _test(x, y, foo, arr, string):
    x.value **= 2
    y.value **= 2
    foo.x **= 2
    foo.y **= 2
    for i in range(len(arr)):
        arr[i] **= 2
    string.value = string.value.upper()
    
def test():
    from processing import Process
    
    x = new_value('i', 7)
    y = new_value(ctypes.c_double, 1.0/3.0)
    foo = new_value(_Foo, 3, 2)
    arr = new_array('d', range(10))
    string = new_array('c', 'hello world')

    bar = copy(foo)
    assert (foo.x, foo.y) == (bar.x, bar.y)

    p = Process(target=_test, args=(x, y, foo, arr, string))
    p.start()
    p.join()

    print x.value
    print y.value
    print (foo.x, foo.y)
    print arr[:]
    print string.value

if __name__ == '__main__':
    test()
