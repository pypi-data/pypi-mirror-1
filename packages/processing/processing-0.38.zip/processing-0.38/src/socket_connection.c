/*
 * A type which wraps a socket
 *
 * socket_connection.c
 *
 * Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
 */

#include <Python.h>
#include "structmember.h"

#ifndef Py_RETURN_NONE
#define Py_RETURN_NONE return Py_INCREF(Py_None), Py_None
#define Py_RETURN_TRUE return Py_INCREF(Py_True), Py_True
#define Py_RETURN_FALSE return Py_INCREF(Py_False), Py_False
#endif

extern PyObject *dumpsFunction, *loadsFunction;
extern PyObject *BufferTooShort;

#define CONNECTION_NAME "_processing.SocketConnection"
#define CONNECTION_TYPE SocketConnectionType

#include "socket_defs.h"
#include "connection.h"

#ifdef MS_WINDOWS

typedef struct {
        PyObject_HEAD
        SOCKET sock_fd;
        int sock_family;
        int sock_type;
        int sock_proto;
        PyObject *(*errorhandler)(void);
        double sock_timeout;
} PySocketSockObject;

extern PyTypeObject *socketType;

PyObject *
socket_changefd(PyObject *self, PyObject *args)
{
    PySocketSockObject *s;
    int family, type, proto=0;
    SOCKET fd, newfd;

    /* should probably use "n" format for fd on Python 2.5 */
    if (!PyArg_ParseTuple(args, "Oiii|i", &s, &fd, &family, &type, &proto))
        return NULL;

    newfd = _duplicate(fd);
    if (newfd == INVALID_SOCKET) {
        PyErr_SetString(PyExc_OSError, "failed to duplicate socket handle");
        return NULL;
    }
    
    if (s->sock_fd != INVALID_SOCKET) {
        Py_BEGIN_ALLOW_THREADS
        closesocket(s->sock_fd);
        Py_END_ALLOW_THREADS
    }

    s->sock_fd = newfd;
    s->sock_family = family;
    s->sock_type = type;
    s->sock_proto = proto;
    
    Py_RETURN_NONE;
}

#endif
