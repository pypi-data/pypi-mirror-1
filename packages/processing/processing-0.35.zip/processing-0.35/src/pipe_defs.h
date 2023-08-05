/*
 * Definitions used by `connection.h`
 *
 * pipes_def.h
 *
 * Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
 */

#ifndef _PIPE_CONNECTION_H
#define _PIPE_CONNECTION_H

#define WIN32_LEAN_AND_MEAN
#include <windows.h>

typedef HANDLE _HANDLE;
typedef unsigned uint32_t;

#define INVALID_HANDLE NULL

static _HANDLE 
_duplicate(_HANDLE h)
{
    HANDLE dup_h;
    BOOL success = DuplicateHandle(
        GetCurrentProcess(), (HANDLE)h, GetCurrentProcess(), 
        &dup_h, 0, FALSE, DUPLICATE_SAME_ACCESS
        );
    return success ? (_HANDLE)dup_h : INVALID_HANDLE;
}

#define _close(h) CloseHandle(h)

/*
 * Error values
 */

#define SUCCESS (0)
#define STANDARD_ERROR (-1)
#define MEMORY_ERROR (-2)
#define ALREADY_SET_ERROR (-3)

static PyObject *
SetExcFromNumber(int num)
{
    switch (num) {
    case STANDARD_ERROR: 
        PyErr_SetFromWindowsErr(0);
        break;
    case MEMORY_ERROR:
        PyErr_NoMemory();
        break;
    case ALREADY_SET_ERROR:
        break;
    default:
        PyErr_SetString(PyExc_AssertionError, "unknown error number");
    }
    return NULL;
}

/*
 * Send string to the pipe; assumes in message oriented mode
 */

static int
send_string(_HANDLE pipe, char *string, size_t length)
{
    size_t amount_written;

    if (!WriteFile(pipe, string, length, &amount_written, NULL))
        return STANDARD_ERROR;
    assert(length == amount_written);
    return SUCCESS;
}

/*
 * Attempts to read into buffer, or if it is too small into *newbuffer.
 *
 * Returns number of bytes read.  Assumes in message oriented mode.
 */

static int
recv_string(_HANDLE pipe, char *buffer, size_t buflength, char **newbuffer)
{
    DWORD left, length, full_length;
    
    *newbuffer = NULL;
    
    if (ReadFile(pipe, buffer, buflength, &length, NULL)) {
        return length;
    } else if (GetLastError() != ERROR_MORE_DATA) {
        return STANDARD_ERROR;
    }
    
    if (!PeekNamedPipe(pipe, NULL, 0, NULL, NULL, &left))
        return STANDARD_ERROR;

    full_length = length + left;    
    assert(full_length > 0);

    *newbuffer = malloc(full_length);
    if (*newbuffer == NULL)
        return MEMORY_ERROR;
    
    memcpy(*newbuffer, buffer, length);

    if (ReadFile(pipe, *newbuffer+length, left, &length, NULL)) {
        return full_length;
    } else {
        free(*newbuffer);
        return STANDARD_ERROR;
    }
}

/*
 * Check whether any data is available for reading
 */

static int
poll(_HANDLE h, double timeout)
{
    DWORD bytes, deadline, delay;
    
    if (timeout <= 0.0) {
        if (PeekNamedPipe(h, NULL, 0, NULL, &bytes, NULL))
            return bytes > 0;
        else
            return STANDARD_ERROR;
    }
    
    deadline = GetTickCount() + (DWORD)(1000 * timeout);

    /*
     * We sleep for 0 msecs and 1 msecs alternately
     * (Trying to delay for 1 msec always seems to cause a sleep of 10 msecs)
     */
    for (delay = 0 ; ; delay = !delay) {
        if (!PeekNamedPipe(h, NULL, 0, NULL, &bytes, NULL))
            return STANDARD_ERROR;
        else if (bytes > 0)
            return TRUE;        
        else if (deadline <= GetTickCount())
            return FALSE;
        Sleep(delay);
    }
}

#endif /* _PIPE_CONNECTION_H */
