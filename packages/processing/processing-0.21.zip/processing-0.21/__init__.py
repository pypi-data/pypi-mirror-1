#
# Package analogous to 'threading.py' but using processes
#
# processing/__init__.py
#
# Copyright (c) 2006, R Oudkerk --- see COPYING.txt
#
# This package is intended to duplicate the functionality (and much of
# the API) of threading.py but uses processes instead of threads.  It
# has been tested on Unix and Windows.  A second module
# 'processing.dummy' has the same API but is a simple wrapper for
# 'threading'.  On Windows the module 'processing.nonforking' is used
# to get round the lack of os.fork.
#
# Communication between processes is achieved using proxies which
# communicate with an manager using sockets (or name pipes).
#
# An example:
#
#   from processing import Process, Manager
#
#   def f(q):
#       for i in range(10):
#           q.put(i*i)
#       q.put('STOP')
#
#   if __name__ == '__main__':
#       manager = Manager()        # launch process to handle shared objects
#       queue = manager.Queue()    # create a proxy for a shared queue
#
#       p = Process(target=f, args=[queue])
#       p.start()                  # launch the new process
#
#       result = None
#       while result != 'STOP':
#           result = queue.get()
#           print result
#
#       p.join()                   # wait for the process to finish
#
# More examples can be seen in `test_processing.py` (and
# `test_with.py` which does the same tests but uses the new
# with-statement).
#
# Read README.txt for more information.
#

from processing.process import Process, currentProcess

__all__ = [ 'Process', 'currentProcess', 'Manager' ]

def Manager():
    '''
    Returns an instance of `processing.managers.SyncManager`
    using default aguments.

    The returned object has methods for the creation of shared
    objects; each such method returns a proxy object.

    For example:

    >>> manager = Manager()
    >>> l = manager.list(range(10))
    >>> l.reverse()
    >>> l
    <Proxy[list] object at 0x00c83450>
    >>> print l
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    >>> manager.shutdown()
    '''
    from processing.managers import SyncManager
    return SyncManager()
