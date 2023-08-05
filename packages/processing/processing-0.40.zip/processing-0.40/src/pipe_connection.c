/*
 * A type which wraps a pipe handle in message oriented mode
 *
 * pipe_connection.c
 *
 * Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
 */

#include "processing_defs.h"
#include "structmember.h"

extern PyObject *dumpsFunction, *loadsFunction;
extern PyObject *BufferTooShort;

#define CONNECTION_NAME "_processing.PipeConnection"
#define CONNECTION_TYPE PipeConnectionType

#include "pipe_defs.h"
#include "connection.h"
