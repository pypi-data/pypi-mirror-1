/*
 * Definition of a `Connection` type.  
 * Used by `socket_connection.h` and `pipe_connection.h`.
 *
 * connection.h
 *
 * Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
 */

#ifndef _CONNECTION_H
#define _CONNECTION_H

#define BUFFER_SIZE 1024

typedef struct {
    PyObject_HEAD
    _HANDLE handle;
    char buffer[BUFFER_SIZE];
} Connection;

PyTypeObject CONNECTION_TYPE;

static PyObject *
Connection_recv_string(Connection *self) 
{
    char *freeme = NULL;
    int res;
    PyObject *result = NULL;

    if (self->handle == INVALID_HANDLE) {
        PyErr_SetString(PyExc_AssertionError, "handle is invalid");
        return NULL;
    }
    
    Py_BEGIN_ALLOW_THREADS
    res = recv_string(self->handle, self->buffer, BUFFER_SIZE, &freeme);
    Py_END_ALLOW_THREADS

    if (res < 0) {
        SetExcFromNumber(res);
    } else {    
        if (freeme == NULL) {
            result = Py_BuildValue("s#", self->buffer, res);
        } else {
            result = Py_BuildValue("s#", freeme, res);
            free(freeme);
        }
    }
    
    return result;
}

static PyObject *
Connection_recv_obj(Connection *self)
{
    char *freeme = NULL;
    int res;
    PyObject *result = NULL;
    
    if (self->handle == INVALID_HANDLE) {
        PyErr_SetString(PyExc_AssertionError, "handle is invalid");
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    res = recv_string(self->handle, self->buffer, BUFFER_SIZE, &freeme);
    Py_END_ALLOW_THREADS
        
    if (res < 0) {
        SetExcFromNumber(res);
    } else {    
        if (freeme == NULL) {
            result = PyObject_CallFunction(loadsFunction, "s#", 
                                           self->buffer, res);
        } else {
            result = PyObject_CallFunction(loadsFunction, "s#", 
                                           freeme, res);
            free(freeme);
        }
    }
    
    return result;
}

static PyObject *
Connection_send_string(Connection* self, PyObject *args)
{
    char *buffer;
    size_t length;
    int res;
    
    if (self->handle == INVALID_HANDLE) {
        PyErr_SetString(PyExc_AssertionError, "handle is invalid");
        return NULL;
    }
    
    if ( !PyArg_ParseTuple( args, "s#", &buffer, &length ) )
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    res = send_string(self->handle, buffer, length);
    Py_END_ALLOW_THREADS

    if (res < 0)
        return SetExcFromNumber(res);

    Py_RETURN_NONE;
}

static PyObject *
Connection_send_obj(Connection *self, PyObject *args)
{
    char *buffer;
    int length, res;
    PyObject *obj = NULL, *pickled_string = NULL;

    if (self->handle == INVALID_HANDLE) {
        PyErr_SetString(PyExc_AssertionError, "handle is invalid");
        return NULL;
    }

    if ( !PyArg_ParseTuple( args, "O", &obj) )
        goto ERR;

    pickled_string = PyObject_CallFunction(dumpsFunction, "Oi", obj, 2);

    if (!pickled_string)
        goto ERR;

    if (PyString_AsStringAndSize(pickled_string, &buffer, &length) != 0)
        goto ERR;

    Py_BEGIN_ALLOW_THREADS
    res = send_string(self->handle, buffer, length);
    Py_END_ALLOW_THREADS
        
    if (res < 0)
        return SetExcFromNumber(res);
    
    Py_XDECREF(pickled_string);
    Py_RETURN_NONE;

 ERR:
    Py_XDECREF(pickled_string);
    return FALSE;
}

static PyObject *
Connection_fileno(Connection* self)
{
    if (self->handle == INVALID_HANDLE) {
        PyErr_SetString(PyExc_AssertionError, "handle is invalid");
        return NULL;
    }
    
    return Py_BuildValue("i", self->handle);
}

static PyObject *
Connection_poll(Connection *self, PyObject *args)
{
    double timeout = 0.0;
    int res;
    
    if (self->handle == INVALID_HANDLE) {
        PyErr_SetString(PyExc_AssertionError, "handle is invalid");
        return NULL;
    }
    
    if (! PyArg_ParseTuple(args, "|d", &timeout) )
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    res = poll(self->handle, timeout);
    Py_END_ALLOW_THREADS

    if (res == 1) {
        Py_RETURN_TRUE;
    } else if (res == 0) {
        Py_RETURN_FALSE;
    } else {
        return SetExcFromNumber(res);
    }
}

static PyObject *
Connection_close(Connection* self)
{
    if (self->handle != INVALID_HANDLE) {
        _close(self->handle);
        self->handle = INVALID_HANDLE;
    }
    
    Py_RETURN_NONE;
}

static void
Connection_dealloc(Connection* self)
{
    Py_XDECREF(Connection_close(self));
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Connection_new(PyTypeObject *type, PyObject *args)
{
    Connection *self;
    _HANDLE handle;

    self = (Connection*)type->tp_alloc(type, 0);
    if (self == NULL)
        return NULL;

    if (! PyArg_ParseTuple(args, "i", &handle) ) {
        Py_DECREF(self);
        return NULL;
    }

    self->handle = _duplicate(handle);
    if (self->handle < 0) {
        self->ob_type->tp_free((PyObject*)self);
        return SetExcFromNumber(-1);
    }
    
    return (PyObject*)self;
}


static PyMethodDef Connection_methods[] = {
    {"close", (PyCFunction)Connection_close, METH_NOARGS,
     "close the connection"},
    {"fileno", (PyCFunction)Connection_fileno, METH_NOARGS,
     "file descriptor or handle of the connection"},
    
    {"poll", (PyCFunction)Connection_poll, METH_VARARGS, 
     "whether there is any input available to be read"},
    
    {"_recv_string", (PyCFunction)Connection_recv_string, METH_NOARGS, 
     "receive a complete string"},
    {"_send_string", (PyCFunction)Connection_send_string, METH_VARARGS, 
     "send a complete string"},
    
    {"recv", (PyCFunction)Connection_recv_obj, METH_NOARGS, 
     "receive a (picklable) object"},
    {"send", (PyCFunction)Connection_send_obj, METH_VARARGS, 
     "send a (picklable) object"},
    
    {NULL}  /* Sentinel */
};


PyTypeObject CONNECTION_TYPE = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    CONNECTION_NAME,           /*tp_name*/
    sizeof(Connection),        /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Connection_dealloc, 
                               /*tp_dealloc*/
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
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, 
                               /*tp_flags*/
    "Connection type.  Constructor takes a file descriptor",
                               /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Connection_methods,        /* tp_methods */
    0,                         /* tp_members */
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

#ifdef FALSE_SOCKET

/*
 * To support sharing of socket objects we need to be able to build a
 * socket object from a handle/fd.  Unfortunately Windows lacks the
 * function `socket.fromfd()` so we define a false socket type.
 */

PyTypeObject FalseSocketType;

static PyObject *
socket_send(Connection* self, PyObject *args)
{
    char *buffer = NULL;
    int length, nbytes;

    if (self->handle == INVALID_HANDLE) {
        PyErr_SetString(PyExc_AssertionError, "handle is invalid");
        return NULL;
    }

    if ( !PyArg_ParseTuple( args, "s#", &buffer, &length) )
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    nbytes = _write(self->handle, buffer, length);
    Py_END_ALLOW_THREADS

    if (nbytes < 0)
        return SetExcFromNumber(nbytes);
    
    return Py_BuildValue("i", nbytes);
}

static PyObject *
socket_recv(Connection* self, PyObject *args)
{
    char *buffer = NULL;
    int nbytes;
    size_t length;
    PyObject *result;

    if (self->handle == INVALID_HANDLE) {
        PyErr_SetString(PyExc_AssertionError, "handle is invalid");
        return NULL;
    }

    if ( !PyArg_ParseTuple( args, "I", &length) )
        return NULL;

    if (length == 0) {
        PyErr_SetString(PyExc_AssertionError, "length should be > 0");
        return NULL;
    }
       
    buffer = malloc(length);
    if (buffer == NULL)
        return PyErr_NoMemory();

    Py_BEGIN_ALLOW_THREADS
    nbytes = _read(self->handle, buffer, length);
    Py_END_ALLOW_THREADS

    if (nbytes < 0) {
        free(buffer);
        return SetExcFromNumber(nbytes);
    }

    result = Py_BuildValue("s#", buffer, nbytes);
    free(buffer);
    return result;
}

static PyObject *
socket_sendall(Connection* self, PyObject *args)
{
    char *buffer = NULL;
    int length, res;

    if (self->handle == INVALID_HANDLE) {
        PyErr_SetString(PyExc_AssertionError, "handle is invalid");
        return NULL;
    }

    if ( !PyArg_ParseTuple( args, "s#", &buffer, &length) )
        return NULL;
    
    Py_BEGIN_ALLOW_THREADS
    res = _sendall(self->handle, buffer, length);
    Py_END_ALLOW_THREADS
        
    if (res < 0)
        return SetExcFromNumber(res);
    
    Py_RETURN_NONE;
}

static PyObject *
socket_notimplemented(Connection* self, PyObject *args)
{
    PyErr_SetString(PyExc_NotImplementedError, "not a real socket");
    return NULL;
}

static PyMethodDef socket_methods[] = {
    {"close", (PyCFunction)Connection_close, METH_NOARGS,
     "close the connection"},
    {"fileno", (PyCFunction)Connection_fileno, METH_NOARGS,
     "file descriptor or handle of the connection"},

    {"recv", (PyCFunction)socket_recv, METH_VARARGS, 
     "receive"},
    {"send", (PyCFunction)socket_send, METH_VARARGS, 
     "send"},
    {"sendall", (PyCFunction)socket_sendall, METH_VARARGS, 
     "sendall"},

    {"recv_into", (PyCFunction)socket_notimplemented, METH_VARARGS, 
     "not implemented"},
    {"sendto", (PyCFunction)socket_notimplemented, METH_VARARGS, 
     "not implemented"},
    {"recvfrom", (PyCFunction)socket_notimplemented, METH_VARARGS, 
     "not implemented"},
    {"recvfrom_into", (PyCFunction)socket_notimplemented, METH_VARARGS, 
     "not implemented"},

    {NULL}  /* Sentinel */
};


PyTypeObject FalseSocketType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_processing.falsesocket", /*tp_name*/
    sizeof(Connection),        /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Connection_dealloc, 
                               /*tp_dealloc*/
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
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, 
                               /*tp_flags*/
    "Pretend socket type.  Constructor takes a handle/file descriptor",
                               /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    socket_methods,            /* tp_methods */
    0,                         /* tp_members */
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

#endif /* FALSE_SOCKET */

#endif /* _CONNECTION_H */
