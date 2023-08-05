#
# Analogue of `processing.manager`
#
# processing/dummy/managers.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'BaseManager', 'SyncManager', 'BaseProxy', 'CreatorMethod' ]

import threading, array

from threading import BoundedSemaphore, Condition, Event, RLock, Semaphore
from Queue import Queue

def Lock():
    return threading.Lock()

class Namespace(object):
    def __repr__(self):
        items = self.__dict__.items()
        temp = []
        for name, value in items:
            if not name.startswith('_'):
                temp.append('%s=%r' % (name, value))
        temp.sort()
        return 'Namespace(%s)' % str.join(', ', temp)
    
class SharedValue(object):
    def __init__(self, format, value):
        self._format = format
        self._value = value
    def get(self):
        return self._value
    def set(self, value):
        self._value = value
    def __repr__(self):
        return '<%r(%r, %r)>'%(type(self).__name__, self._format, self._value)
    value = property(get, set)

class SharedStruct(SharedValue):
    pass

class BaseManager(object):
    def __init__(self, *args, **kwds):
        pass
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

def CreatorMethod(callable, proxytype=None, exposed=None, typeid=None):
    def temp(self, *args, **kwds):
        return callable(*args, **kwds)
    temp.__name__ = callable.__name__
    return temp

class SyncManager(BaseManager):
    Event = CreatorMethod(Event)
    Queue = CreatorMethod(Queue)
    Lock = CreatorMethod(Lock)
    RLock = CreatorMethod(RLock)
    Semaphore = CreatorMethod(Semaphore)
    BoundedSemaphore = CreatorMethod(BoundedSemaphore)
    Condition = CreatorMethod(Condition)
    Namespace = CreatorMethod(Namespace)
    SharedValue = CreatorMethod(SharedValue)
    SharedStruct = CreatorMethod(SharedStruct)
    SharedArray = CreatorMethod(array.array)
    dict = CreatorMethod(dict)
    list = CreatorMethod(list)

class BaseProxy(object):
    pass

