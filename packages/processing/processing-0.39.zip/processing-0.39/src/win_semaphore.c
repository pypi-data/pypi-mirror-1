/*
 * A type which wraps a windows mutex or semaphore
 *
 * win_semaphore.c
 *
 * Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
 */

#include "processing_defs.h"
#include "pythread.h"

#define WIN32_LEAN_AND_MEAN
#include <windows.h>

enum { MUTEX, RECURSIVE_MUTEX, SEMAPHORE, BOUNDED_SEMAPHORE };

#define IS_MUTEX(self) ((self)->kind < SEMAPHORE)

typedef struct {
    PyObject_HEAD
    char *name;
    HANDLE *handle;
    int kind;
    int count;
    long last_tid;
} Blocker;


PyTypeObject BlockerType;


static PyObject *
sync_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Blocker *self;
    
    self = (Blocker*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->name = NULL;
        self->handle = NULL;
    }
        
    return (PyObject*)self;
}

static int
sync_init(Blocker *self, PyObject *args,  PyObject *kwds)
{
    char *name;
    int create, kind, value = -1;
    
    static char *kwlist[] = {"name", "create", "kind", "value", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "siii", kwlist,
                                     &name, &create, &kind, &value))
        return -1;
    
    self->name = malloc(strlen(name)+1);
    if (self->name == NULL) {
        PyErr_NoMemory();
        return -1;
    }
    
    memcpy(self->name, name, strlen(name)+1);
    
    self->kind = kind;
    self->count = 0;
    self->last_tid = 0;
    
    if (create) {
        if (IS_MUTEX(self))
            self->handle = CreateMutex(NULL, FALSE, name);
        else if (self->kind == BOUNDED_SEMAPHORE)
            self->handle = CreateSemaphore(NULL, value, value, name);
        else
            self->handle = CreateSemaphore(NULL, value, 0x7FFFFFFF, name);
        
        if (GetLastError() == ERROR_ALREADY_EXISTS) {
            CloseHandle(self->handle);
            PyErr_SetFromWindowsErr(0);
        }
    } else {
        if (IS_MUTEX(self))
            self->handle = OpenMutex(MUTEX_ALL_ACCESS, FALSE, name);
        else
            self->handle = OpenSemaphore(SEMAPHORE_ALL_ACCESS, FALSE, name);
    }
    
    if (self->handle == NULL) {
        PyErr_SetFromWindowsErr(0);
        return -1;
    }
    
    return 0;
}

static PyObject *
sync_close(Blocker *self)
{
    int res;
    
    if (self->handle != NULL) {
        res = CloseHandle(self->handle);
        self->handle = NULL;
        if (!res)
            return PyErr_SetFromWindowsErr(0);
    }
    
    Py_RETURN_NONE;
}

static void
sync_dealloc(Blocker* self)
{
    PyObject *ignore;

    ignore = sync_close(self);
    Py_XDECREF(ignore);
    free(self->name);
    self->name = NULL;
    self->ob_type->tp_free((PyObject*)self);
}

static int
wait_and_check_signals(HANDLE h, DWORD timeout)
{
    DWORD delta, res;

    if (timeout == 0)
        return WaitForSingleObject(h, 0);

    do {
        delta = timeout > 1000 ? 1000 : timeout;
        Py_BEGIN_ALLOW_THREADS
        res = WaitForSingleObject(h, delta);
        Py_END_ALLOW_THREADS
        if (res != WAIT_TIMEOUT)
            return res;
        if (PyErr_CheckSignals())
            return -2;
        if (timeout != INFINITE)
            timeout -= delta;
    } while (timeout > 0);

    return WAIT_TIMEOUT;
}

static PyObject *
_acquire(Blocker *self, DWORD timeout)
{
    DWORD res;

    if (self->handle == NULL) {
        PyErr_SetString(PyExc_AssertionError, "semaphore/mutex is closed");
        return NULL;
    }
    
    if (self->kind == MUTEX && self->count > 0 
        && self->last_tid == PyThread_get_thread_ident()) {
        PyErr_SetString(PyExc_AssertionError, "attempt to acquire an owned "
                        "non-recusive lock");
        return NULL;
    }
    
    res = wait_and_check_signals(self->handle, timeout);
        
    switch (res) {
    case WAIT_TIMEOUT:
        Py_RETURN_FALSE;
    case WAIT_OBJECT_0:
    case WAIT_ABANDONED:
        self->last_tid = PyThread_get_thread_ident();
        ++self->count;
        Py_RETURN_TRUE;
    case WAIT_FAILED:
        return PyErr_SetFromWindowsErr(0);
    case -2:
        return NULL;
    default:
        PyErr_SetString(PyExc_AssertionError, 
                        "WaitForSingleObject gave unrecognized value");
        return NULL;
    }
}

static PyObject *
sync_acquire(Blocker *self, PyObject *args)
{
    int blocking = 1;

    if (!PyArg_ParseTuple(args, "|i", &blocking))
        return NULL;

    if (blocking)
        return _acquire(self, INFINITE);
    else
        return _acquire(self, 0);
}

static PyObject *
sync_acquire_timeout(Blocker *self, PyObject *args)
{
    double timeout = 0.0;
    
    if (!PyArg_ParseTuple(args, "|d", &timeout))
        return NULL;

    if (timeout < 0.0)
        timeout = 0.0;

    return _acquire(self, (DWORD)(timeout * 1000));
}

static PyObject *
sync_release(Blocker *self)
{
    int res;

    if (self->handle == NULL) {
        PyErr_SetString(PyExc_AssertionError, "semaphore/mutex is closed");
        return NULL;
    }
    
    if (IS_MUTEX(self))
        res = ReleaseMutex(self->handle);
    else
        res = ReleaseSemaphore(self->handle, 1, NULL);
    
    if (res == 0) {
        if (GetLastError() == ERROR_TOO_MANY_POSTS) {
            PyErr_SetString(PyExc_ValueError, 
                            "Semaphore released too many times");
            return NULL;
        } else {
            return PyErr_SetFromWindowsErr(0);
        }
    }
    
    --self->count;
    Py_RETURN_NONE;
}

static PyObject *
sync_getvalue(Blocker *self)
{
    long previous;

    if (self->handle == NULL) {
        PyErr_SetString(PyExc_AssertionError, "semaphore/mutex is closed");
        return NULL;
    }
    
    if (IS_MUTEX(self)) {
        if (self->count > 0)
            return Py_BuildValue("i", 0);

        switch (WaitForSingleObject(self->handle, 0)) {
        case WAIT_OBJECT_0:
        case WAIT_ABANDONED:
            if (ReleaseMutex(self->handle))
                return Py_BuildValue("i", 1);
            else
                return PyErr_SetFromWindowsErr(0);
        case WAIT_TIMEOUT:
            return Py_BuildValue("i", 0);
        case WAIT_FAILED:
            return PyErr_SetFromWindowsErr(0);
        }
    } else {
        switch (WaitForSingleObject(self->handle, 0)) {
        case WAIT_OBJECT_0:
            if (ReleaseSemaphore(self->handle, 1, &previous))
                return Py_BuildValue("i", previous+1);
            else
                return PyErr_SetFromWindowsErr(0);
        case WAIT_TIMEOUT:
            return Py_BuildValue("i", 0);
        case WAIT_FAILED:
            return PyErr_SetFromWindowsErr(0);
        }
    }
    
    PyErr_SetString(PyExc_AssertionError, "unexpected value");
    return NULL;
}

static PyObject *
sync_ismine(Blocker *self)
{
    int res = FALSE;

    if (self->handle == NULL) {
        PyErr_SetString(PyExc_AssertionError, "semaphore/mutex is closed");
        return NULL;
    }

    if (!IS_MUTEX(self)) {
        PyErr_SetString(PyExc_NotImplementedError, "not a mutex");
        return NULL;
    }
    
    res = self->count > 0 && self->last_tid == PyThread_get_thread_ident();
    return Py_BuildValue("i", res);
}

static PyObject *
sync_count(Blocker *self)
{
    if (self->handle == NULL) {
        PyErr_SetString(PyExc_AssertionError, "semaphore/mutex is closed");
        return NULL;
    }
    
    return Py_BuildValue("i", self->count);
}


static PyMethodDef sync_methods[] = {
    {"acquire", (PyCFunction)sync_acquire, METH_VARARGS,
     "acquire the semaphore/mutex"},
    {"release", (PyCFunction)sync_release, METH_NOARGS, 
     "release the semaphore/mutex"},
    {"acquire_timeout", (PyCFunction)sync_acquire_timeout, METH_VARARGS,
     "acquire the semaphore/mutex using a timeout"},
    {"_count", (PyCFunction)sync_count, METH_NOARGS, 
     "number of `acquire()`s minus number of `release()`s for this process"},
    {"_ismine", (PyCFunction)sync_ismine, METH_NOARGS, 
     "whether the mutex is owned by this thread"},
    {"_getvalue", (PyCFunction)sync_getvalue, METH_NOARGS, 
     "get the value of the semaphore"},
    {"_close", (PyCFunction)sync_close, METH_NOARGS, 
     "close the semaphore/mutex"},
    {NULL}
};


#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif


PyTypeObject BlockerType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /* ob_size*/
    "_semaphore.Blocker",      /* tp_name*/
    sizeof(Blocker),           /* tp_basicsize*/
    0,                         /* tp_itemsize*/
    (destructor)sync_dealloc, 
                               /* tp_dealloc*/
    0,                         /* tp_print*/
    0,                         /* tp_getattr*/
    0,                         /* tp_setattr*/
    0,                         /* tp_compare*/
    0,                         /* tp_repr*/
    0,                         /* tp_as_number*/
    0,                         /* tp_as_sequence*/
    0,                         /* tp_as_mapping*/
    0,                         /* tp_hash */
    0,                         /* tp_call*/
    0,                         /* tp_str*/
    0,                         /* tp_getattro*/
    0,                         /* tp_setattro*/
    0,                         /* tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, 
                               /* tp_flags*/
    "Semaphore/Mutex type",    /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    sync_methods,              /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)sync_init,       /* tp_init */
    0,                         /* tp_alloc */
    (newfunc)sync_new,         /* tp_new */
};
