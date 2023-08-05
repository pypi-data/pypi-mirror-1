#
# A higher level module for using sockets (or Windows named pipes)
#
# processing/connection/__init__.py
#
# Copyright (c) 2006, R Oudkerk --- see COPYING.txt
#
# If available the C extensions `socket_connection` and
# `pipe_connection` will be used.
#
# An example is::
# 
#     >>> l = Listener(family='AF_INET')
#     >>> client = Client(l.address)
#     >>> server = l.accept()
#     >>> client.send(['this', range(10), None])
#     >>> server.recv()
#     ['this', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], None]
#     >>> client.send_string('some string')
#     >>> server.recv_string()
#     'some string'
#
# The type of connection is determined by the `family` argument of
# Listener.  Valid options are 'AF_INET', 'AF_UNIX' (unix only) and
# 'AF_PIPE' (a windows only 'named pipe').
#

__all__ = [ 'Client', 'Listener' ]

import os, threading, socket, time

from cPickle import dumps, loads


def arbitrary_address(family):
    '''
    Return an arbitrary free address for the given family
    '''
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
    '''
    Return the types of the address

    This can be 'AF_INET', 'AF_UNIX', or 'AF_PIPE'
    '''
    if type(address) == tuple:
        return 'AF_INET'
    elif type(address) is str and address.startswith('\\\\'):
        return 'AF_PIPE'
    elif type(address) is str:
        return 'AF_UNIX'
    else:
        raise ValueError, 'unrecognized address type'


default_family = 'AF_INET'
families = ['AF_INET']

if hasattr(socket, 'AF_UNIX'):
    default_family = 'AF_UNIX'
    families += ['AF_UNIX']

#
#
#

try:
    from processing.connection import _socket_connection

except ImportError:

    from struct import pack, unpack

    def recv_exact(s, length):
        '''
        read exactly `length` bytes from socket
        '''
        a = s.recv(length)
        if len(a) == length:
            return a
        temp = [a]
        rem = length - len(a)
        while 1:
            a = s.recv(rem)
            temp.append(a)
            rem -= len(a)
            if rem == 0:
                return ''.join(temp)
            if not a:
                break
        raise socket.error, ('only %d of %d bytes read' % (length-rem, length))

    def recv_string(s):
        '''
        receive a complete string
        '''
        data = recv_exact(s, 4)
        length = unpack('!I', data)[0]
        return recv_exact(s, length)

    def send_string(s, data):
        '''
        send a string
        '''
        s.sendall(pack('!I', len(data)) + data)

    def recv(s):
        '''
        recaive an object
        '''
        data = recv_exact(s, 4)
        length = unpack('!I', data)[0]
        return loads(recv_exact(s, length))

    def send(s, data):
        '''
        send an object
        '''
        data = dumps(data, 2)
        s.sendall(pack('!I', len(data)) + data)
        

    class _SocketConnection(object):
        '''
        A socket connection supporting the sending/receiving of objects
        '''
        def __init__(self, sock):
            self._socket = sock
            self.close = sock.close
            for func in (recv_string, send_string, recv, send):
                setattr(self, func.__name__,
                        func.__get__(sock, _SocketConnection))
                

class SocketListener(object):
    '''
    Represtation of a socket which is bound to an address and listening
    '''
    def __init__(self, address, family, backlog=1):
        self._socket = socket.socket( getattr(socket, family) )
        self._socket.bind(address)
        self._socket.listen(backlog)
        self._address = self._socket.getsockname()
        self._family = family
        self._last_accepted = None

    def accept(self):
        s, self._last_accepted = self._socket.accept()
        if '_socket_connection' in globals():
            conn = _socket_connection.Connection(s.fileno())
        else:
            conn = _SocketConnection(s._sock)
        self.connection = conn
        return conn

    def close(self):
        if hasattr(self, '_address') and self._family == 'AF_UNIX':
            import os
            os.unlink(self._address)
            del self._address
        self._socket.close()

    def __del__(self):
        self.close()


def SocketClient(address):
    '''
    Return a connection object connected to the socket given by `address`
    '''
    family = address_type(address)
    s = socket.socket( getattr(socket, family) )

    # on windows try connecting up to 10 times
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
    
    if '_socket_connection' in globals():
        conn = _socket_connection.Connection(s.fileno())
    else:
        conn = _SocketConnection(s._sock)
    return conn

#
#
#

try:
    from processing.connection import _pipe_connection

except ImportError:
    pass

else:
    default_family = 'AF_PIPE'
    families += ['AF_PIPE']

    class PipeListener(object):
        '''
        Representation of a named pipe
        '''
        def __init__(self, address, backlog=1):
            self._address = address
            self._next_pipe = _pipe_connection.createpipe(address)
            self._last_accepted = None

        def accept(self):
            _pipe_connection.connectpipe(self._next_pipe)
            conn = _pipe_connection.Connection(self._next_pipe)
            self._next_pipe = _pipe_connection.createpipe(self._address)
            self.connection = conn
            return conn

        def close(self):
            del self._next_pipe


    def PipeClient(address):
        '''
        Return a connection object connected to the pipe given by `address`
        '''
        while 1:
            try:
                _pipe_connection.waitpipe(address, -1);
                h = _pipe_connection.createfile(address)
            except OSError, e:
                if e[0] != 231:    # 231 => all pipes busy
                    raise
            else:
                break
        return _pipe_connection.Connection(h)

#
#
#

class Listener(object):
    '''
    Returns a listener object.

    This is a wrapper for a bound socket which is 'listening' for
    connections, or for a Windows named pipe.
    '''
    def __init__(self, address=None, family=None, backlog=1):    
        '''
        `address`
           The address to be used by the bound socket
           or named pipe of `self`.

        `family`
           The type of the socket or named pipe to use.

           This can be one of the strings 'AF_INET' (for a TCP
           socket), 'AF_UNIX' (for a Unix domain socket) or 'AF_PIPE'
           (for a Windows named pipe).  Of these only the first is
           guaranteed to be available.

           If `family` is None than the family is inferred by the
           format of `address`.  If `address` is unspecified then 
           a default is chosen which is dependent on the platform.
           This default is the family which is assumed to be the
           fastest available.
        
        `backlog`
           If the `self` uses a socket then this is passed to the
           `listen()` method of the socket once it has been bound.
        '''
        family = family or (address and address_type(address)) \
                 or default_family
        address = address or arbitrary_address(family)

        if family == 'AF_PIPE':
            self._listener = PipeListener(address, backlog)
        else:
            self._listener = SocketListener(address, family, backlog)
            
    def accept(self):
        '''
        Accept a connection on the bound socket or named pipe of `self`.

        Returns a `Connection` object.
        '''
        return self._listener.accept()

    def close(self):
        '''
        Close the bound socket or named pipe of `self`.
        '''
        return self._listener.close()

    address = property(lambda self: self._listener._address)
    last_accepted = property(lambda self: self._listener._last_accepted)
    

def Client(address, family=None):
    '''
    Returns a connection to the address of a `Listener`.
    '''
    family = family or address_type(address)
    if family == 'AF_PIPE':
        return PipeClient(address)
    else:
        return SocketClient(address)
    

def test(address):
    c = Client(address)
    print 'received: %s' % c.recv()    



if __name__ == '__main__':
    from processing import Process

    obj = ['this', range(10), None]

    for f in families:
        print '\nfamily =', f

        l = Listener(family=f)
        p = Process(target=test, args=[l.address])
        p.start()

        server = l.accept()

        print 'sending:  %s' % obj
        server.send(obj)
        p.join()


    if 'AF_UNIX' in families and '_socket_connection' in globals():
        print '\nusing _socket_connection.Connection ' \
              'with descriptors from os.pipe'

        r, w = os.pipe()
        r = _socket_connection.Connection(r)
        w = _socket_connection.Connection(w)

        print 'sending: ', obj
        w.send(obj)

        print 'received:', r.recv()
        
