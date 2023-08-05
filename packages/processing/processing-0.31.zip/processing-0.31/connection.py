#
# A higher level module for using sockets (or Windows named pipes)
#
# processing/connection.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'Client', 'Listener', 'Pipe' ]

import os
import sys
import socket
import time
import tempfile

from cPickle import dumps, loads
from processing import Finalize, currentProcess

#
# Try to import `_processing` and if cannot define fallback connection type
#

try:
    from processing import _processing

except ImportError:
    import select
    from struct import pack, unpack

    class _SocketConnection(object):
        '''
        A socket connection supporting the sending/receiving of objects
        '''        
        def __init__(self, _sock):
            if hasattr(self, '_sock'):
                _sock = _sock._sock
            self._sock = _sock

        def _recv_string(self, maxlength=-1):
            s = self._sock
            data = _recv_exact(s, 4)
            length = unpack('!I', data)[0]
            if length > maxlength > 0:
                raise socket.error, 'string longer than maxlength'
            return _recv_exact(s, length)

        def _send_string(self, data):
            self._sock.sendall(pack('!I', len(data)) + data)

        def recv(self):
            s = self._sock
            data = _recv_exact(s, 4)
            length = unpack('!I', data)[0]
            return loads(_recv_exact(s, length))

        def send(self, data):
            data = dumps(data, 2)
            self._sock.sendall(pack('!I', len(data)) + data)

        def fileno(self):
            return self._sock.fileno()

        def poll(self, timeout=0):
            res, _, _ = select.select([self._sock.fileno()], [], [], timeout)
            return bool(res)

        def close(self):
            self._sock.close()

    def _recv_exact(s, length):
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

else:
    # On Windows monkey patch `socket` module
    if not hasattr(socket, 'fromfd'):        
        def fromfd(fd, family, type, proto=0):
            assert family == socket.AF_INET
            assert type == socket.SOCK_STREAM
            assert proto == 0
            return _processing.falsesocket(fd)
        socket.fromfd = fromfd
        
#
# Importing `processing.reduction` enables pickling of connection objects etc
#

try:
    import processing.reduction
except ImportError:
    connections_are_picklable = False
else:
    connections_are_picklable = True

#
#
#

def arbitrary_address(family):
    '''
    Return an arbitrary free address for the given family
    '''
    if family == 'AF_INET':
        return ('localhost', 0)
    elif family == 'AF_UNIX':
        return tempfile.mktemp(prefix='pyc%d' % os.getpid())
    elif family == 'AF_PIPE':
        result = tempfile.mktemp(prefix=r'\\.\pipe\pyc%d' % os.getpid())
        return result
    else:
        raise ValueError, 'unrecognized family'
    

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
# Public functions
#

class Listener(object):
    '''
    Returns a listener object.

    This is a wrapper for a bound socket which is 'listening' for
    connections, or for a Windows named pipe.
    '''
    def __init__(self, address=None, family=None, backlog=1,
                 authenticate=False, authkey=None):
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

        `authenticate`
           If this is true then digest authentication is used even if
           `authkey` is` None`.

        `authkey`
           If `authkey` is a string then it will be used as the
           authentication key; otherwise it must be `None`.

           If `authkey` is `None` and `authenticate` is true then
           `currentProcess.getAuthKey()` is used as the authentication
           key.

           If `authkey` is `None` and `authentication` is false then
           no authentication is done.
        '''
        family = family or (address and address_type(address)) \
                 or default_family
        address = address or arbitrary_address(family)

        if family == 'AF_PIPE':
            self._listener = PipeListener(address, backlog)
        else:
            self._listener = SocketListener(address, family, backlog)
            
        if authenticate and authkey is None:
            authkey = currentProcess().getAuthKey()
        elif authenticate:
            assert type(authkey) is str
            
        self._authkey = authkey

    def accept(self):
        '''
        Accept a connection on the bound socket or named pipe of `self`.

        Returns a `Connection` object.
        '''
        c = self._listener.accept()
        if self._authkey:
            deliver_challenge(c, self._authkey)
            answer_challenge(c, self._authkey)
        return c

    def close(self):
        '''
        Close the bound socket or named pipe of `self`.
        '''
        return self._listener.close()

    address = property(lambda self: self._listener._address)
    last_accepted = property(lambda self: self._listener._last_accepted)
    
    
def Client(address, family=None, authenticate=False, authkey=None):
    '''
    Returns a connection to the address of a `Listener`
    '''
    family = family or address_type(address)
    if family == 'AF_PIPE':
        c = PipeClient(address)
    else:
        c = SocketClient(address)
        
    if authenticate and authkey is None:
        authkey = currentProcess().getAuthKey()
    elif authenticate:
        assert type(authkey) is str
        
    if authkey:
        answer_challenge(c, authkey)
        deliver_challenge(c, authkey)
        
    return c


def Pipe():
    '''
    Returns pair of connection objects at either end of a duplex connection
    '''
    if sys.platform == 'win32':
        assert '_processing' in globals()
        l = Listener()
        a = Client(l.address)
        b = l.accept()
        l.close()
        return a, b
    else:
        a, b = socket.socketpair()
        try:
            Connection = _processing.SocketConnection
            c, d = Connection(a.fileno()), Connection(b.fileno())
            a.close()
            b.close()
        except NameError:
            Connection = _SocketConnection
            c, d = Connection(a), Connection(b)
        return c, d
        
#
# Definitions for connections based on sockets
#

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
                
        self.close = Finalize(self, SocketListener._finalize,
                              args=(self._address, self._family, self._socket))

    def accept(self):
        s, self._last_accepted = self._socket.accept()
        try:
            return _processing.SocketConnection(s.fileno())
        except NameError:
            return _SocketConnection(s._sock)

    @staticmethod
    def _finalize(address, family, sock):
        sock.close()
        if family == 'AF_UNIX':
            try:
                os.unlink(address)
            except OSError:
                pass

def SocketClient(address):
    '''
    Return a connection object connected to the socket given by `address`
    '''
    family = address_type(address)
    s = socket.socket( getattr(socket, family) )

    endtime = time.time() + 10
    
    while endtime > time.time():
        try:
            s.connect(address)
        except socket.error, e:
            if e.args[0] != 10061:    # 10061 => connection refused
                raise
            time.sleep(0.01)
        else:
            break
    else:
        raise
    
    try:
        return _processing.SocketConnection(s.fileno())
    except NameError:
        return _SocketConnection(s._sock)

#
# Definitions for connections based on named pipes
#

if '_processing' in globals() and hasattr(_processing, 'PipeConnection'):
    
    default_family = 'AF_PIPE'
    families += ['AF_PIPE']

    class PipeListener(object):
        '''
        Representation of a named pipe
        '''
        def __init__(self, address, backlog=None):
            self._address = address
            self._handle_queue = [_processing.createpipe(address)]
            self._last_accepted = None
            
            def close(queue):
                for handle in queue:
                    _processing.PipeConnection(handle).close()
                    
            self.close = Finalize(self, close, args=[self._handle_queue])
            
        def accept(self):
            handle = self._handle_queue.pop(0)
            _processing.connectpipe(handle)
            self._handle_queue.append(
                _processing.createpipe(self._address)
                )
            conn = _processing.PipeConnection(handle)
            return conn
        
        
    def PipeClient(address):
        '''
        Return a connection object connected to the pipe given by `address`
        '''
        endtime = time.time() + 10
        
        while endtime > time.time():
            try:
                _processing.waitpipe(address, 1000)
                h = _processing.createfile(address)
            except WindowsError, e:
                if e.args[0] not in (121, 231): # 121 => Semaphore timeout
                    raise                       # 231 => All pipes busy
            else:
                break
        else:
            raise
        
        return _processing.PipeConnection(h)

#
# Authentication stuff
#

import hmac, sha

class AuthenticationError(Exception):
    pass

def deliver_challenge(connection, authkey):
    assert type(authkey) is str, '%r is not a string' % authkey
    message = os.urandom(20)
    connection._send_string('#CHALLENGE:' + message)
    digest = hmac.new(authkey, message, sha).digest()
    response = connection._recv_string()
    if response == digest:
        connection._send_string('#WELCOME')
    else:
        connection._send_string('#AUTHENTICATION_FAILED')
        raise AuthenticationError, 'Digest received was wrong'
    
def answer_challenge(connection, authkey):
    assert type(authkey) is str, '%r is not a string' % authkey
    message = connection._recv_string()
    assert message[:11] == '#CHALLENGE:', 'message = %r' % message
    message = message[11:]
    digest = hmac.new(authkey, message, sha).digest()
    connection._send_string(digest)
    response = connection._recv_string()
    if response != '#WELCOME':
        raise AuthenticationError, 'Digest sent was rejected'
    
#
#
#

def _test(address):
    c = Client(address, authenticate=True)
    print 'received: %s' % c.recv()
    
    
if __name__ == '__main__':

    from processing import Process

    obj = ['this', range(10), None]

    print 'authkey =', currentProcess().getAuthKey()


    for f in families:
        print '\nfamily =', f

        l = Listener(family=f, authenticate=True)
        p = Process(target=_test, args=[l.address])
        p.start()

        server = l.accept()

        print 'sending:  %s' % obj
        server.send(obj)
        p.join()


    if 'AF_UNIX' in families and '_processing' in globals():
        print '\nusing _socket_connection.Connection ' \
              'with descriptors from os.pipe'
        
        r, w = os.pipe()
        r = _socket_connection.Connection(r)
        w = _socket_connection.Connection(w)

        print 'sending: ', obj
        w.send(obj)

        print 'received:', r.recv()
