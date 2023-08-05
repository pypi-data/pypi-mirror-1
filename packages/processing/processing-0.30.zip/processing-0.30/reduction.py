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
from processing import _processing

if not hasattr(_processing, 'HandleFromPidHandle') and \
   not hasattr(_processing, 'recvfd'):
    raise ImportError, 'Cannot transfer handles/descriptors between processes'


if sys.platform == 'win32':
    
    import msvcrt
    
    #
    # Handles can be transferred between processes using `DuplicateHandle()`
    #
    
    def reduce_handle(handle):
        return (os.getpid(), handle)
    
    def rebuild_handle(reduced_handle):
        pid, old_handle = reduced_handle
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
    
else:   # assume unix

    #
    # On Unix file descriptors can be transferred between processes 
    # over Unix domain sockets.
    #
    # When `reduce_handle()` is run a listener is created (using
    # authentication) and its address is returned.  A thread is
    # spawned which waits for a connection and then transfers the
    # descriptor to the connecting process which calls
    # `rebuild_handle()`.
    #
    
    def _sharer(l, fd):
        try:
            conn = l.accept()
            _processing.sendfd(conn.fileno(), fd)
        finally:
            os.close(fd)
            
    def reduce_handle(fd):
        from threading import Thread
        from processing.connection import Listener
        l = Listener(family='AF_UNIX', authenticate=True)
        fd = os.dup(fd)
        t = Thread(target=_sharer, args=[l, fd])
        t.setDaemon(True)
        t.start()
        return l.address
    
    def rebuild_handle(reduced_handle):
        from processing.connection import Client
        conn = Client(reduced_handle, authenticate=True)
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
    return _processing.SocketConnection(fd)

copy_reg.pickle(_processing.SocketConnection, reduce_socket_connection)
    
#
# Register `socket.socket` with `copy_reg`
#

def reduce_socket(s):
    try:
        Family, Type, Proto = s.family, s.type, s.proto
    except AttributeError:
        # have to guess family, type, proto
        try:
            address = s.getsockname()
        except AttributeError:
            Family, Type, Proto = socket.AF_INET, socket.SOCK_STREAM, 0
        else:
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
    _sock = socket.fromfd(fd, family, type, proto)
    s = object.__new__(socket.socket)
    s._sock = _sock
    s.recv = _sock.recv
    s.send = _sock.send
    for a in ('sendto', 'recvfrom', 'recv_into', 'recvfrom_into'):
        try:
            setattr(s, a, None)
        except AttributeError:
            pass
    return s

copy_reg.pickle(socket.socket, reduce_socket)
