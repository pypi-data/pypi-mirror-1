#
# Package analogous to 'threading.py' but using processes
#
# processing/__init__.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#
# This package is intended to duplicate the functionality (and much of
# the API) of threading.py but uses processes instead of threads.  A
# subpackage 'processing.dummy' has the same API but is a simple
# wrapper for 'threading'.
#
# Communication between processes is achieved using proxies which
# communicate with an manager using sockets (or name pipes).
#
# An example:
#
#   from processing import Process, Queue
#
#   def f(q):
#       for i in range(10):
#           q.put(i*i)
#       q.put('STOP')
#
#   if __name__ == '__main__':
#       queue = Queue()
#
#       p = Process(target=f, args=[queue])
#       p.start()
#
#       result = None
#       while result != 'STOP':
#           result = queue.get()
#           print result
#
#       p.join()
#

__all__ = [
    'Process', 'currentProcess', 'activeChildren', 'ProcessExit',
    'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore',
    'Condition', 'Event', 'Queue',
    'Manager', 'LocalManager', 'Pipe'
    ]

from processing.process import Process, currentProcess, \
     activeChildren, ProcessExit, Finalize


def Manager():
    from processing.managers import SyncManager
    m = SyncManager()
    m.start()
    return m

def LocalManager():
    from processing.localmanager import LocalManager
    return LocalManager()


def Pipe():
    from processing.connection import Pipe
    return Pipe()


def Lock():
    from processing.synchronize import Lock
    return Lock()

def RLock():
    from processing.synchronize import RLock
    return RLock()

def Condition(lock=None):
    from processing.synchronize import Condition
    return Condition(lock)

def Semaphore(value):
    from processing.synchronize import Semaphore
    return Semaphore(value)

def BoundedSemaphore(value):
    from processing.synchronize import BoundedSemaphore
    return BoundedSemaphore(value)

def Event():
    from processing.synchronize import Event
    return Event()


def PipeQueue(maxsize=0):
    from processing.synchronize import PipeQueue
    return PipeQueue(maxsize)

try:
    import processing._processing
except ImportError:
    Queue = PipeQueue
else:
    if hasattr(processing._processing, 'Queue'):   
        def PosixQueue(maxsize=0, msgsize=0):
            from processing.synchronize import PosixQueue
            return PosixQueue(maxsize, msgsize)
        Queue = PosixQueue
    else:
        Queue = PipeQueue




