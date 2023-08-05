/*
 * Windows version of extension module used by `processing` package
 *
 * win_processing.c
 *
 * Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
 */

#include "Python.h"

#ifndef Py_RETURN_NONE
#define Py_RETURN_NONE return Py_INCREF(Py_None), Py_None
#define Py_RETURN_TRUE return Py_INCREF(Py_True), Py_True
#define Py_RETURN_FALSE return Py_INCREF(Py_False), Py_False
#endif

extern PyTypeObject BlockerType;
extern PyTypeObject SocketConnectionType;
extern PyTypeObject QueueType;

PyObject *dumpsFunction, *loadsFunction, *Empty, *Full;


#if USE_SENDFD

/*
 * Functions for transferring file descriptors between processes.
 * Reimpliments some of the functionality of the `fdcred`
 * module at `http://www.mca-ltd.com/resources/fdcred_1.tgz`.
 */

#include <sys/socket.h>

static int
sendfd(int conn, int fd)
{
    char dummy_char;
    char buf[CMSG_SPACE(sizeof(int))];
    struct msghdr msg = {0};
    struct iovec dummy_iov;
    struct cmsghdr *cmsg;
    
    dummy_iov.iov_base = &dummy_char;
    dummy_iov.iov_len = 1;
    msg.msg_control = buf;
    msg.msg_controllen = sizeof(buf);
    msg.msg_iov = &dummy_iov;
    msg.msg_iovlen = 1;
    cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));
    msg.msg_controllen = cmsg->cmsg_len;

    *(int*)CMSG_DATA(cmsg) = fd;
    return sendmsg(conn, &msg, 0);
}

static int
recvfd(int conn, int *fd)
{
    int result;
    char dummy_char;
    char buf[CMSG_SPACE(sizeof(int))];
    struct msghdr msg = {0};
    struct iovec dummy_iov;
    struct cmsghdr *cmsg;
    
    dummy_iov.iov_base = &dummy_char;
    dummy_iov.iov_len = 1;
    msg.msg_control = buf;
    msg.msg_controllen = sizeof(buf);
    msg.msg_iov = &dummy_iov;
    msg.msg_iovlen = 1;
    cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));
    msg.msg_controllen = cmsg->cmsg_len;

    result = recvmsg(conn, &msg, 0);
    *fd = *(int*)CMSG_DATA(cmsg);
    return result;
}

static PyObject *
processing_sendfd(PyObject *self, PyObject *args)
{
    int conn, fd;

    if (!PyArg_ParseTuple(args, "ii", &conn, &fd))
        return NULL;
    if (sendfd(conn, fd) < 0)
        return PyErr_SetFromErrno(PyExc_OSError);
    Py_RETURN_NONE;
}

static PyObject *
processing_recvfd(PyObject *self, PyObject *args)
{
    int conn, fd;
    
    if (!PyArg_ParseTuple(args, "i", &conn))
        return NULL;
    if (recvfd(conn, &fd) < 0)
        return PyErr_SetFromErrno(PyExc_OSError);
    return Py_BuildValue("i", fd);
}

static PyMethodDef module_methods[] = {
    {"sendfd", processing_sendfd, METH_VARARGS, 
     "sendfd(sockfd, fd): send file descriptor given by fd over\n"
     "the unix domain socket whose file decriptor is sockfd"},
    
    {"recvfd", processing_recvfd, METH_VARARGS, 
     "recvfd(sockfd): returns a file descriptor over\n"
     "a unix domain socket whose file decriptor is sockfd"},
    
    {NULL, NULL, 0, NULL}
};

#else /* USE_SENDFD */

static PyMethodDef module_methods[] = {
    {NULL, NULL, 0, NULL}
};

#endif /* USE_SENDFD */


PyMODINIT_FUNC
init_processing(void)
{
    PyObject *m, *other_module;
    
    /*
     * Initialize module
     */

    m = Py_InitModule("_processing", module_methods);

    /*
     * Get copy of `cPickle.dumps` and `cPickle.loads`
     */

    other_module = PyImport_ImportModule("cPickle");
    if (!other_module)
        return;
    dumpsFunction = PyObject_GetAttrString(other_module, "dumps");
    loadsFunction = PyObject_GetAttrString(other_module, "loads");
    Py_XDECREF(other_module);

    /*
     * Add type objects to module
     */

    if (PyType_Ready(&SocketConnectionType) < 0)
        return;
    Py_INCREF(&SocketConnectionType);
    PyModule_AddObject(m,"SocketConnection",(PyObject*)&SocketConnectionType);

#if USE_POSIX_SEMAPHORE
    if (PyType_Ready(&BlockerType) < 0)
        return;
    Py_INCREF(&BlockerType);
    PyModule_AddObject(m, "Blocker", (PyObject*)&BlockerType);
#endif

#if USE_POSIX_QUEUE
    other_module = PyImport_ImportModule("Queue");
    Empty = PyObject_GetAttrString(other_module, "Empty");
    Full = PyObject_GetAttrString(other_module, "Full");
    Py_XDECREF(other_module);

    if (PyType_Ready(&QueueType) < 0)
        return;
    Py_INCREF(&QueueType);
    PyModule_AddObject(m, "Queue", (PyObject*)&QueueType);
#endif
}
