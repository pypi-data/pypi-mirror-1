#
# Module to support the pickling of different types of connection
# objects and file objects so that they can be transferred between
# different processes.
#
# processing/reduction.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#

__all__ = []

import os, sys, copy_reg, socket
import _processing
import process

#
#
#

if (not hasattr(_processing, 'HandleFromPidHandle') and
    not hasattr(_processing, 'recvfd')):
    raise ImportError, 'Cannot transfer handles/descriptors between processes'

try:
    fromfd = socket.fromfd
except AttributeError:
    def fromfd(fd, family, type, proto=0):
        s = socket._socket.socket()
        _processing.changefd(s, fd, family, type, proto)
        return s
    
if sys.platform == 'win32':
    closefd = _processing.CloseHandle
else:
    closefd = os.close

#
#
#

if sys.platform == 'win32':

    import msvcrt

    #
    # Handles can be transferred between processes using `DuplicateHandle()`
    #

    def reduce_handle(handle):
        process.subdebug('reducing handle %d', handle)
        return (os.getpid(), handle)

    def rebuild_handle(reduced_handle):
        pid, old_handle = reduced_handle
        process.subdebug('rebuilding handle %d from PID=%d', old_handle, pid)
        return _processing.HandleFromPidHandle(pid, old_handle)

    #
    # Register `file` with `copy_reg`
    #

    def reduce_file(f):
        reduced_handle = reduce_handle(msvcrt.get_osfhandle(f.fileno()))
        return rebuild_file, (reduced_handle, f.mode)

    def rebuild_file(reduced_handle, mode):
        fd = msvcrt.open_osfhandle(rebuild_handle(reduced_handle), 0)
        return os.fdopen(fd, mode)

    copy_reg.pickle(file, reduce_file)

    #
    # Register `_processing.PipeConnection` with `copy_reg`
    #
    
    def reduce_pipe_connection(conn):
        return rebuild_pipe_connection, (reduce_handle(conn.fileno()),)

    def rebuild_pipe_connection(reduced_handle):
        handle = rebuild_handle(reduced_handle)
        return _processing.PipeConnection(handle)

    copy_reg.pickle(_processing.PipeConnection, reduce_pipe_connection)

else:

    #
    # On Unix file descriptors can be transferred between processes
    # over Unix domain sockets.
    #
    # When we first use `reduce_handle()` we start a server thread
    # which listens to a Unix domain socket for connections from
    # client processes.  When a client process asks for an fd the
    # thread sends it using `_processing.sendfd()`.
    #

    import threading
    
    _fd_cache = set()
    _fd_lock = threading.Lock()
    _fd_listener = None

    def _share_fds():
        while 1:
            try:
                conn = _fd_listener.accept()
                fd_wanted = conn.recv()
                _fd_cache.remove(fd_wanted)
                _processing.sendfd(conn.fileno(), fd_wanted)
                os.close(fd_wanted)
                del conn
            except (SystemExit, KeyboardInterrupt):
                raise
            except:
                import traceback
                traceback.print_exc()

    def reduce_handle(fd):
        global _fd_listener
        
        if _fd_listener is None:
            _fd_lock.acquire()
            try:
                if _fd_listener is None:
                    from processing.connection import Listener
                    process.debug('starting listener and '
                                  'thread for sending fds')
                    _fd_listener = Listener(family='AF_UNIX',authenticate=True)
                    t = threading.Thread(target=_share_fds)
                    t.setDaemon(True)
                    t.start()
            finally:
                _fd_lock.release()

        dup_fd = os.dup(fd)
        _fd_cache.add(dup_fd)
        process.subdebug('reducing fd %d', fd)
        return (_fd_listener.address, dup_fd)

    def rebuild_handle(reduced_handle):
        from processing.connection import Client
        address, fd = reduced_handle
        process.subdebug('rebuilding fd %d', fd)
        conn = Client(address, authenticate=True)
        conn.send(fd)
        return _processing.recvfd(conn.fileno())

    #
    # Register `file` with `copy_reg`
    #

    def reduce_file(f):
        reduced_handle = reduce_handle(f.fileno())
        return rebuild_file, (reduced_handle, f.mode)

    def rebuild_file(reduced_handle, mode):
        fd = rebuild_handle(reduced_handle)
        return os.fdopen(fd, mode)

    copy_reg.pickle(file, reduce_file)


#
# Register `_processing.SocketConnection` with `copy_reg`
#

def reduce_socket_connection(conn):
    reduced_handle = reduce_handle(conn.fileno())
    return rebuild_socket_connection, (reduced_handle,)

def rebuild_socket_connection(reduced_handle):
    fd = rebuild_handle(reduced_handle)
    conn = _processing.SocketConnection(fd)
    closefd(fd)
    return conn

copy_reg.pickle(_processing.SocketConnection, reduce_socket_connection)

#
# Register `socket.socket` with `copy_reg`
#

def reduce_socket(s):
    try:
        Family, Type, Proto = s.family, s.type, s.proto
    except AttributeError:
        # have to guess family, type, proto
        address = s.getsockname()
        if type(address) is str:
            Family = socket.AF_UNIX
        else:
            Family = socket.AF_INET
        Type = s.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
        Proto = 0
    reduced_handle = reduce_handle(s.fileno())
    return rebuild_socket, (reduced_handle, Family, Type, Proto)

def rebuild_socket(reduced_handle, family, type, proto):
    fd = rebuild_handle(reduced_handle)
    _sock = fromfd(fd, family, type, proto)
    closefd(fd)
    return socket.socket(_sock=_sock)

copy_reg.pickle(socket.socket, reduce_socket)
