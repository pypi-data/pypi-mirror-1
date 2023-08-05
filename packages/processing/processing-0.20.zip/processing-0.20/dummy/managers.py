#
# Analogue of `processing.manager`
#
# processing/dummy/managers.py
#
# Copyright (c) 2006, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'BaseManager', 'SyncManager', 'BaseProxy', 'CreatorMethod' ]

import threading

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

class BaseManager(object):
    def __init__(self, *args, **kwds):
        pass
    def shutdown(self):
        pass
    def join(self):
        pass
    def _info(self):
        return {}
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass

def CreatorMethod(callable, proxytype=None, exposed=None):
    def temp(self, *args, **kwds):
        return callable(*args, **kwds)
    temp.__name = callable.__name__
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
    dict = CreatorMethod(dict)
    list = CreatorMethod(list)

class BaseProxy(object):
    pass

