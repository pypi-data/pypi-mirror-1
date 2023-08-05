/*
 * A type which wraps a socket
 *
 * socket_connection.c
 *
 * Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
 */

#include <Python.h>
#include "structmember.h"

extern PyObject *dumpsFunction, *loadsFunction;

#define CONNECTION_NAME "_processing.SocketConnection"
#define CONNECTION_TYPE SocketConnectionType

#include "socket_defs.h"
#include "connection.h"

