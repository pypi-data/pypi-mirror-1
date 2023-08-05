#
# A higher level module for using sockets (or named pipes)
#
# processing/connection.py
#
# Copyright (c) 2006, Richard Oudkerk
#
# If available the C extensions 'socket_connection' and
# 'pipe_connection' will be used.
#
# An example is
# 
# >>> l = Listener(family='AF_INET')
# >>> client = Client(l.address)
# >>> server = l.accept()
# >>> client.send(['this', range(10), None])
# >>> server.recv()
# ['this', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], None]
# >>> client.send_string('some string')
# >>> server.recv_string()
# 'some string'
#
# The type of connection is determined by the 'family' argument of
# Listener.  Valid options are 'AF_INET', 'AF_UNIX' (unix only) and
# 'AF_PIPE' (a windows only 'named pipe').
#

__all__ = [ 'Client', 'Listener' ]

import os, threading, socket, time

from cPickle import dumps, loads


def arbitrary_address(family):
    if family == 'AF_UNIX':
        from tempfile import mktemp
        return mktemp(prefix='py-connection-' + os.environ['USER'] + '-')
    elif family == 'AF_INET':
        return ('localhost', 0)
    elif family == 'AF_PIPE':
        arbitrary_address._lock.acquire()
        result = r'\\.\pipe\socket-%d-%d' % (os.getpid(),
                                             arbitrary_address._counter)
        arbitrary_address._counter += 1
        arbitrary_address._lock.release()
        return result
    else:
        raise ValueError, 'unrecognized family'
    
arbitrary_address._lock = threading.Lock()
arbitrary_address._counter = 0


def address_type(address):
    if type(address) == tuple:
        return 'AF_INET'
    elif type(address) is str and address.startswith('\\\\'):
        return 'AF_PIPE'
    elif type(address):
        return 'AF_UNIX'
    else:
        raise ValueError, 'unrecognized address type'


families = ['AF_INET']

if hasattr(socket, 'AF_UNIX'):
    default_family = 'AF_UNIX'
    families += ['AF_UNIX']
else:
    default_family = 'AF_INET'

#
#
#

try:
    from processing import socket_connection

except ImportError:

    def recv_exact(s, length):
        a = s.recv(length)
        if len(a) == length:
            return a
        temp = [a]
        rem = length - len(a)
        for i in xrange(length):
            a = s.recv(rem)
            temp.append(a)
            rem -= len(a)
            if rem == 0:
                return ''.join(temp)
            if len(a) == 0:
                break
        raise socket.error, ('only %d of %d bytes read' % (length-rem, length))

    def recv_string(s):
        data = recv_exact(s, 8)
        length = int(data, 16)
        return recv_exact(s, length)

    def send_string(s, data):
        s.sendall('%08x' % len(data) + data)

    def recv(s):
        data = recv_exact(s, 8)
        length = int(data, 16)
        return loads(recv_exact(s, length))

    def send(s, data):
        data = dumps(data, 2)
        s.sendall('%08x' % len(data) + data)
        

    class _SocketConnection(object):

        def __init__(self, sock):
            self._socket = sock
            self.close = sock.close
            for func in (recv_string, send_string, recv, send):
                setattr(self, func.__name__,
                        func.__get__(sock, _SocketConnection))
                

class SocketListener(object):

    def __init__(self, address=None, family=None, backlog=1):
        if address is None:
            if family is None:
                family = 'AF_INET'
            address = arbitrary_address(family)
        else:
            family = address_type(address)
        self._family = family
        self._socket = socket.socket( getattr(socket, family) )

        self._socket.bind(address)
        self._socket.listen(backlog)
        self._address = self._socket.getsockname()

    def accept(self):
        s, _ = self._socket.accept()
        if 'socket_connection' in globals():
            conn = socket_connection.Connection(s.fileno())
        else:
            conn = _SocketConnection(s._sock)
        self.connection = conn
        return conn

    def close(self):
        if hasattr(self, '_address') and self._family == 'AF_UNIX':
            self._socket.close()
            import os
            os.unlink(self._address)
            del self._address

    def __del__(self):
        self.close()

    address = property(lambda self : self._address)


def SocketClient(address):
    family = address_type(address)
    s = socket.socket( getattr(socket, family) )
    
    for i in xrange(10):
        try:
            s.connect(address)
        except socket.error, e:
            if e[0] != 10061:    # 10061 => connection refused
                raise
            time.sleep(0.01)
        else:
            break
    else:
        raise
    
    if 'socket_connection' in globals():
        conn = socket_connection.Connection(s.fileno())
    else:
        conn = _SocketConnection(s._sock)
    return conn

#
#
#

try:
    from processing import pipe_connection

except ImportError:
    pass

else:

    default_family = 'AF_PIPE'
    families += ['AF_PIPE']

    class PipeListener(object):

        def __init__(self, address=None, backlog=1):
            if address is None:
                address = arbitrary_address('AF_PIPE')
            else:
                assert address_type(address) == 'AF_PIPE'
            self._address = address
            self._next_pipe = pipe_connection.createpipe(address)

        def accept(self):
            pipe_connection.connectpipe(self._next_pipe)
            conn = pipe_connection.Connection(self._next_pipe)
            self._next_pipe = pipe_connection.createpipe(self._address)
            self.connection = conn
            return conn

        def close(self):
            del self._next_pipe

        address = property(lambda self : self._address)


    def PipeClient(address):
        while 1:
            try:
                h = pipe_connection.wait_and_createfile(address, -1)
            except OSError, e:
                if e[0] != 231:    # 231 => all pipes busy
                    raise
            else:
                break

        return pipe_connection.Connection(h)

#
#
#

def Listener(address=None, family=None, backlog=1):
    '''
    Returns a listener object which can be thought of as a bound
    socket which is 'listening' for connections.

    If 'address' is not specified then an arbitrary one is chosen.

    'family' determines the type of connection that will be used:
    acceptable values are 'AF_INET', 'AF_UNIX' (unix only) and
    'AF_PIPE' (windows only).  The default is the one which is assume
    to be fastest.

    The 'backlog' argument is passed on to the 'listen' method of the
    bound socket.  (It is ignored if the family is 'AF_PIPE'.)

    The 'accept' method of the listener object returns a connection
    which can be used for sending and receiving objects or strings.
    '''
    assert 1 <= backlog <= 10
    if family is None:
        if address is not None:
            family = address_type(address)
        else:
            family = default_family
    if family == 'AF_PIPE':
        return PipeListener(address=address, backlog=backlog)
    else:
        return SocketListener(address=address, family=family, backlog=backlog)

def Client(address):
    '''
    Returns a connection to the address of a Listener.
    '''
    if address_type(address) == 'AF_PIPE':
        return PipeClient(address)
    else:
        return SocketClient(address)
    

if __name__ == '__main__':

    obj = ['this', range(10), None]

    for f in families:
        print '\nfamily =', f

        l = Listener(family=f)
        client = Client(l.address)
        server = l.accept()

        print 'sending: ', obj
        client.send(['this', range(10), None])

        print 'received:', server.recv()

    if 'AF_UNIX' in families and 'socket_connection' in globals():
        import os

        print '\nusing socket_connection.Connection ' \
              'with descriptors from os.pipe'

        r, w = os.pipe()
        r = socket_connection.Connection(r)
        w = socket_connection.Connection(w)

        print 'sending: ', obj
        w.send(['this', range(10), None])

        print 'received:', r.recv()
        
