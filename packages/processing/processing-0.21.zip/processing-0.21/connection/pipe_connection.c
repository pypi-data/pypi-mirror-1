/*
 * Extension module used by connection.py to enable the transferring of 
 * pickled data using named pipes
 *
 * pipe_connection.c
 *
 * Copyright (c) 2006, R Oudkerk --- see COPYING.txt
 */

#include <Python.h>
#include "structmember.h"

#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#ifdef __CYGWIN__
void PyErr_SetFromWindowsErr(int number)
{
    PyObject *obj = Py_BuildValue("is", number, "Windows Error");
    PyErr_SetObject(PyExc_OSError, obj);
    Py_XDECREF(obj);
}
#endif

#define BUFSIZE 1024

PyObject *dumpsFunction, *loadsFunction;

typedef struct {
    PyObject_HEAD
    HANDLE handle;
} Connection;


static PyTypeObject ConnectionType;


static BOOL 
recv_string(HANDLE pipe, char **outstring, DWORD *count)
{
    char *buffer;
    BOOL success;
    DWORD BytesLeft, length;
    
    buffer = malloc(BUFSIZE);
    if (buffer == NULL)
        return FALSE;

    success = ReadFile(pipe, buffer, BUFSIZE, &length, NULL);

    if (success) {
        *outstring = buffer;
        *count = length;
        return TRUE;
    } else if (GetLastError() != ERROR_MORE_DATA) {
        free(buffer);
        return FALSE;
    }

    success = PeekNamedPipe(pipe, NULL, 0, NULL, NULL, &BytesLeft);
    
    if (!success) {
        free(buffer);
        return FALSE;
    }
   
    *count = length + BytesLeft;
    *outstring = realloc(buffer, *count);

    if (!*outstring) {
        free(buffer);
        return FALSE;
    }

    success = ReadFile(pipe, *outstring+length, BytesLeft, &length, NULL);
    
    if (!success)
        free(*outstring);

    return success;
}


static BOOL 
send_string(HANDLE pipe, char *s, DWORD length)
{
    DWORD amount_written;
    WriteFile(pipe, s, length, &amount_written, NULL);
    return length == amount_written;
}


static PyObject *
Connection_recv_string(Connection *self) 
{
    char *buffer;
    DWORD length;
    BOOL success;
    PyObject *result;

    Py_BEGIN_ALLOW_THREADS
    success = recv_string((HANDLE)(self->handle), &buffer, &length);
    Py_END_ALLOW_THREADS

    if (!success) {
        PyErr_SetFromWindowsErr(GetLastError());
        return NULL;
    }
    
    result = Py_BuildValue("s#", buffer, length);
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
    success = send_string((HANDLE)(self->handle), buffer, length);
    Py_END_ALLOW_THREADS

    if (!success) {
        PyErr_SetFromWindowsErr(GetLastError());
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *
Connection_recv(Connection *self)
{
    char *buffer;
    DWORD length;
    BOOL success;
    PyObject *result;

    Py_BEGIN_ALLOW_THREADS
    success = recv_string(self->handle, &buffer, &length);
    Py_END_ALLOW_THREADS
        
    if (!success) {
        PyErr_SetFromWindowsErr(GetLastError());
        return NULL;
    }

    result = PyObject_CallFunction(loadsFunction, "s#", buffer, length); 
    free(buffer);
    return result;
}

static PyObject *
Connection_send(Connection *self, PyObject *args)
{
    char *buffer;
    size_t length;
    BOOL success;
    PyObject *obj, *pickled_string;

    if ( !PyArg_ParseTuple( args, "O", &obj) )
        return NULL;

    pickled_string = PyObject_CallFunction(dumpsFunction, "Oi", obj, 2);

    if (!pickled_string)
        return NULL;

    if (PyString_AsStringAndSize(pickled_string, &buffer, &length) != 0)
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    success = send_string(self->handle, buffer, length);
    Py_END_ALLOW_THREADS
        
    Py_DECREF(pickled_string);

    if (!success) {
        PyErr_SetFromWindowsErr(GetLastError());
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *
Connection_close(Connection* self)
{
    BOOL success;

    if (self->handle != NULL) {
        Py_BEGIN_ALLOW_THREADS
        success = CloseHandle(self->handle);
        Py_END_ALLOW_THREADS
        self->handle = NULL;
    }

    if (!success) {
        PyErr_SetFromWindowsErr(GetLastError());
        return NULL;
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
    HANDLE handle;

    self = (Connection*)type->tp_alloc(type, 0);

    if (self == NULL)
        return NULL;

    if (! PyArg_ParseTuple(args, "i", &handle) ) {
        Py_DECREF(self);
        return NULL;
    }
    
    self->handle = handle;

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
    "pipe_connection.Connection", /*tp_name*/
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
    "corresponding to a Windows Named Pipe", /* tp_doc */
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


static PyObject *
Connection_createpipe(PyObject *self, PyObject *args)
{
    char *name;
    HANDLE pipe;
    DWORD openmode = PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT;

    if ( !PyArg_ParseTuple( args, "s", &name) )
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    pipe = CreateNamedPipe(name, PIPE_ACCESS_DUPLEX, openmode, 
                           PIPE_UNLIMITED_INSTANCES, BUFSIZE, BUFSIZE, 
                           NMPWAIT_WAIT_FOREVER, NULL);
    Py_END_ALLOW_THREADS

    if (pipe == INVALID_HANDLE_VALUE) {
        CloseHandle(pipe);
        PyErr_SetFromWindowsErr(GetLastError());
        return NULL;
    }

    return Py_BuildValue("i", pipe);
}

static PyObject *
Connection_connectpipe(PyObject *self, PyObject *args)
{
    HANDLE pipe;
    BOOL success;

    if ( !PyArg_ParseTuple( args, "i", &pipe ) )
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    success = ConnectNamedPipe(pipe, NULL);
    Py_END_ALLOW_THREADS

    if (!success && GetLastError() != ERROR_PIPE_CONNECTED) {
        CloseHandle(pipe);
        PyErr_SetFromWindowsErr(GetLastError());
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *
Connection_waitpipe(PyObject *self, PyObject *args)
{
    char *name;
    BOOL success;
    DWORD timeout;

    if ( !PyArg_ParseTuple( args, "si", &name, &timeout ) )
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    success = WaitNamedPipe(name, timeout);
    Py_END_ALLOW_THREADS

    if (!success) {
        PyErr_SetFromWindowsErr(GetLastError());
        return NULL;
    }

    Py_RETURN_NONE;
}    


static PyObject *
Connection_createfile(PyObject *self, PyObject *args)
{
    char *name;
    HANDLE pipe;
    BOOL success;

    if ( !PyArg_ParseTuple( args, "s", &name ) )
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    pipe = CreateFile(name, GENERIC_READ | GENERIC_WRITE, 
                       0, NULL, OPEN_EXISTING, 0, NULL);
    if (pipe == INVALID_HANDLE_VALUE) {
        success = FALSE;
    } else {
        DWORD dwMode = PIPE_READMODE_MESSAGE; 
        success = SetNamedPipeHandleState(pipe, &dwMode, NULL, NULL);
    }
    Py_END_ALLOW_THREADS

    if (!success) {
        if (pipe != INVALID_HANDLE_VALUE)
            CloseHandle(pipe);
        PyErr_SetFromWindowsErr(GetLastError());
        return NULL;
    }

    return Py_BuildValue("i", pipe);    
}

static PyMethodDef module_methods[] = {
    {"createpipe", (PyCFunction)Connection_createpipe, METH_VARARGS, ""},
    {"connectpipe", (PyCFunction)Connection_connectpipe, METH_VARARGS, ""},
    {"waitpipe", (PyCFunction)Connection_waitpipe, METH_VARARGS, ""},
    {"createfile", (PyCFunction)Connection_createfile, METH_VARARGS, ""},
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC
init_pipe_connection(void) 
{
    PyObject* m, *cPickleModule;

    if (PyType_Ready(&ConnectionType) < 0)
        return;

    m = Py_InitModule("_pipe_connection", module_methods);
    assert(m);

    cPickleModule = PyImport_ImportModule("cPickle");
    assert(cPickleModule);

    dumpsFunction = PyObject_GetAttrString(cPickleModule, "dumps");
    assert(dumpsFunction);

    loadsFunction = PyObject_GetAttrString(cPickleModule, "loads");
    assert(loadsFunction);

    Py_DECREF(cPickleModule);

    Py_INCREF(&ConnectionType);
    PyModule_AddObject(m, "Connection", (PyObject *)&ConnectionType);
}

