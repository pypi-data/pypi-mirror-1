#
# Support for the API of the processing package using threads instead
#
# processing/dummy.py
#
# Copyright (c) 2006, Richard Oudkerk
#

__all__ = [ 'Process', 'Manager', 'currentProcess', 'Repr',
            'Listener', 'Client' ]

import sys
import threading

from threading import BoundedSemaphore, Condition, Event, RLock, Semaphore
from Queue import Queue

currentProcess = threading.currentThread
Repr = repr
Process = threading.Thread
Process.exit = staticmethod(sys.exit)

def Lock():
    return threading.Lock()

class Namespace(object):
    def __repr__(self):
        temp = self.__dict__.items()
        temp = ['%s=%r' % i for i in temp if not i[0].startswith('_')]
        temp.sort()
        return '<Namespace(%s)>' % str.join(', ', temp)


class BaseManager(object):
    def __init__(self, *args):
        pass
    def shutdown(self):
        pass
    def join(self):
        pass
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def register(cls, name, type, proxytype=None, exposed=None):
        setattr(cls, name, staticmethod(type))
    register = classmethod(register)

class Manager(BaseManager):
    pass

manager = type(threading)('manager')
manager.BaseManager = manager.ProcessBaseManager = BaseManager
manager.DefaultManager = Manager

for callable in (
    BoundedSemaphore, Condition, Event, Lock,
    RLock, Semaphore, Namespace, Queue, dict, list, set
    ):
    Manager.register(callable.__name__, callable)

del callable, BaseManager


class Listener(object):
    def __init__(self, family=None, backlog=1):
        self._queue = Queue(backlog)
    def accept(self):
        return Client(address=None, use=self._queue.get())
    address = property(lambda self: self)

class Client(object):
    def __init__(self, address, use=None):
        if address is None:
            self._rqueue, self._squeue = use
        else:
            self._rqueue = Queue()
            self._squeue = Queue()
            address._queue.put((self._squeue, self._rqueue))
        self.send = self.send_string = self._squeue.put
        self.recv = self.recv_string = self._rqueue.get


if __name__ == "__main__":

    s = Manager()

    d = s.dict()

    d[5] = 6
    print d

    n = s.Namespace()

    n.dog = 29
    n.cat = 6
    n.dog += 7
    
    print Repr(n)
    
    s.shutdown()
