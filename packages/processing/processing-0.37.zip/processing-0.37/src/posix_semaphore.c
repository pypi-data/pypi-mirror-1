/*
 * A type which wraps a posix named semaphore
 *
 * win_processing.c
 *
 * Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
 */

#include "Python.h"
#include "pythread.h"

#ifndef Py_RETURN_NONE
#define Py_RETURN_NONE return Py_INCREF(Py_None), Py_None
#define Py_RETURN_TRUE return Py_INCREF(Py_True), Py_True
#define Py_RETURN_FALSE return Py_INCREF(Py_False), Py_False
#endif

#include <semaphore.h>
#include <pthread.h>
#include <fcntl.h>
#include <time.h>
#include <math.h>

#if NO_SEM_UNLINK
int sem_unlink(char *name) { return 0; }
#endif

extern int calc_deadline(double timeout, struct timespec *deadline);

enum { MUTEX, RECURSIVE_MUTEX, SEMAPHORE, BOUNDED_SEMAPHORE };

#define IS_MUTEX(self) ((self)->kind < SEMAPHORE)

typedef struct {
    PyObject_HEAD
    char *name;
    sem_t *handle;
    int maxvalue;
    int kind;
    int count;
    pid_t last_pid;
    long last_tid;
} Blocker;

PyTypeObject BlockerType;


static int
ismine(Blocker *self)
{
    if (self->last_pid == getpid()) {
        if (self->count > 0 && PyThread_get_thread_ident() == self->last_tid)
            return 1;
    } else {
        if (self->count != 0)    /* correction after fork */
            self->count = 0;
    }
    return 0;
}


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
    
    self->maxvalue = (kind == BOUNDED_SEMAPHORE ? value : -1);
    self->kind = kind;
    self->count = 0;
    self->last_pid = 0;
    self->last_tid = 0;
    
    if (create)
        self->handle = sem_open(name, O_CREAT | O_EXCL, 0600, value);
    else
        self->handle = sem_open(name, 0);
    
    if (self->handle == SEM_FAILED) {
        PyErr_SetFromErrno(PyExc_OSError);
        return -1;
    }
    
    return 0;
}

static PyObject *
sync_close(Blocker *self)
{
    int res;
    
    if (self->handle != NULL) {
        if (IS_MUTEX(self) && self->last_pid == getpid() && self->count > 0) {
            self->count = 0;
            sem_post(self->handle);
        }
        res = sem_close(self->handle);
        self->handle = NULL;
        if (res < 0)
            return PyErr_SetFromErrno(PyExc_OSError);
    }
    
    Py_RETURN_NONE;
}

static PyObject *
sync_unlink(Blocker *self)
{
    int res;
    
    res = sem_unlink(self->name);
    if (res < 0)
        return PyErr_SetFromErrno(PyExc_OSError);
    
    Py_RETURN_NONE;
}

static void
sync_dealloc(Blocker* self)
{
    Py_XDECREF(sync_close(self));
    free(self->name);
    self->name = NULL;
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
sync_acquire(Blocker *self, PyObject *args)
{
    int blocking = 1, mine, res;
    
    if (!PyArg_ParseTuple(args, "|i", &blocking))
        return NULL;
    
    if (self->handle == NULL) {
        PyErr_SetString(PyExc_AssertionError, "semaphore is closed");
        return NULL;
    }    

    mine = ismine(self);

    if (self->kind == MUTEX && mine) {
        PyErr_SetString(PyExc_AssertionError, "attempt to acquire a "
                        "non-recusive lock already owned by thread");
        return NULL;
    }
    
    if (self->kind == RECURSIVE_MUTEX && mine) {
        ++self->count;
        Py_RETURN_TRUE;
    }
    
    do {
        Py_BEGIN_ALLOW_THREADS
        if (blocking)
            res = sem_wait(self->handle);
        else
            res = sem_trywait(self->handle);
        Py_END_ALLOW_THREADS
    } while (res < 0 && errno == EINTR && !PyErr_CheckSignals());

    if (res < 0) {
        if (errno == EAGAIN)
            Py_RETURN_FALSE;
        else if (errno == EINTR)
            return NULL;
        else
            return PyErr_SetFromErrno(PyExc_OSError);
    }
    
    ++self->count;
    self->last_pid = getpid();
    self->last_tid = PyThread_get_thread_ident();

    Py_RETURN_TRUE;
}

static PyObject *
sync_release(Blocker *self)
{
    int sval, res, mine;

    if (self->handle == NULL) {
        PyErr_SetString(PyExc_AssertionError, "semaphore is closed");
        return NULL;
    }
    
    mine = ismine(self);

    if (IS_MUTEX(self)) {
        if (!mine) {
            PyErr_SetString(PyExc_AssertionError, "attempt to release a "
                            "lock which is not owned by thread");
            return NULL;
        }
        if (self->count > 1) {     /* a recursively acquired mutex */
            --self->count;
            Py_RETURN_NONE;
        }
    } else if (self->kind == BOUNDED_SEMAPHORE) {
        if (sem_getvalue(self->handle, &sval) < 0)
            return PyErr_SetFromErrno(PyExc_OSError);
        if (sval >= self->maxvalue) {
            PyErr_SetString(PyExc_ValueError, 
                            "Semaphore released too many times");
            return NULL;
        }
    }
    
    res = sem_post(self->handle);
    if (res < 0)
        return PyErr_SetFromErrno(PyExc_OSError);
    
    --self->count;
    Py_RETURN_NONE;
}

static PyObject *
sync_acquire_timeout(Blocker *self, PyObject *args)
{
    double timeout = 0.0;
    int res, mine;
    
    if (!PyArg_ParseTuple(args, "d", &timeout))
        return NULL;

    if (self->handle == NULL) {
        PyErr_SetString(PyExc_AssertionError, "semaphore is closed");
        return NULL;
    }
    
    mine = ismine(self);
    
    if (self->kind == MUTEX && mine) {
        PyErr_SetString(PyExc_AssertionError, "attempt to acquire a "
                        "non-recusive lock owned by thread");
        return NULL;
    }
    
    if (self->kind == RECURSIVE_MUTEX && mine) {
        ++self->count;
        Py_RETURN_TRUE;
    }
    
    if (timeout < 0.0)
        timeout = 0.0;

#if NO_SEM_TIMED

    res = sem_trywait(self->handle);
    if (res < 0 && errno == EAGAIN) {
        struct timeval now, deadline;
        unsigned long delay, difference;
        
        /* get current time */
        if (gettimeofday(&now, NULL) < 0)
            return NULL;

        /* calculate when we should be prepared to wait until */
        difference = (unsigned long)(timeout * 1000000);
        deadline.tv_sec = now.tv_sec + difference / 1000000;
        deadline.tv_usec = now.tv_usec + difference % 1000000;
        if (deadline.tv_usec >= 1000000) {
            deadline.tv_sec++;
            deadline.tv_usec %= 1000000;
        }
        
        for (delay = 0 ; ; delay += 1000) {
            /* poll */
            res = sem_trywait(self->handle);
            if (res < 0 && errno != EAGAIN)
                break;
            
            /* get current time */
            if (gettimeofday(&now, NULL) < 0)
                return NULL;
            
            /* check for timeout */
            if (deadline.tv_sec < now.tv_sec || 
                (deadline.tv_sec == now.tv_sec && 
                 deadline.tv_usec <= now.tv_usec))
                break;
            
            /* calculate how much time is left */
            difference = (deadline.tv_sec - now.tv_sec)*1000000 + 
                (deadline.tv_usec - now.tv_usec);
            
            /* check delay not too long -- maximum is 20 msecs */
            if (delay > 20000)
                delay = 20000;
            if (delay > difference)
                delay = difference;
            
            /* sleep */
            usleep(delay);
            if (PyErr_CheckSignals())
                break;
        }
    }

#else

    {
        struct timespec deadline;

        if (calc_deadline(timeout, &deadline) < 0)
            return PyErr_SetFromErrno(PyExc_OSError);

        do {
            Py_BEGIN_ALLOW_THREADS
            res = sem_timedwait(self->handle, &deadline);
            Py_END_ALLOW_THREADS
        } while (res < 0 && errno == EINTR && !PyErr_CheckSignals());
    }

#endif /* NO_SEM_TIMED */    

    if (res < 0) {
        if (errno == EAGAIN || errno == ETIMEDOUT)
            Py_RETURN_FALSE;
        else if (errno == EINTR)
            return NULL;
        else
            return PyErr_SetFromErrno(PyExc_OSError);
    }

    ++self->count;
    self->last_pid = getpid();
    self->last_tid = PyThread_get_thread_ident();

    Py_RETURN_TRUE;
}

static PyObject *
sync_count(Blocker *self)
{
    if (self->handle == NULL) {
        PyErr_SetString(PyExc_AssertionError, "semaphore is closed");
        return NULL;
    }
    
    if (self->last_pid != getpid() && self->count > 0)
        self->count = 0;            /* correction after fork */

    return Py_BuildValue("i", self->count);
}

static PyObject *
sync_getvalue(Blocker *self)
{
    int sval;
    
    if (self->handle == NULL) {
        PyErr_SetString(PyExc_AssertionError, "semaphore/mutex is closed");
        return NULL;
    }
    
    if (sem_getvalue(self->handle, &sval) < 0)
        return PyErr_SetFromErrno(PyExc_OSError);

    return Py_BuildValue("i", sval);
}

static PyObject *
sync_ismine(Blocker *self)
{
    if (self->handle == NULL) {
        PyErr_SetString(PyExc_AssertionError, "semaphore/mutex is closed");
        return NULL;
    }

    if (!IS_MUTEX(self)) {
        PyErr_SetString(PyExc_AssertionError, "semaphores cannot be owned");
        return NULL;
    }
    
    if (ismine(self))
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}


static PyMethodDef sync_methods[] = {
    {"acquire", (PyCFunction)sync_acquire, METH_VARARGS,
     "acquire the semaphore/mutex"},
    {"release", (PyCFunction)sync_release, METH_NOARGS, 
     "release the semaphore/mutex"},
    {"acquire_timeout", (PyCFunction)sync_acquire_timeout, METH_VARARGS,
     "acquire the semaphore/mutex"},
    {"_close", (PyCFunction)sync_close, METH_NOARGS, 
     "close the semaphore/mutex"},
    {"_unlink", (PyCFunction)sync_unlink, METH_NOARGS, 
     "unlink the name of the semaphore/mutex"},
    {"_count", (PyCFunction)sync_count, METH_NOARGS, 
     "number of `acquire()`s minus number of `release()`s for this process"},
    {"_ismine", (PyCFunction)sync_ismine, METH_NOARGS, 
     "whether the mutex is owned by this thread"},
    {"_getvalue", (PyCFunction)sync_getvalue, METH_NOARGS, 
     "get the value of the semaphore"},
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
