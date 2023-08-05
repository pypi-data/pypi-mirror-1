/*
 * Windows version of extension module used by `processing` package
 *
 * win_processing.c
 *
 * Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
 */

#include "processing_defs.h"
#include "processing.h"

extern PyTypeObject BlockerType;
extern PyTypeObject SocketConnectionType;
extern PyTypeObject QueueType;

PyObject *dumpsFunction, *loadsFunction, *Empty, *Full, *BufferTooShort;

int
calc_deadline(double timeout, struct timespec *deadline)
{
    struct timeval now;
    long sec, nsec;

    if (gettimeofday(&now, NULL) < 0)
        return -1;

    sec = (long) trunc(timeout);
    nsec = (long) (1e9 * (timeout - sec));
    
    deadline->tv_sec = now.tv_sec + sec;
    deadline->tv_nsec = now.tv_usec * 1000 + nsec;
    
    deadline->tv_sec += (deadline->tv_nsec / 1000000000);
    deadline->tv_nsec %= 1000000000;
    
    return 0;
}

#if !NO_SENDFD

/*
 * Functions for transferring file descriptors between processes.
 * Reimplements some of the functionality of the `fdcred`
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

#endif /* !NO_SENDFD */

static PyMethodDef module_methods[] = {
#if !NO_SENDFD
    {"sendfd", processing_sendfd, METH_VARARGS, 
     "sendfd(sockfd, fd) -> None: send file descriptor given by fd over\n"
     "the unix domain socket whose file decriptor is sockfd"},
    
    {"recvfd", processing_recvfd, METH_VARARGS, 
     "recvfd(sockfd) -> fd: returns a file descriptor over\n"
     "a unix domain socket whose file decriptor is sockfd"},
#endif
    {"rwbuffer", processing_rwbuffer, METH_VARARGS,
     "rwbuffer(object [, offset[, size]]) -> read-write buffer"},

    {"address_of_buffer", processing_address_of_buffer, METH_O,
     "address_of_buffer(obj) -> (address, size)"},

    {NULL, NULL, 0, NULL}
};

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
     * Add exception to module
     */
    
    BufferTooShort = PyErr_NewException("_processing.BufferToShort", 
                                        NULL, NULL);
    Py_INCREF(BufferTooShort);
    PyModule_AddObject(m, "BufferTooShort", BufferTooShort);
    
    /*
     * Add type objects to module
     */

    if (PyType_Ready(&SocketConnectionType) < 0)
        return;
    Py_INCREF(&SocketConnectionType);
    PyModule_AddObject(m, "Connection", (PyObject*)&SocketConnectionType);

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
