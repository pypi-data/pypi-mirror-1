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

#define CONNECTION_NAME "_processing.SocketConnection"
#define CONNECTION_TYPE SocketConnectionType

#include "socket_defs.h"
#include "connection.h"

