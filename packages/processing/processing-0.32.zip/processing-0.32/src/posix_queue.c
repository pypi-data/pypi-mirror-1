#include "Python.h"
#include "structmember.h"

#ifndef Py_RETURN_NONE
#define Py_RETURN_NONE return Py_INCREF(Py_None), Py_None
#define Py_RETURN_TRUE return Py_INCREF(Py_True), Py_True
#define Py_RETURN_FALSE return Py_INCREF(Py_False), Py_False
#endif

#include <mqueue.h>
#include <fcntl.h>
#include <time.h>

typedef struct {
    PyObject_HEAD
    char *name;
    mqd_t queue;
    int msgsize;
    int maxmsg;
} Queue;

PyTypeObject QueueType;

extern PyObject *dumpsFunction, *loadsFunction, *Empty, *Full;

static PyObject *
queue_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Queue *self;
    
    self = (Queue*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->name = NULL;
    }
    
    return (PyObject*)self;
}

static int
queue_init(Queue *self, PyObject *args,  PyObject *kwds)
{
    char *name;
    int res, create = 1, maxmsg = 0, msgsize = 0;
    struct mq_attr attr;
    
    static char *kwlist[] = {"maxmsg", "msgsize", "name", "create", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "iisi", kwlist,
                                     &maxmsg, &msgsize, &name, &create))
        return -1;
    
    if ((self->name = malloc(strlen(name)+1)) == NULL) {
        PyErr_NoMemory();
        return -1;
    }

    if (maxmsg < 0 || msgsize < 0) {
        PyErr_SetString(PyExc_ValueError, 
                        "maxmsg and msgsize should not be negative");
        return -1;
    }
    
    memcpy(self->name, name, strlen(name)+1);
    
    if ((maxmsg && !msgsize) || (msgsize && !maxmsg)) {
        PyErr_SetString(PyExc_AssertionError, "either both maxmsg and msgsize "
                        "should be zero or neither should be");
        return -1;
    } else if (maxmsg || msgsize) {
        attr.mq_flags = 0;
        attr.mq_maxmsg = maxmsg;
        attr.mq_msgsize = msgsize;
        attr.mq_curmsgs = 0;
    }
    
    if (create) {
        if (maxmsg || msgsize)
            self->queue = mq_open(name, O_RDWR|O_CREAT|O_EXCL, 0600, &attr);
        else
            self->queue = mq_open(name, O_RDWR|O_CREAT|O_EXCL, 0600, NULL);
    } else {
        self->queue = mq_open(name, O_RDWR);
    }
    
    if (self->queue == -1) {
        if (errno == EINVAL && (maxmsg || msgsize)) {
            PyErr_SetString(PyExc_OSError, "invalid parameter:\n"
                "\tmaybe the requested queue size or the requested maxmimum\n"
                "\tmessage size was larger than system imposed limit");
        } else {
            PyErr_SetFromErrno(PyExc_OSError);
        }
        return -1;
    }
    
    res = mq_getattr(self->queue, &attr);
    if (res < 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return -1;
    }
    
    self->msgsize = attr.mq_msgsize;
    self->maxmsg = attr.mq_maxmsg;
    
    return 0;
}

static PyObject *
queue_close(Queue *self)
{
    int res;
    
    if (self->queue != -1) {
        res = mq_close(self->queue);
        self->queue = -1;
        if (res < 0)
            return PyErr_SetFromErrno(PyExc_OSError);
    }
    
    Py_RETURN_NONE;
}

static PyObject *
queue_unlink(Queue *self)
{
    int res;
    
    if (self->name != NULL) {
        res = mq_unlink(self->name);
        if (res < 0)
            return PyErr_SetFromErrno(PyExc_OSError);
    }
    
    Py_RETURN_NONE;
}

static void
queue_dealloc(Queue* self)
{
    Py_XDECREF(queue_close(self));
    free(self->name);
    self->name = NULL;
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
queue_empty(Queue *self)
{
    struct mq_attr attr;
    
    if (self->queue == -1) {
        PyErr_SetString(PyExc_AssertionError, "queue is closed");
        return NULL;
    }

    if (mq_getattr(self->queue, &attr) < 0)
        return PyErr_SetFromErrno(PyExc_OSError);
    
    if (attr.mq_curmsgs == 0)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static PyObject *
queue_full(Queue *self)
{
    struct mq_attr attr;
    
    if (self->queue == -1) {
        PyErr_SetString(PyExc_AssertionError, "queue is closed");
        return NULL;
    }

    if (mq_getattr(self->queue, &attr) < 0)
        return PyErr_SetFromErrno(PyExc_OSError);
    
    if (attr.mq_curmsgs == attr.mq_maxmsg)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static PyObject *
queue_qsize(Queue *self)
{
    struct mq_attr attr;
    
    if (self->queue == -1) {
        PyErr_SetString(PyExc_AssertionError, "queue is closed");
        return NULL;
    }

    if (mq_getattr(self->queue, &attr) < 0)
        return PyErr_SetFromErrno(PyExc_OSError);
    
    return Py_BuildValue("i", attr.mq_curmsgs);
}

static int
calc_deadline(PyObject *timeout_obj, struct timespec *deadline)
{
    int res;
    double timeout;
    long sec, nsec;
    
    timeout_obj = PyNumber_Float(timeout_obj);
    if (timeout_obj == NULL)
        return 0;

    timeout = PyFloat_AS_DOUBLE(timeout_obj);
    Py_DECREF(timeout_obj);
    
    res = clock_gettime(CLOCK_REALTIME, deadline);
    if (res < 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return 0;
    }
    
    sec = (long) trunc(timeout);
    nsec = (long) (1e9 * (timeout - sec));
    
    deadline->tv_sec += sec;
    deadline->tv_nsec += nsec;
    
    deadline->tv_sec += (deadline->tv_nsec / 1000000000);
    deadline->tv_nsec %= 1000000000;
    
    return 1;
}

static PyObject *
queue_put(Queue *self, PyObject *args, PyObject *kwds)
{
    int res, length, block = 1;
    char *string;
    unsigned priority = 1;
    PyObject *obj, *pickled_string = NULL, *timeout_obj = Py_None;
    struct timespec deadline;
    
    static char *kwlist[] = {"item", "block", "timeout", "priority", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|iOi", kwlist,
                                     &obj, &block, &timeout_obj, &priority))
        goto ERR;
    
    if (self->queue == -1) {
        PyErr_SetString(PyExc_AssertionError, "queue is closed");
        goto ERR;
    }
    
    pickled_string = PyObject_CallFunction(dumpsFunction, "Oi", obj, 2);
    if (!pickled_string)
        goto ERR;
    
    if (PyString_AsStringAndSize(pickled_string, &string, &length) != 0)
        goto ERR;
    
    if (length > self->msgsize) {
        PyErr_SetString(PyExc_ValueError, "pickled string too long");
        goto ERR;
    }
    
    if (!block || timeout_obj != Py_None) {
        if (!calc_deadline(timeout_obj, &deadline))
            goto ERR;        
        do {
            Py_BEGIN_ALLOW_THREADS
            res = mq_timedsend(self->queue, string, length, 0, &deadline);
            Py_END_ALLOW_THREADS
        } while (res < 0 && errno == EINTR && !PyErr_CheckSignals());
    } else {
        do {
            Py_BEGIN_ALLOW_THREADS
            res = mq_send(self->queue, string, length, 1);
            Py_END_ALLOW_THREADS
        } while (res < 0 && errno == EINTR && !PyErr_CheckSignals());
    }
    
    if (res < 0) {
        if (errno == ETIMEDOUT)
            PyErr_SetString(Full, "timed out");
        else if (errno != EINTR)
            PyErr_SetFromErrno(PyExc_OSError);
        goto ERR;
    }
    
    Py_XDECREF(pickled_string);
    Py_RETURN_NONE;
    
 ERR:
    Py_XDECREF(pickled_string);
    return NULL;
}

static PyObject *
queue_get(Queue *self, PyObject *args, PyObject *kwds)
{
    int bytes, block = 1;
    char *buffer;
    PyObject *result, *timeout_obj = Py_None;
    struct timespec deadline;

    static char *kwlist[] = {"block", "timeout", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|iO", kwlist,
                                     &block, &timeout_obj))
        return NULL;

    if (self->queue == -1) {
        PyErr_SetString(PyExc_AssertionError, "queue is closed");
        return NULL;
    }
    
    buffer = malloc(self->msgsize);
    if (buffer == NULL)
        return PyErr_NoMemory();
    
    if (!block || timeout_obj != Py_None) {
        if (!calc_deadline(timeout_obj, &deadline))
            goto ERR;
        do {
            Py_BEGIN_ALLOW_THREADS
            bytes = mq_timedreceive(self->queue, buffer, self->msgsize, 
                                    NULL, &deadline);
            Py_END_ALLOW_THREADS
        } while (bytes < 0 && errno == EINTR && !PyErr_CheckSignals());
    } else {
        do {
            Py_BEGIN_ALLOW_THREADS
            bytes = mq_receive(self->queue, buffer, self->msgsize, NULL);
            Py_END_ALLOW_THREADS
        } while (bytes < 0 && errno == EINTR && !PyErr_CheckSignals());
    }
    
    if (bytes < 0) {
        if (errno == ETIMEDOUT)
            PyErr_SetString(Empty, "timed out");
        else if (errno != EINTR)
            PyErr_SetFromErrno(PyExc_OSError);
        goto ERR;
    }
    
    result = PyObject_CallFunction(loadsFunction, "s#", buffer, bytes);
    free(buffer);
    return result;
    
 ERR:
    free(buffer);
    return NULL;
}

static PyObject *
queue_send(Queue *self, PyObject *args, PyObject *kwds)
{
    int res, length, block = 1;
    unsigned priority = 0;
    char *string;
    PyObject *pickled_string = NULL, *timeout_obj = Py_None;
    struct timespec deadline;
    
    static char *kwlist[] = {"message", "block", "timeout", "priority", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s#|iOI", kwlist,
                           &string, &length, &block, &timeout_obj, &priority))
        goto ERR;
    
    if (self->queue == -1) {
        PyErr_SetString(PyExc_AssertionError, "queue is closed");
        goto ERR;
    }
    
    if (length > self->msgsize) {
        PyErr_SetString(PyExc_ValueError, "pickled string too long");
        goto ERR;
    }
    
    if (!block || timeout_obj != Py_None) {
        if (!calc_deadline(timeout_obj, &deadline))
            goto ERR;        
        do {
            Py_BEGIN_ALLOW_THREADS
            res = mq_timedsend(self->queue, string, length, 
                               priority, &deadline);
            Py_END_ALLOW_THREADS
        } while (res < 0 && errno == EINTR && !PyErr_CheckSignals());
    } else {
        do {
            Py_BEGIN_ALLOW_THREADS
            res = mq_send(self->queue, string, length, priority);
            Py_END_ALLOW_THREADS
        } while (res < 0 && errno == EINTR && !PyErr_CheckSignals());
    }
    
    if (res < 0) {
        if (errno == ETIMEDOUT)
            PyErr_SetString(Full, "timed out");
        else if (errno != EINTR)
            PyErr_SetFromErrno(PyExc_OSError);
        goto ERR;
    }
    
    Py_XDECREF(pickled_string);
    Py_RETURN_NONE;
    
 ERR:
    Py_XDECREF(pickled_string);
    return NULL;
}

static PyObject *
queue_receive(Queue *self, PyObject *args, PyObject *kwds)
{
    int bytes, block = 1;
    unsigned priority;
    char *buffer;
    PyObject *result, *timeout_obj = Py_None;
    struct timespec deadline;

    static char *kwlist[] = {"block", "timeout", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|iO", kwlist,
                                     &block, &timeout_obj))
        return NULL;
    
    if (self->queue == -1) {
        PyErr_SetString(PyExc_AssertionError, "queue is closed");
        return NULL;
    }
    
    buffer = malloc(self->msgsize);
    if (buffer == NULL)
        return PyErr_NoMemory();
    
    if (!block || timeout_obj != Py_None) {
        if (!calc_deadline(timeout_obj, &deadline))
            goto ERR;
        do {
            Py_BEGIN_ALLOW_THREADS
            bytes = mq_timedreceive(self->queue, buffer, self->msgsize, 
                                    &priority, &deadline);
            Py_END_ALLOW_THREADS
        } while (bytes < 0 && errno == EINTR && !PyErr_CheckSignals());
    } else {
        do {
            Py_BEGIN_ALLOW_THREADS
            bytes = mq_receive(self->queue, buffer, self->msgsize, &priority);
            Py_END_ALLOW_THREADS
        } while (bytes < 0 && errno == EINTR && !PyErr_CheckSignals());
    }
    
    if (bytes < 0) {
        if (errno == ETIMEDOUT)
            PyErr_SetString(Empty, "timed out");
        else if (errno != EINTR)
            PyErr_SetFromErrno(PyExc_OSError);
        goto ERR;
    }
    
    result = Py_BuildValue("s#I", buffer, bytes, priority);
    free(buffer);
    return result;
    
 ERR:
    free(buffer);
    return NULL;
}

static PyMemberDef queue_members[] = {
    {"_maxmsg", T_INT, offsetof(Queue, maxmsg), 0,
     "maximum number of messages that can be in queue"},
    {"_msgsize", T_INT, offsetof(Queue, msgsize), 0,
     "maximum size of a message in bytes"},
    {"_name", T_STRING, offsetof(Queue, name), 0,
     "name of the queue"},
    {NULL}  /* Sentinel */
};

static PyMethodDef queue_methods[] = {
    {"_unlink", (PyCFunction)queue_unlink, METH_NOARGS, 
     "unlink the queue's name"},
    {"_close", (PyCFunction)queue_close, METH_NOARGS, 
     "close the queue's descriptor"},
    {"put", (PyCFunction)queue_put, METH_VARARGS | METH_KEYWORDS,
     "put object in queue"},
    {"get", (PyCFunction)queue_get, METH_VARARGS | METH_KEYWORDS, 
     "get object from queue"},
    {"_put_string", (PyCFunction)queue_send, METH_VARARGS | METH_KEYWORDS,
     "_put_string(msg, block=True, timeout=None, priority=0)\n"
     "puts a string message on the queue"},
    {"_get_string", (PyCFunction)queue_receive, METH_VARARGS | METH_KEYWORDS, 
     "_get_string(block=True, timeout=None)\n"
     "gets string message from queue, returning (priority, msg)"},
    {"empty", (PyCFunction)queue_empty, METH_NOARGS, 
     "whether queue is empty"},
    {"full", (PyCFunction)queue_full, METH_NOARGS, 
     "whether queue is full"},    
    {"qsize", (PyCFunction)queue_qsize, METH_NOARGS, 
     "number of messages in queue"},
    {NULL}
};

PyTypeObject QueueType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /* ob_size*/
    "_processing._Queue",      /* tp_name*/
    sizeof(Queue),             /* tp_basicsize*/
    0,                         /* tp_itemsize*/
    (destructor)queue_dealloc, 
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
    "Queue type",              /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    queue_methods,             /* tp_methods */
    queue_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)queue_init,      /* tp_init */
    0,                         /* tp_alloc */
    (newfunc)queue_new,        /* tp_new */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

