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
import itertools

from processing.process import currentProcess
from processing.finalize import Finalize
from processing.logger import subdebug
from processing._processing import *

try:
    import processing.reduction
except ImportError:
    connections_are_picklable = False
else:
    connections_are_picklable = True

#
#
#

BUFSIZE = 8192

_nextid = itertools.count().next

default_family = 'AF_INET'
families = ['AF_INET']

if hasattr(socket, 'AF_UNIX'):
    default_family = 'AF_UNIX'
    families += ['AF_UNIX']

if sys.platform == 'win32':
    default_family = 'AF_PIPE'
    families += ['AF_PIPE']

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
        return tempfile.mktemp(prefix='pyc-%d-%d-' % (os.getpid(), _nextid()))
    elif family == 'AF_PIPE':
        result = tempfile.mktemp(prefix=r'\\.\pipe\pyc-%d-%d-' %
                                 (os.getpid(), _nextid()))
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


if sys.platform != 'win32':

    def Pipe(duplex=True):
        '''
        Returns pair of connection objects at either end of a pipe
        '''
        if duplex:
            s1, s2 = socket.socketpair()
            c1, c2 = Connection(s1.fileno()), Connection(s2.fileno())
            s1.close()
            s2.close()
        else:
            fd1, fd2 = os.pipe()
            c1, c2 = Connection(fd1), Connection(fd2)
            os.close(fd1)
            os.close(fd2)

        return c1, c2
    
else:

    def Pipe(duplex=True):
        '''
        Returns pair of connection objects at either end of a pipe
        '''
        address = arbitrary_address('AF_PIPE')
        if duplex:
            openmode = PIPE_ACCESS_DUPLEX
            access = GENERIC_READ | GENERIC_WRITE
            obsize, ibsize = BUFSIZE, BUFSIZE
        else:
            openmode = PIPE_ACCESS_INBOUND
            access = GENERIC_WRITE
            obsize, ibsize = 0, BUFSIZE

        h1 = CreateNamedPipe(
            address, openmode,
            PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
            1, obsize, ibsize, NMPWAIT_WAIT_FOREVER, NULL
            )
        h2 = CreateFile(address, access, 0, NULL, OPEN_EXISTING, 0, NULL)
        SetNamedPipeHandleState(h2, PIPE_READMODE_MESSAGE, None, None)

        try:
            ConnectNamedPipe(h1, NULL)
        except WindowsError, e:
            if e.args[0] != ERROR_PIPE_CONNECTED:
                raise

        c1 = PipeConnection(h1)
        c2 = PipeConnection(h2)
        CloseHandle(h1)
        CloseHandle(h2)
        return c1, c2

#
# Definitions for connections based on sockets
#

class SocketListener(object):
    '''
    Represtation of a socket which is bound to an address and listening
    '''
    def __init__(self, address, family, backlog=1):
        self._socket = socket.socket(getattr(socket, family))
        self._socket.bind(address)
        if family == 'AF_UNIX':
            os.chmod(address, int('0600', 8))  # readable/writable only by user
        self._socket.listen(backlog)
        address = self._socket.getsockname()
        if type(address) is tuple:
            address = (socket.getfqdn(address[0]),) + address[1:]
        self._address = address
        self._family = family
        self._last_accepted = None

        subdebug('listener has bound address %r', self._address)

        if family == 'AF_UNIX':
            self.close = Finalize(
                self, SocketListener._finalize_socketlistener,
                args=[self._address, self._family, self._socket],
                exitpriority=0
                )

    def accept(self):
        s, self._last_accepted = self._socket.accept()
        conn = Connection(s.fileno())
        s.close()
        return conn

    @staticmethod
    def _finalize_socketlistener(address, family, sock):
        subdebug('closing listener with address=%r', address)
        import os
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

    conn = Connection(s.fileno())
    s.close()
    return conn

#
# Definitions for connections based on named pipes
#

if sys.platform == 'win32':

    class PipeListener(object):
        '''
        Representation of a named pipe
        '''        
        def __init__(self, address, backlog=None):
            self._address = address
            handle = CreateNamedPipe(
                address, PIPE_ACCESS_DUPLEX,
                PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
                PIPE_UNLIMITED_INSTANCES, BUFSIZE, BUFSIZE,
                NMPWAIT_WAIT_FOREVER, NULL
                )
            self._handle_queue = [handle]
            self._last_accepted = None
            
            subdebug('listener created with address=%r', self._address)

            self.close = Finalize(
                self, PipeListener._finalize_pipelistener,
                args=(self._handle_queue, self._address), exitpriority=0
                )
            
        def accept(self):
            handle = self._handle_queue.pop(0)
            try:
                ConnectNamedPipe(handle, NULL)
            except WindowsError, e:
                if e.args[0] != ERROR_PIPE_CONNECTED:
                    raise
            newhandle = CreateNamedPipe(
                self._address, PIPE_ACCESS_DUPLEX,
                PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
                PIPE_UNLIMITED_INSTANCES, BUFSIZE, BUFSIZE,
                NMPWAIT_WAIT_FOREVER, NULL
                )
            self._handle_queue.append(newhandle)
            conn = PipeConnection(handle)
            CloseHandle(handle)
            return conn

        @staticmethod
        def _finalize_pipelistener(queue, address):
            subdebug('closing listener with address=%r', address)
            for handle in queue:
                CloseHandle(handle)
        
    def PipeClient(address):
        '''
        Return a connection object connected to the pipe given by `address`
        '''
        endtime = time.time() + 10

        while endtime > time.time():
            try:
                WaitNamedPipe(address, 1000)
                h = CreateFile(
                    address, GENERIC_READ | GENERIC_WRITE,
                    0, NULL, OPEN_EXISTING, 0, NULL
                    )
            except WindowsError, e:
                if e.args[0] not in (ERROR_SEM_TIMEOUT, ERROR_PIPE_BUSY):
                    raise
            else:
                break
        else:
            raise

        SetNamedPipeHandleState(h, PIPE_READMODE_MESSAGE, None, None)
        conn = PipeConnection(h)
        CloseHandle(h)
        return conn

#
# Authentication stuff
#

import hmac, sha

class AuthenticationError(Exception):
    pass

def deliver_challenge(connection, authkey):
    assert type(authkey) is str, '%r is not a string' % authkey
    try:
        message = os.urandom(20)
    except AttributeError:
        import random
        message = ''.join(str(random.randrange(256)) for i in range(20))
    connection.sendbytes('#CHALLENGE:' + message)
    digest = hmac.new(authkey, message, sha).digest()
    response = connection.recvbytes()
    if response == digest:
        connection.sendbytes('#WELCOME')
    else:
        connection.sendbytes('#AUTHENTICATION_FAILED')
        raise AuthenticationError, 'digest received was wrong'

def answer_challenge(connection, authkey):
    assert type(authkey) is str, '%r is not a string' % authkey
    message = connection.recvbytes()
    assert message[:11] == '#CHALLENGE:', 'message = %r' % message
    message = message[11:]
    digest = hmac.new(authkey, message, sha).digest()
    connection.sendbytes(digest)
    response = connection.recvbytes()
    if response != '#WELCOME':
        raise AuthenticationError, 'digest sent was rejected'

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

    for duplex in (True, False):
        print '\nusing Pipe(duplex=%s)' % duplex
        r, w = Pipe(duplex=duplex)
        print 'sending: ', obj
        w.send(obj)
        print 'received:', r.recv()

    try:
        r.send(1)
    except OSError:
        pass
    else:
        print 'expected OSError from r.send(...)'

    try:
        w.recv()
    except OSError:
        pass
    else:
        print 'expected OSError from w.recv(...)'
