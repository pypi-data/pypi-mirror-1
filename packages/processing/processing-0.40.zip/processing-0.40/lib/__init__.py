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

__version__ = '0.40'

__all__ = [
    'Process', 'currentProcess', 'activeChildren', 'freezeSupport',
    'ProcessExit', 'Manager', 'Pipe', 'cpuCount', 
    'getLogger', 'enableLogging', 'BufferTooShort'
    ]

#
# Imports
#

import os
import sys
import _processing              # from . import _processing

from process import Process, currentProcess, activeChildren
from process import freezeSupport, ProcessExit

HAVE_NATIVE_SEMAPHORE = hasattr(_processing, 'Blocker')

#
# Definitions not depending on native semaphores or queues
#

BufferTooShort = _processing.BufferTooShort

def Manager():
    '''
    Returns a manager associated with a running server process

    The managers methods such as `Lock()`, `Condition()` and `Queue()`
    can be used to create shared objects.
    '''
    from processing.managers import SyncManager
    m = SyncManager()
    m.start()
    return m

def Pipe(duplex=True):
    '''
    Returns two connection object connected by a pipe
    '''
    from processing.connection import Pipe
    return Pipe(duplex)

def cpuCount():
    '''
    Returns the number of CPUs in the system
    '''
    if sys.platform == 'win32':
        try:
            num = int(os.environ['NUMBER_OF_PROCESSORS'])
        except (ValueError, KeyError):
            num = 0
    elif sys.platform == 'darwin':
        try:
            num = int(os.popen('sysctl -n hw.ncpu').read())
        except ValueError:
            num = 0
    else:
        try:
            num = os.sysconf('SC_NPROCESSORS_ONLN')
        except (ValueError, OSError, AttributeError):
            num = 0
        
    if num >= 1:
        return num
    else:
        raise NotImplementedError

def getLogger():
    '''
    Returns logger used by processing
    '''
    from processing.logger import getLogger
    return getLogger()

def enableLogging(level=10, HandlerType=None, handlerArgs=(), format=None):
    '''
    Enable logging using `level` as the debug level
    '''
    from processing.logger import enableLogging
    return enableLogging(level, HandlerType, handlerArgs, format)


if HAVE_NATIVE_SEMAPHORE:
    
    __all__ += [
        'LocalManager', 'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore',
        'Condition', 'Event', 'Queue', 'Pool', 'TimeoutError'
        ]
    
    def LocalManager():
        '''
        Returns a manager object which allows creation of data in shared memory
        '''
        from processing.localmanager import LocalManager
        return LocalManager()

    def Lock():
        '''
        Returns a non-recursive lock object
        '''
        from processing.synchronize import Lock
        return Lock()

    def RLock():
        '''
        Returns a recursive lock object
        '''
        from processing.synchronize import RLock
        return RLock()

    def Condition(lock=None):
        '''
        Returns a condition object
        '''
        from processing.synchronize import Condition
        return Condition(lock)

    def Semaphore(value=1):
        '''
        Returns a semaphore object
        '''
        from processing.synchronize import Semaphore
        return Semaphore(value)

    def BoundedSemaphore(value=1):
        '''
        Returns a bounded object
        '''
        from processing.synchronize import BoundedSemaphore
        return BoundedSemaphore(value)

    def Event():
        '''
        Returns an event object
        '''
        from processing.synchronize import Event
        return Event()

    def Queue(maxsize=0):
        '''
        Returns a queue object implemented using a pipe
        '''
        from processing.queue import Queue
        return Queue(maxsize)

    def Pool(processes=None):
        '''
        Returns a process pool object
        '''
        from processing.pool import Pool
        return Pool(processes)

    class TimeoutError(Exception):
        pass
