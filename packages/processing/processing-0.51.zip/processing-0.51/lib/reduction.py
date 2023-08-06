#
# Module to support the pickling of different types of connection
# objects and file objects so that they can be transferred between
# different processes.
#
# processing/reduction.py
#
# Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
#

__all__ = []

import os
import sys
import copy_reg
import socket
import threading

from processing import _processing, currentProcess
from processing.logger import debug, subdebug

#
#
#

connections_are_picklable = (
    sys.platform == 'win32' or hasattr(_processing, 'recvfd')
    )

try:
    fromfd = socket.fromfd
except AttributeError:
    def fromfd(fd, family, type, proto=0):
        s = socket._socket.socket()
        _processing.changefd(s, fd, family, type, proto)
        return s

#
#
#

if sys.platform == 'win32':

    import msvcrt, _subprocess
    from processing._processing import win32
    closefd = _processing.win32.CloseHandle

    #
    # Handles can be transferred between processes using `DuplicateHandle()`
    #

    def reduce_handle(handle):
        subdebug('reducing handle %d', handle)
        flags = win32.GetHandleInformation(handle)
        return (os.getpid(), handle, flags & win32.HANDLE_FLAG_INHERIT)

    def rebuild_handle(reduced_handle):
        pid, old_handle, inheritable = reduced_handle
        subdebug('rebuilding handle %d from PID=%d', old_handle, pid)
        
        if inheritable and getattr(currentProcess(), '_inheriting', False):
            return old_handle
        
        process_handle = win32.OpenProcess(
            win32.PROCESS_ALL_ACCESS, False, pid
            )
        try:
            new_handle = _subprocess.DuplicateHandle(
                process_handle, old_handle, _subprocess.GetCurrentProcess(), 
                0, False, _subprocess.DUPLICATE_SAME_ACCESS
                )
        finally:
            win32.CloseHandle(process_handle)

        return new_handle.Detach()
    
    #
    # Register `_processing.PipeConnection` with `copy_reg`
    #
    
    def reduce_pipe_connection(conn):
        return rebuild_pipe_connection, (reduce_handle(conn.fileno()),)
    
    def rebuild_pipe_connection(reduced_handle):
        handle = rebuild_handle(reduced_handle)
        return _processing.PipeConnection(handle, duplicate=False)
    
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
    closefd = os.close

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
                closefd(fd_wanted)
                conn.close()
            except (SystemExit, KeyboardInterrupt):
                raise
            except:
                import traceback
                traceback.print_exc()

    def reduce_handle(fd):
        global _fd_listener

        if not connections_are_picklable:
            raise RuntimeError, 'pickling of file dscriptors not supported'
        
        if _fd_listener is None:
            _fd_lock.acquire()
            try:
                if _fd_listener is None:
                    from processing.connection import Listener
                    debug('starting listener and thread for sending fds')
                    _fd_listener = Listener(family='AF_UNIX',authenticate=True)
                    t = threading.Thread(target=_share_fds)
                    t.setDaemon(True)
                    t.start()
            finally:
                _fd_lock.release()

        dup_fd = os.dup(fd)
        _fd_cache.add(dup_fd)
        subdebug('reducing fd %d', fd)
        return (_fd_listener.address, dup_fd)

    def rebuild_handle(reduced_handle):
        from processing.connection import Client
        address, fd = reduced_handle
        subdebug('rebuilding fd %d', fd)
        conn = Client(address, authenticate=True)
        conn.send(fd)
        return _processing.recvfd(conn.fileno())

#
# Register `_processing.Connection` with `copy_reg`
#

def reduce_connection(conn):
    return rebuild_connection, (reduce_handle(conn.fileno()),)

def rebuild_connection(reduced_handle):
    fd = rebuild_handle(reduced_handle)
    return _processing.Connection(fd, duplicate=False)

copy_reg.pickle(_processing.Connection, reduce_connection)

#
# Register `socket.socket` with `copy_reg`
#

def reduce_socket(s):
    try:
        Family, Type, Proto = s.family, s.type, s.proto
    except AttributeError:
        # have to guess family, type, proto
        address = s.getsockname()
        Family = type(address) is str and socket.AF_UNIX or socket.AF_INET
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
