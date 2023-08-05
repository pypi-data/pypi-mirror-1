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

__version__ = '0.35'

__all__ = [
    'Process', 'currentProcess', 'activeChildren', 'freezeSupport',
    'ProcessExit', 'Manager', 'Pipe', 'cpuCount', 'Pool', 'TimeoutError'
    ]

#
# Imports
#

import os
import sys
import process

#
# Try importing the C extension module
#

try:
    import _processing
    
except ImportError, e:
    if e.args[0] != 'No module named _processing':
        raise

    HAVE_C_EXTENSION = False
    HAVE_NATIVE_SEMAPHORE = False
    HAVE_NATIVE_QUEUE = False
    
else:
    HAVE_C_EXTENSION = True
    HAVE_NATIVE_SEMAPHORE = hasattr(_processing, 'Blocker')
    HAVE_NATIVE_QUEUE = hasattr(_processing, 'Queue')
    
    BufferTooShort = _processing.BufferTooShort
    __all__ += ['BufferTooShort']

#
# Definitions from `process` module
#

from process import Process, currentProcess, activeChildren
from process import freezeSupport, ProcessExit, Finalize, debug, info

#
# Other definitions that don't need `_processing`
#

def Manager():
    '''
    Returns a manager associated with a running server process

    The managers methods such as `Lock()`, `Condition()` and `Queue()`
    can be used to create shared objects.
    '''
    from managers import SyncManager
    m = SyncManager()
    m.start()
    return m

def Pipe():
    '''
    Returns two connection object connected by a duplex pipe
    '''
    from processing.connection import Pipe
    return Pipe()

def cpuCount():
    '''
    Returns the number of CPUs in the system
    '''
    if sys.platform == 'win32':
        try:
            num = int(os.environ['NUMBER_OF_PROCESSORS'])
        except (ValueError, KeyError):
            pass
    elif sys.platform == 'darwin':
        try:
            num = int(os.popen('sysctl -n hw.ncpu').read())
        except ValueError:
            pass
    else:
        try:
            num = os.sysconf('SC_NPROCESSORS_ONLN')
        except (ValueError, OSError, AttributeError):
            pass
        
    if num >= 1:
        return num
    else:
        raise NotImplementedError
    
def Pool(processes=None):
    '''
    Returns a process pool object
    '''
    from processing.pool import Pool
    return Pool(processes)

class TimeoutError:
    pass

#
# Definitions needing native semaphore support
#

if HAVE_NATIVE_SEMAPHORE:
    
    __all__ += [
        'LocalManager', 'Lock', 'RLock', 'Semaphore',
        'BoundedSemaphore', 'Condition', 'Event',
        'PipeQueue', 'BufferedPipeQueue', 'Queue', 'BufferedQueue'
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

    def Semaphore(value):
        '''
        Returns a semaphore object
        '''
        from processing.synchronize import Semaphore
        return Semaphore(value)

    def BoundedSemaphore(value):
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

    def PipeQueue(maxsize=0):
        '''
        Returns a queue object implemented using a pipe
        '''
        from processing.synchronize import PipeQueue
        return PipeQueue(maxsize)

    def BufferedPipeQueue(maxsize=0):
        '''
        Returns a queue for which `put()` always succeeds without blocking
        '''
        from processing.synchronize import BufferedPipeQueue
        return BufferedPipeQueue(maxsize)

    Queue = PipeQueue
    BufferedQueue = BufferedPipeQueue


if HAVE_NATIVE_QUEUE:

    __all__ += ['PosixQueue', 'BufferedPosixQueue']
    
    def PosixQueue(maxsize=0, msgsize=0):
        '''
        Returns a queue object implemented using a Posix queue
        '''
        from processing.synchronize import PosixQueue
        return PosixQueue(maxsize, msgsize)

    def BufferedPosixQueue(maxsize=0, msgsize=0):
        '''
        Returns a queue for which `put()` always succeeds without blocking
        '''
        from processing.synchronize import BufferedPosixQueue
        return BufferedPosixQueue(maxsize)

    Queue = PosixQueue
    BufferedQueue = BufferedPosixQueue
