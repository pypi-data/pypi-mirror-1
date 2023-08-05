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

#define CHECKHANDLE(self) \
    if (self->handle == INVALID_HANDLE) { \
        PyErr_SetString(PyExc_OSError, "handle is invalid"); \
        return NULL; \
    }

typedef struct {
    PyObject_HEAD
    _HANDLE handle;
    char buffer[BUFFER_SIZE];
} Connection;

PyTypeObject CONNECTION_TYPE;

/*
 * Functions for transferring buffers
 */

static PyObject *
Connection_sendbytes(Connection* self, PyObject *args)
{
    char *buffer;
    int res;
    Py_ssize_t length;
    
    CHECKHANDLE(self);
    
    if (!PyArg_ParseTuple(args, "s#", &buffer, &length))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    res = send_string(self->handle, buffer, length);
    Py_END_ALLOW_THREADS

    if (res < 0)
        return SetExcFromNumber(res);

    Py_RETURN_NONE;
}

static PyObject *
Connection_recvbytes(Connection *self) 
{
    char *freeme = NULL;
    Py_ssize_t nbytes;
    PyObject *result = NULL;

    CHECKHANDLE(self);
    
    Py_BEGIN_ALLOW_THREADS
    nbytes = recv_string(self->handle, self->buffer, BUFFER_SIZE, &freeme);
    Py_END_ALLOW_THREADS

    if (nbytes < 0) {
        SetExcFromNumber(nbytes);
    } else {    
        if (freeme == NULL) {
            result = Py_BuildValue("s#", self->buffer, nbytes);
        } else {
            result = Py_BuildValue("s#", freeme, nbytes);
            free(freeme);
        }
    }
    
    return result;
}

static PyObject *
Connection_recvbytes_into(Connection *self, PyObject *args) 
{
    char *freeme = NULL, *buffer = NULL;
    Py_ssize_t nbytes, length;
    int offset=0;
    PyObject *result = NULL;

    CHECKHANDLE(self);
    
    if (!PyArg_ParseTuple(args, "w#|i", &buffer, &length, &offset))
        return NULL;
    
    if (offset < 0) {
        PyErr_SetString(PyExc_ValueError, "negative offset");
        return NULL;
    }   

    if (offset > length) {
        PyErr_SetString(PyExc_ValueError, "offset too large");
        return NULL;
    }   

    Py_BEGIN_ALLOW_THREADS
    nbytes = recv_string(self->handle, buffer+offset, length-offset, &freeme);
    Py_END_ALLOW_THREADS

    if (nbytes < 0) {
        SetExcFromNumber(nbytes);
    } else {
        if (freeme == NULL) {
            result = Py_BuildValue("i", nbytes);
        } else {
            result = PyObject_CallFunction(BufferTooShort, 
                                           "s#", freeme, nbytes);
            free(freeme);
            PyErr_SetObject(BufferTooShort, result);
            Py_XDECREF(result);
            return NULL;
        }
    }
    
    return result;
}

/*
 * Functions for transferring objects
 */

static PyObject *
Connection_send_obj(Connection *self, PyObject *args)
{
    char *buffer;
    int res;
    Py_ssize_t length;
    PyObject *obj = NULL, *pickled_string = NULL;

    CHECKHANDLE(self);

    if (!PyArg_ParseTuple(args, "O", &obj))
        goto ERR;

    pickled_string = PyObject_CallFunction(dumpsFunction, "Oi", obj, 2);

    if (!pickled_string)
        goto ERR;

    if (PyString_AsStringAndSize(pickled_string, &buffer, &length) != 0)
        goto ERR;

    if (length > 0x7fffffff) {
        PyErr_SetString(PyExc_ValueError, "string too long");
        goto ERR;
    }

    Py_BEGIN_ALLOW_THREADS
    res = send_string(self->handle, buffer, (int)length);
    Py_END_ALLOW_THREADS
        
    if (res < 0)
        return SetExcFromNumber(res);
    
    Py_XDECREF(pickled_string);
    Py_RETURN_NONE;

 ERR:
    Py_XDECREF(pickled_string);
    return NULL;
}

static PyObject *
Connection_recv_obj(Connection *self)
{
    char *freeme = NULL;
    Py_ssize_t nbytes;
    PyObject *result = NULL;
    
    CHECKHANDLE(self);

    Py_BEGIN_ALLOW_THREADS
    nbytes = recv_string(self->handle, self->buffer, BUFFER_SIZE, &freeme);
    Py_END_ALLOW_THREADS
        
    if (nbytes < 0) {
        SetExcFromNumber(nbytes);
    } else {    
        if (freeme == NULL) {
            result = PyObject_CallFunction(loadsFunction, "s#", 
                                           self->buffer, nbytes);
        } else {
            result = PyObject_CallFunction(loadsFunction, "s#", 
                                           freeme, nbytes);
            free(freeme);
        }
    }
    
    return result;
}

/*
 * Other functions
 */

static PyObject *
Connection_fileno(Connection* self)
{
    CHECKHANDLE(self);
    
    return Py_BuildValue("i", self->handle);
}

static PyObject *
Connection_poll(Connection *self, PyObject *args)
{
    double timeout = 0.0;
    int res;
    
    CHECKHANDLE(self);

    if (! PyArg_ParseTuple(args, "|d", &timeout))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    res = poll(self->handle, timeout);
    Py_END_ALLOW_THREADS

    if (res == TRUE) {
        Py_RETURN_TRUE;
    } else if (res == FALSE) {
        Py_RETURN_FALSE;
    } else {
        return SetExcFromNumber(res);
    }
}

static PyObject *
Connection_close(Connection* self)
{
    if (self->handle != INVALID_HANDLE) {
        Py_BEGIN_ALLOW_THREADS
        _close(self->handle);
        Py_END_ALLOW_THREADS
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

    if (! PyArg_ParseTuple(args, "i", &handle)) {
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
    
    {"recv", (PyCFunction)Connection_recv_obj, METH_NOARGS, 
     "receive a (picklable) object"},
    {"send", (PyCFunction)Connection_send_obj, METH_VARARGS, 
     "send a (picklable) object"},
    
    {"recvbytes", (PyCFunction)Connection_recvbytes, METH_NOARGS, 
     "receive byte data as a string"},
    {"sendbytes", (PyCFunction)Connection_sendbytes, METH_VARARGS, 
     "send the byte data from a readable buffer-like (such as a string)"},

    {"recvbytes_into", (PyCFunction)Connection_recvbytes_into, METH_VARARGS, 
     "receive byte data into a writeable buffer-like object\n"
     "returns the number of bytes read"},
    
    {"poll", (PyCFunction)Connection_poll, METH_VARARGS, 
     "whether there is any input available to be read"},

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
    0,                         /*tp_hash*/
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, 
                               /*tp_flags*/
    "Connection type.\n"
    "The constructor takes an fd/handle as its argument.\n"
    "The instance uses a duplicated copy of the fd/handle.",
                               /*tp_doc*/
    0,		               /*tp_traverse*/
    0,		               /*tp_clear*/
    0,		               /*tp_richcompare*/
    0,		               /*tp_weaklistoffset*/
    0,		               /*tp_iter*/
    0,		               /*tp_iternext*/
    Connection_methods,        /*tp_methods*/
    0,                         /*tp_members*/
    0,                         /*tp_getset*/
    0,                         /*tp_base*/
    0,                         /*tp_dict*/
    0,                         /*tp_descr_get*/ 
    0,                         /*tp_descr_set*/
    0,                         /*tp_dictoffset*/
    0,                         /*tp_init*/
    0,                         /*tp_alloc*/
    (newfunc)Connection_new,   /*tp_new*/
};

#endif /* _CONNECTION_H */
