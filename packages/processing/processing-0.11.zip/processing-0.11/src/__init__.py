#
# Package analogous to 'threading.py' but using processes
#
# processing/__init__.py
#
# Copyright (c) 2006, Richard Oudkerk
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
# More examples can be seen in test_processing.py (and test_with.py
# which does the same tests but uses the new with-statement).  Also read 
# README.txt for more information.
#

from process import Process, currentProcess

__all__ = [ 'Process', 'Manager', 'currentProcess', 'Repr',
            'Listener', 'Client' ]

def Repr(p):
    '''
    Representation of the object to which the proxy p refers
    '''
    return p._repr()

def Manager(family=None, address=None, autostart=True):
    '''
    Returns an object manager.

    This is an instance of a subclass of Process.  It has methods for
    the creation of shared objects which return proxy objects.

    For example:

    >>> manager = Manager()
    >>> l = manager.list(range(10))
    >>> l.reverse()
    >>> print l
    <Proxy[list] object at 0x00c83450>
    >>> print Repr(l)
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    >>> del l
    >>> manager.shutdown()
    '''
    try:
        return _manager.DefaultManager(family, address, autostart)
    except NameError:
        from processing import manager
        globals()['_manager'] = manager
        return _manager.DefaultManager(family, address, autostart)

def Listener(address=None, family=None, backlog=1):
    '''
    Returns a 'binder object' which can be thought of as a bound
    socket which is 'listening' for connections.  An example of its
    usage is

    >>> l = Listener(family='AF_INET')
    >>> client = Client(l.address)
    >>> server = l.accept()
    >>> client.send(['this', range(10), None])
    >>> server.recv()
    ['this', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], None]
    >>> client.send_string('some string')
    >>> server.recv_string()
    'some string'

    If 'address' is not specified then an arbitrary one is chosen.

    'family' determines the type of connection that will be used:
    acceptable values are 'AF_INET', 'AF_UNIX' (unix only) and
    'AF_PIPE' (windows only).  The default is the one which is assume
    to be fastest.

    The 'backlog' argument is passed on to the 'listen' method of the
    bound socket.  (It is ignored if the family is 'AF_PIPE'.)

    The 'accept' method of the binder object returns a connection
    which can be used for sending and receiving objects or strings.
    '''
    try:
        return _connection.Listener(address, family, backlog)
    except NameError:
        from processing import connection
        globals()['_connection'] = connection
        return _connection.Listener(address, family, backlog)

def Client(address):
    '''
    Returns a connection to the address of a Listener.
    '''
    try:
        return _connection.Client(address)
    except NameError:
        from processing import connection
        globals()['_connection'] = connection
        return _connection.Client(address)
