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

#define WIN32_LEAN_AND_MEAN
#include <windows.h>

extern PyTypeObject BlockerType;
extern PyTypeObject PipeConnectionType;
extern PyTypeObject SocketConnectionType;

extern PyObject *socket_changefd(PyObject *self, PyObject *args);

PyObject *dumpsFunction, *loadsFunction, *BufferTooShort, *socketType;

/*
 * Definitions to create and manipulate pipe handles
 */

#define PIPE_BUFFER_SIZE 8192

static PyObject *
processing_createpipe(PyObject *self, PyObject *args)
{
    char *name;
    HANDLE pipe;
    DWORD timeout = NMPWAIT_WAIT_FOREVER;
    DWORD openmode = PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT;

    if ( !PyArg_ParseTuple( args, "s|i", &name, &timeout) )
        return NULL;
    
    Py_BEGIN_ALLOW_THREADS
    pipe = CreateNamedPipe(name, PIPE_ACCESS_DUPLEX, openmode, 
                           PIPE_UNLIMITED_INSTANCES, PIPE_BUFFER_SIZE, 
                           PIPE_BUFFER_SIZE, timeout, NULL);
    Py_END_ALLOW_THREADS
        
    if (pipe == INVALID_HANDLE_VALUE) {
        CloseHandle(pipe);
        PyErr_SetFromWindowsErr(0);
        return NULL;
    }

    if (!SetHandleInformation(pipe,HANDLE_FLAG_INHERIT,HANDLE_FLAG_INHERIT)) {
        CloseHandle(pipe);
        return PyErr_SetFromWindowsErr(0);
    }

    return Py_BuildValue("i", pipe);
}

static PyObject *
processing_connectpipe(PyObject *self, PyObject *args)
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
        PyErr_SetFromWindowsErr(0);
        return NULL;
    }

    if (!SetHandleInformation(pipe,HANDLE_FLAG_INHERIT,HANDLE_FLAG_INHERIT)) {
        CloseHandle(pipe);
        return PyErr_SetFromWindowsErr(0);
    }

    Py_RETURN_NONE;
}

static PyObject *
processing_waitpipe(PyObject *self, PyObject *args)
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
        PyErr_SetFromWindowsErr(0);
        return NULL;
    }

    Py_RETURN_NONE;
}    

static PyObject *
processing_createfile(PyObject *self, PyObject *args)
{
    char *name;
    HANDLE pipe;
    BOOL success;
    DWORD dwMode = PIPE_READMODE_MESSAGE; 

    if ( !PyArg_ParseTuple( args, "s", &name ) )
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    pipe = CreateFile(name, GENERIC_READ | GENERIC_WRITE, 
                       0, NULL, OPEN_EXISTING, 0, NULL);
    if (pipe == INVALID_HANDLE_VALUE)
        success = FALSE;
    else
        success = SetNamedPipeHandleState(pipe, &dwMode, NULL, NULL);
    Py_END_ALLOW_THREADS

    if (!success) {
        if (pipe != INVALID_HANDLE_VALUE)
            CloseHandle(pipe);
        PyErr_SetFromWindowsErr(0);
        return NULL;
    }

    if (!SetHandleInformation(pipe,HANDLE_FLAG_INHERIT,HANDLE_FLAG_INHERIT)) {
        CloseHandle(pipe);
        return PyErr_SetFromWindowsErr(0);
    }
    
    return Py_BuildValue("i", pipe);
}

static PyObject *
processing_CloseHandle(PyObject *self, PyObject *args)
{
    HANDLE pipe;
    
    if (!PyArg_ParseTuple(args, "i", &pipe))
        return NULL;
    if (!CloseHandle(pipe))
        return PyErr_SetFromWindowsErr(0);
    Py_RETURN_NONE;
}

/*
 * Miscellaneous functions
 */

static PyObject *
processing_InheritCtrlC(PyObject *self, PyObject *args)
{
    BOOL value;

    if (!PyArg_ParseTuple(args, "i", &value))
        return NULL;
    if (!SetConsoleCtrlHandler(NULL, !value))
        return PyErr_SetFromWindowsErr(0);
    Py_RETURN_NONE;
}

static PyObject *
processing_GenerateConsoleCtrlEvent(PyObject *self, PyObject *args)
{
    DWORD event, gid;

    if (!PyArg_ParseTuple(args, "ii", &event, &gid))
        return NULL;
    if (!GenerateConsoleCtrlEvent(event, gid))
        return PyErr_SetFromWindowsErr(0);
    Py_RETURN_NONE;
}

static PyObject *
processing_HandleFromPidHandle(PyObject *self, PyObject *args)
{
    DWORD pid;
    HANDLE handle, new_handle, process_handle;
    
    if (!PyArg_ParseTuple(args, "ii", &pid, &handle))
        return NULL;
    
    process_handle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if (!process_handle)
        return PyErr_SetFromWindowsErr(0);

    if (!DuplicateHandle(process_handle, handle, GetCurrentProcess(), 
                         &new_handle, 0, TRUE, DUPLICATE_SAME_ACCESS)) {
        CloseHandle(process_handle);
        return PyErr_SetFromWindowsErr(0);
    }

    CloseHandle(process_handle);
    return Py_BuildValue("i", new_handle);
}

static PyObject *
processing_TerminateProcess(PyObject *self, PyObject *args)
{
    UINT code;
    HANDLE handle;

    if (!PyArg_ParseTuple(args, "iI", &handle, &code))
        return NULL;
    
    if (!TerminateProcess(handle, code))
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

/*
 *
 */

static PyMethodDef module_methods[] = {
    {"InheritCtrlC", 
     (PyCFunction)processing_InheritCtrlC, METH_VARARGS, 
     "InheritCtrlC(value) -- whether to inherit Ctrl-C signals"},
    
    {"CloseHandle", 
     (PyCFunction)processing_CloseHandle, METH_VARARGS, 
     "CloseHandle(handle)"},
    
    {"GenerateConsoleCtrlEvent",
     (PyCFunction)processing_GenerateConsoleCtrlEvent, METH_VARARGS,  
     "GenerateConsoleCtrlEvent(event, gid)"},

    {"HandleFromPidHandle",
     (PyCFunction)processing_HandleFromPidHandle, METH_VARARGS,  
     "HandleFromPidHandle(pid, handle)"},

    {"TerminateProcess",
     (PyCFunction)processing_TerminateProcess, METH_VARARGS,  
     "TerminateProcess(handle, code)"},

    {"createpipe", (PyCFunction)processing_createpipe, METH_VARARGS, ""},

    {"connectpipe", (PyCFunction)processing_connectpipe, METH_VARARGS, ""},

    {"waitpipe", (PyCFunction)processing_waitpipe, METH_VARARGS, ""},

    {"createfile", (PyCFunction)processing_createfile, METH_VARARGS, ""},

    {"changefd", (PyCFunction)socket_changefd, METH_VARARGS, ""},

    {NULL}  /* Sentinel */
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
     * Get copy of `_socket.socket`
     */

    other_module = PyImport_ImportModule("_socket");
    if (!other_module)
        return;
    socketType = PyObject_GetAttrString(other_module, "socket");
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
    
    if (PyType_Ready(&PipeConnectionType) < 0)
        return;
    Py_INCREF(&PipeConnectionType);
    PyModule_AddObject(m,"PipeConnection",(PyObject*)&PipeConnectionType);

    if (PyType_Ready(&SocketConnectionType) < 0)
        return;
    Py_INCREF(&SocketConnectionType);
    PyModule_AddObject(m,"SocketConnection",(PyObject*)&SocketConnectionType);

    if (PyType_Ready(&BlockerType) < 0)
        return;
    Py_INCREF(&BlockerType);
    PyModule_AddObject(m, "Blocker", (PyObject*)&BlockerType);   
}
