/*
 * Windows version of extension module used by `processing` package
 *
 * win_processing.c
 *
 * Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
 */

#include "processing_defs.h"
#include "processing.h"

#define WIN32_LEAN_AND_MEAN
#include <windows.h>


extern PyTypeObject BlockerType;
extern PyTypeObject PipeConnectionType;
extern PyTypeObject SocketConnectionType;

extern PyObject *socket_changefd(PyObject *self, PyObject *args);

PyObject *dumpsFunction, *loadsFunction, *BufferTooShort, *socketType;

/*
 * Win32 functions
 */

static PyObject *
win32_CloseHandle(PyObject *self, PyObject *args)
{
    HANDLE hObject;

    BOOL success;
    
    if (!PyArg_ParseTuple(args, "k", &hObject))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    success = CloseHandle(hObject); 
    Py_END_ALLOW_THREADS

    if (!success)
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

static PyObject *
win32_ConnectNamedPipe(PyObject *self, PyObject *args)
{
    HANDLE hNamedPipe;
    LPOVERLAPPED lpOverlapped;

    BOOL success;

    if (!PyArg_ParseTuple(args, "k" N_FMT, &hNamedPipe, &lpOverlapped))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    success = ConnectNamedPipe(hNamedPipe, lpOverlapped);
    Py_END_ALLOW_THREADS

    if (!success)
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

static PyObject *
win32_CreateFile(PyObject *self, PyObject *args)
{
    LPCTSTR lpFileName;
    DWORD dwDesiredAccess;
    DWORD dwShareMode;
    LPSECURITY_ATTRIBUTES lpSecurityAttributes;
    DWORD dwCreationDisposition;
    DWORD dwFlagsAndAttributes;
    HANDLE hTemplateFile;

    HANDLE handle;

    if (!PyArg_ParseTuple(args, "skk" N_FMT "kkk",
                          &lpFileName, &dwDesiredAccess, &dwShareMode, 
                          &lpSecurityAttributes, &dwCreationDisposition, 
                          &dwFlagsAndAttributes, &hTemplateFile))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    handle = CreateFile(lpFileName, dwDesiredAccess, dwShareMode, 
                      lpSecurityAttributes, dwCreationDisposition, 
                      dwFlagsAndAttributes, hTemplateFile);
    Py_END_ALLOW_THREADS

    if (handle == INVALID_HANDLE_VALUE)
        return PyErr_SetFromWindowsErr(0);
    
    return Py_BuildValue("k", handle);
}

static PyObject *
win32_CreateNamedPipe(PyObject *self, PyObject *args)
{
    LPCTSTR lpName;
    DWORD dwOpenMode;
    DWORD dwPipeMode;
    DWORD nMaxInstances;
    DWORD nOutBufferSize;
    DWORD nInBufferSize;
    DWORD nDefaultTimeOut;
    LPSECURITY_ATTRIBUTES lpSecurityAttributes;

    HANDLE handle;

    if (!PyArg_ParseTuple(args, "skkkkkk" N_FMT,
                          &lpName, &dwOpenMode, &dwPipeMode, &nMaxInstances, 
                          &nOutBufferSize, &nInBufferSize, &nDefaultTimeOut,
                          &lpSecurityAttributes))
        return NULL;
    
    Py_BEGIN_ALLOW_THREADS
    handle = CreateNamedPipe(lpName, dwOpenMode, dwPipeMode, nMaxInstances, 
                             nOutBufferSize, nInBufferSize, nDefaultTimeOut,
                             lpSecurityAttributes);
    Py_END_ALLOW_THREADS
        
    if (handle == INVALID_HANDLE_VALUE)
        return PyErr_SetFromWindowsErr(0);

    return Py_BuildValue("k", handle);
}

static PyObject *
win32_DuplicateHandle(PyObject *self, PyObject *args)
{
    HANDLE hSourceProcessHandle;
    HANDLE hSourceHandle;
    HANDLE hTargetProcessHandle;
    DWORD dwDesiredAccess;
    BOOL bInheritHandle;
    DWORD dwOptions;

    HANDLE handle;

    if (!PyArg_ParseTuple(args, "kkkkik", 
                          &hSourceProcessHandle, &hSourceHandle,
                          &hTargetProcessHandle, &dwDesiredAccess,
                          &bInheritHandle, &dwOptions))
        return NULL;

    if (!DuplicateHandle(hSourceProcessHandle, hSourceHandle,
                         hTargetProcessHandle, &handle,
                         dwDesiredAccess, bInheritHandle, dwOptions))
        return PyErr_SetFromWindowsErr(0);
    
    return Py_BuildValue("k", handle);
}

static PyObject *
win32_GenerateConsoleCtrlEvent(PyObject *self, PyObject *args)
{
    DWORD dwCtrlEvent;
    DWORD dwProcessGroupId;

    if (!PyArg_ParseTuple(args, "kk", &dwCtrlEvent, &dwProcessGroupId))
        return NULL;

    if (!GenerateConsoleCtrlEvent(dwCtrlEvent, dwProcessGroupId))
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

static PyObject *
win32_GetCurrentProcess(PyObject *self, PyObject *args)
{
    return Py_BuildValue("k", GetCurrentProcess());
}

static PyObject *
win32_OpenProcess(PyObject *self, PyObject *args)
{
    DWORD dwDesiredAccess;
    BOOL bInheritHandle;
    DWORD dwProcessId;

    HANDLE handle;

    if (!PyArg_ParseTuple(args, "kik", &dwDesiredAccess, &bInheritHandle,
                          &dwProcessId))
        return NULL;
    
    handle = OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId);    
    if (handle == NULL)
        return PyErr_SetFromWindowsErr(0);
    
    return Py_BuildValue("k", handle);
}

static PyObject *
win32_SetConsoleCtrlHandler(PyObject *self, PyObject *args)
{
    PHANDLER_ROUTINE HandlerRoutine;
    BOOL Add;

    if (!PyArg_ParseTuple(args, N_FMT "i", &HandlerRoutine, &Add))
        return NULL;
    
    if (!SetConsoleCtrlHandler(HandlerRoutine, Add))
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

static PyObject *
win32_SetHandleInformation(PyObject *self, PyObject *args)
{
    HANDLE hObject;
    DWORD dwMask;
    DWORD dwFlags;

    if (!PyArg_ParseTuple(args, "kkk", &hObject, &dwMask, &dwFlags))
        return NULL;
    
    if (!SetHandleInformation(hObject, dwMask, dwFlags))
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

static PyObject *
win32_SetNamedPipeHandleState(PyObject *self, PyObject *args)
{
    HANDLE hNamedPipe;
    DWORD dwMode;
    PyObject *ignore1, *ignore2;

    if (!PyArg_ParseTuple(args, "kkOO", 
                          &hNamedPipe, &dwMode, &ignore1, &ignore2))
        return NULL;

    if (ignore1 != Py_None || ignore2 != Py_None) {
        PyErr_SetString(PyExc_ValueError, "last two arguments must be None");
        return NULL;
    }
    
    if (!SetNamedPipeHandleState(hNamedPipe, &dwMode, NULL, NULL))
        return PyErr_SetFromWindowsErr(0);
    
    Py_RETURN_NONE;
}

static PyObject *
win32_TerminateProcess(PyObject *self, PyObject *args)
{
    HANDLE hProcess;
    UINT uExitCode;

    if (!PyArg_ParseTuple(args, "kI", &hProcess, &uExitCode))
        return NULL;
    
    if (!TerminateProcess(hProcess, uExitCode))
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

static PyObject *
win32_WaitNamedPipe(PyObject *self, PyObject *args)
{
    LPCTSTR lpNamedPipeName;
    DWORD nTimeOut;

    BOOL success;

    if (!PyArg_ParseTuple(args, "sk", &lpNamedPipeName, &nTimeOut))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    success = WaitNamedPipe(lpNamedPipeName, nTimeOut);
    Py_END_ALLOW_THREADS

    if (!success)
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}    

/*
 *
 */

#define WIN32_FUNCTION(func) \
    {#func, (PyCFunction)win32_ ## func, METH_VARARGS, ""}

#define WIN32_CONSTANT(fmt, con) \
    PyModule_AddObject(m, #con, Py_BuildValue(fmt, con))

static PyMethodDef module_methods[] = {
    {"changefd", (PyCFunction)socket_changefd, METH_VARARGS, ""},
    {"rwbuffer", processing_rwbuffer, METH_VARARGS, ""},
    {"address_of_buffer", processing_address_of_buffer, METH_O, ""},
    WIN32_FUNCTION(CloseHandle),
    WIN32_FUNCTION(ConnectNamedPipe),
    WIN32_FUNCTION(CreateFile),
    WIN32_FUNCTION(CreateNamedPipe),
    WIN32_FUNCTION(DuplicateHandle),
    WIN32_FUNCTION(GenerateConsoleCtrlEvent),
    WIN32_FUNCTION(GetCurrentProcess),
    WIN32_FUNCTION(OpenProcess),
    WIN32_FUNCTION(SetConsoleCtrlHandler),
    WIN32_FUNCTION(SetHandleInformation),
    WIN32_FUNCTION(SetNamedPipeHandleState),
    WIN32_FUNCTION(TerminateProcess),
    WIN32_FUNCTION(WaitNamedPipe),
    {NULL, NULL}
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
     * Add win32 constants
     */

    WIN32_CONSTANT("k", DUPLICATE_SAME_ACCESS);
    WIN32_CONSTANT("k", ERROR_PIPE_BUSY);
    WIN32_CONSTANT("k", ERROR_PIPE_CONNECTED);
    WIN32_CONSTANT("k", ERROR_SEM_TIMEOUT);
    WIN32_CONSTANT("k", GENERIC_READ);
    WIN32_CONSTANT("k", GENERIC_WRITE);
    WIN32_CONSTANT("k", HANDLE_FLAG_INHERIT);
    WIN32_CONSTANT("k", NMPWAIT_WAIT_FOREVER);
    WIN32_CONSTANT("k", OPEN_EXISTING);
    WIN32_CONSTANT("k", PIPE_ACCESS_DUPLEX);
    WIN32_CONSTANT("k", PIPE_ACCESS_INBOUND);
    WIN32_CONSTANT("k", PIPE_ACCESS_OUTBOUND);
    WIN32_CONSTANT("k", PIPE_READMODE_MESSAGE);
    WIN32_CONSTANT("k", PIPE_TYPE_MESSAGE);
    WIN32_CONSTANT("k", PIPE_UNLIMITED_INSTANCES);
    WIN32_CONSTANT("k", PIPE_WAIT);
    WIN32_CONSTANT("k", PROCESS_ALL_ACCESS);
    WIN32_CONSTANT("k", NULL);

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
    if (!BufferTooShort)
        return;
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
    PyModule_AddObject(m,"Connection",(PyObject*)&SocketConnectionType);

    if (PyType_Ready(&BlockerType) < 0)
        return;
    Py_INCREF(&BlockerType);
    PyModule_AddObject(m, "Blocker", (PyObject*)&BlockerType);   
}
