/*
 * Extension module used by connection.py to speed up use of
 * sockets for transferring pickled data.
 *
 * socket_connection.c
 *
 * Copyright (c) 2006, R Oudkerk --- see COPYING.txt
 *
 * (On unix the 'Connection' class also seems to work with file descriptors
 * for pipes produced with 'os.pipe()' and for ordinary files.)
 */

#include <Python.h>
#include "structmember.h"

#ifdef MS_WINDOWS

#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>

#define write(fd, buffer, length) send(fd, buffer, length, 0)
#define read(fd, buffer, length) recv(fd, buffer, length, 0)
#define close(fd) closesocket(fd)
#define SHUT_RDWR SD_BOTH

SOCKET duplicate(SOCKET handle)
{
    HANDLE dup_handle;
    BOOL success = DuplicateHandle(
        GetCurrentProcess(), (HANDLE)handle, GetCurrentProcess(), 
        &dup_handle, 0, FALSE, DUPLICATE_SAME_ACCESS
        );
    
    return success ? (SOCKET)dup_handle : INVALID_SOCKET;
}

typedef SSIZE_T ssize_t;

#else

#include <sys/socket.h>
#include <unistd.h>

#define TRUE (1)
#define FALSE (0)
#define INVALID_SOCKET (-1)
#define duplicate(handle) dup(handle)

typedef int BOOL;
typedef unsigned char BYTE;
typedef int SOCKET;

#endif


#define BUFSIZE 1024


PyObject *SocketError, *dumpsFunction, *loadsFunction;

typedef struct {
    PyObject_HEAD
    SOCKET handle;
    char push_buffer[BUFSIZE];
    char *start, *end;
} Connection;


static PyTypeObject ConnectionType;


static size_t
bytes_to_word(BYTE *buffer)
{
    return buffer[0] + (buffer[1] << 8) + 
        (buffer[2] << 16) + (buffer[3] << 24);
}

static void 
word_to_bytes(size_t d, BYTE *buffer)
{
    buffer[0] = (BYTE)(d & 0xFF);
    buffer[1] = (BYTE)((d >> 8) & 0xFF);
    buffer[2] = (BYTE)((d >> 16) & 0xFF);
    buffer[3] = (BYTE)((d >> 24) & 0xFF);
}

static BOOL
recv_string(int fd, char **buffer, size_t *length, 
            char *p_buffer, char **start, char **end, BOOL *must_free)
{
    ssize_t bytes_read = *end - *start, remaining;
    char *p = NULL;

    *must_free = FALSE;
    *buffer = NULL;
        
    if (BUFSIZE - (*start - p_buffer) < 4) {
        memcpy(p_buffer, *start, bytes_read);
        *end = p_buffer + bytes_read;
        *start = p_buffer;
    }
    
    while (bytes_read < 4) {
        int temp = read(fd, *end, BUFSIZE - (*end - p_buffer));
        if (temp <= 0)
            goto ERR;
        bytes_read += temp;
        *end += temp;
    }
    
    *length = bytes_to_word((BYTE*) *start);
    remaining = *length + 4 - bytes_read;
    
    if (remaining == 0) {
        *buffer = *start + 4;
        *start = *end = p_buffer;
        return TRUE;
    } else if (remaining < 0) {
        *buffer = *start + 4;
        *start += (*length + 4);
        return TRUE;
    }

    *must_free = TRUE;
    *buffer = malloc(*length);
    if (*buffer == NULL)
        goto ERR;
    
    memcpy(*buffer, *start + 4, bytes_read - 4);
    p = *buffer + bytes_read - 4;
    *start = *end = p_buffer;
    
    while (remaining > 0) {
        if ( (bytes_read = read(fd, p, remaining)) <= 0 )
            goto ERR;
        remaining -= bytes_read;
        p += bytes_read;
    }
    
    if (remaining != 0)
        goto ERR;

    return TRUE;
    
 ERR:
    free(*buffer);
    *buffer = NULL;
    *length = 0;
    *start = *end = p_buffer;
    *must_free = FALSE;
    return FALSE;
}

static BOOL
send_string(SOCKET fd, char *buffer, size_t length)
{    
    char *nbuffer = NULL, *p;
    size_t remaining = length + 4;
    ssize_t bytes_written;

    p = nbuffer = malloc(remaining);
    if (p == NULL)
        goto ERR;

    word_to_bytes(length, (BYTE*)nbuffer);
    memcpy(nbuffer+4, buffer, length);

    while (remaining > 0) {
        bytes_written = write(fd, p, remaining);
        if (bytes_written < 0)
            goto ERR;
        remaining -= bytes_written;
        p += bytes_written;
    }
    free(nbuffer);
    return (remaining == 0);

 ERR:
    free(nbuffer);
    return FALSE;
}

static PyObject *
Connection_recv_string(Connection *self) 
{
    char *buffer;
    size_t length;
    BOOL success, must_free;
    PyObject *result;

    Py_BEGIN_ALLOW_THREADS
    success = recv_string(
        self->handle, &buffer, &length, self->push_buffer, 
        &(self->start), &(self->end), &must_free
        );
    Py_END_ALLOW_THREADS

    if (!success) {
        PyErr_SetString(SocketError, "recv_string failed");
        return NULL;
    }
    
    result = Py_BuildValue("s#", buffer, length);
    if (must_free) 
        free(buffer);
    return result;
}


static PyObject *
Connection_send_string(Connection* self, PyObject *args)
{
    char *buffer;
    size_t length;
    BOOL success;


    if ( !PyArg_ParseTuple( args, "s#", &buffer, &length ) )
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    success = send_string(self->handle, buffer, length);
    Py_END_ALLOW_THREADS

    if (!success) {
        PyErr_SetString(SocketError, "send_string failed");
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *
Connection_send(Connection *self, PyObject *args)
{
    char *buffer = NULL;
    int length;
    BOOL success;
    PyObject *obj = NULL, *pickled_string = NULL;

    if ( !PyArg_ParseTuple( args, "O", &obj) )
        goto ERR;

    pickled_string = PyObject_CallFunction(dumpsFunction, "Oi", obj, 2);

    if (!pickled_string)
        goto ERR;

    if (PyString_AsStringAndSize(pickled_string, &buffer, &length) != 0)
        goto ERR;

    Py_BEGIN_ALLOW_THREADS
    success = send_string(self->handle, buffer, length);
    Py_END_ALLOW_THREADS
        
    if (!success) {
        PyErr_SetString(SocketError, "send_string failed");
        goto ERR;
    }

    Py_XDECREF(pickled_string);
    Py_RETURN_NONE;

 ERR:
    Py_XDECREF(pickled_string);
    return FALSE;
}

static PyObject *
Connection_recv(Connection *self)
{
    char *buffer = NULL;
    size_t length;
    PyObject *result;
    BOOL success, must_free;
    
    Py_BEGIN_ALLOW_THREADS
    success = recv_string(self->handle, &buffer, &length, 
              self->push_buffer, &(self->start), &(self->end), &must_free);
    Py_END_ALLOW_THREADS
        
    if (!success) {
        PyErr_SetString(SocketError, "recv_string failed");
        return NULL;
    }
    
    result = PyObject_CallFunction(loadsFunction, "s#", buffer, length);
    
    if (must_free) 
        free(buffer);
    return result;
}

static PyObject *
Connection_close(Connection* self)
{
    if (self->handle != INVALID_SOCKET) {
        shutdown(self->handle, SHUT_RDWR);
        close(self->handle);
        self->handle = INVALID_SOCKET;
    }

    Py_RETURN_NONE;
}

static void
Connection_dealloc(Connection* self)
{
    Connection_close(self);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Connection_new(PyTypeObject *type, PyObject *args)
{
    Connection *self;
    SOCKET handle;

    self = (Connection*)type->tp_alloc(type, 0);

    if (self == NULL)
        return NULL;

    if (! PyArg_ParseTuple(args, "i", &handle) ) {
        Py_DECREF(self);
        return NULL;
    }

    self->handle = duplicate(handle);
    self->start = self->end = self->push_buffer;

    return (PyObject*)self;
}

static PyMemberDef Connection_members[] = {
    {"_handle", T_INT, offsetof(Connection, handle), READONLY, ""},
    {NULL}  /* Sentinel */
};


static PyMethodDef Connection_methods[] = {
    {"close", (PyCFunction)Connection_close, METH_NOARGS,
     "close the connection"},
    {"send_string", (PyCFunction)Connection_send_string, METH_VARARGS, 
     "send a complete string"},
    {"recv_string", (PyCFunction)Connection_recv_string, METH_NOARGS, 
     "receive a complete string"},
    {"send", (PyCFunction)Connection_send, METH_VARARGS, 
     "send a (picklable) object"},
    {"recv", (PyCFunction)Connection_recv, METH_NOARGS, 
     "receive a (picklable) object"},
    {NULL}  /* Sentinel */
};


static PyTypeObject ConnectionType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "socket_connection.Connection", /*tp_name*/
    sizeof(Connection),        /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Connection_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Connection type.  Constructor takes an integer handle"
    "or file descriptor corresponding to a socket", /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Connection_methods,        /* tp_methods */
    Connection_members,        /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                         /* tp_init */
    0,                         /* tp_alloc */
    (newfunc)Connection_new,   /* tp_new */
};

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC
init_socket_connection(void) 
{
    PyObject* m, *otherModule;

    if (PyType_Ready(&ConnectionType) < 0)
        return;

    m = Py_InitModule("_socket_connection", module_methods);

    otherModule = PyImport_ImportModule("cPickle");
    dumpsFunction = PyObject_GetAttrString(otherModule, "dumps");
    loadsFunction = PyObject_GetAttrString(otherModule, "loads");
    Py_XDECREF(otherModule);

    otherModule = PyImport_ImportModule("socket");
    SocketError = PyObject_GetAttrString(otherModule, "error");
    Py_XDECREF(otherModule);

    Py_INCREF(&ConnectionType);
    PyModule_AddObject(m, "Connection", (PyObject *)&ConnectionType);
}

