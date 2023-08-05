/*
 * Definitions used by `connection.h`
 *
 * socket_def.h
 *
 * Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
 */

#ifndef _SOCKET_CONNECTION_H
#define _SOCKET_CONNECTION_H

#ifdef MS_WINDOWS

/*
 * Windows definitions
 */

#define FALSE_SOCKET

#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>

typedef SOCKET _HANDLE;
typedef unsigned uint32_t;

#define INVALID_HANDLE INVALID_SOCKET

#define _write(h, buffer, length) send(h, buffer, length, 0)
#define _read(h, buffer, length) recv(h, buffer, length, 0)
#define _close(h) closesocket(h)

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

#else

/*
 * Posix definitions
 */

#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

typedef int BOOL;
typedef unsigned char BYTE;
typedef int _HANDLE;

#define TRUE (1)
#define FALSE (0)
#define INVALID_HANDLE (-1)

#define _write write
#define _read read
#define _close close
#define _duplicate dup

#endif /* MS_WINDOWS */


/*
 * Error values
 */

#define SUCCESS (0)
#define STANDARD_ERROR (-1)
#define MEMORY_ERROR (-2)
#define ALREADY_SET_ERROR (-3)
#define SELECT_ERROR (4)
#define END_OF_FILE (-5)
#define EARLY_END_OF_FILE (-6)

static PyObject *
SetExcFromNumber(int num)
{
    switch (num) {
    case STANDARD_ERROR: 
#ifdef MS_WINDOWS
        PyErr_SetFromWindowsErr(0);
#else
        PyErr_SetFromErrno(PyExc_OSError); 
#endif
        break;
    case MEMORY_ERROR:
        PyErr_NoMemory();
        break;
    case ALREADY_SET_ERROR:
        break;
    case END_OF_FILE:
        PyErr_SetString(PyExc_IOError, "got end of file");
        break;
    case EARLY_END_OF_FILE:
        PyErr_SetString(PyExc_IOError, "got end of file during message");
        break;
    case SELECT_ERROR:
        PyErr_SetString(PyExc_IOError, "select failed");
        break;
    default:
        PyErr_SetString(PyExc_AssertionError, "unknown error number");
    }
    return NULL;
}

/*
 * Send string to file descriptor
 */

static int
_sendall(_HANDLE h, char *string, size_t length)
{
    char *p = string;
    int res;
    
    while (length > 0) {
        res = _write(h, p, length);
        if (res < 0)
            return STANDARD_ERROR;
        length -= res;
        p += res;
    }
    
    return SUCCESS;
}

/*
 * Receive string of exact length from file descriptor 
 */

static int
_recvall(_HANDLE h, char *buffer, size_t length)
{
    int remaining = length, temp;
    char *p = buffer;
    
    while (remaining > 0) {
        temp = _read(h, p, remaining);
        if (temp <= 0) {
            if (temp == 0)
                return remaining == (int)length
                    ? END_OF_FILE : EARLY_END_OF_FILE;
            else
                return temp;
        }
        remaining -= temp;
        p += temp;
    }
    
    assert(remaining == 0);
    return SUCCESS;
}

/*
 * Send a string prepended by the string length in network byte order
 */

static int
send_string(_HANDLE h, char *string, size_t length)
{
    char *message, *p;
    int res;
    
    p = message = malloc(length+4);
    if (p == NULL)
        return MEMORY_ERROR;
    
    *(uint32_t*)message = htonl(length);     
    memcpy(message+4, string, length);
    res = _sendall(h, message, length+4);
    free(message);
    
    return res;
}

/*
 * Attempts to read into buffer, or failing that into *newbuffer
 *
 * Returns number of bytes read.
 */

static int
recv_string(_HANDLE h, char *buffer, size_t buflength, char **newbuffer)
{
    int res, length;
    char lenbuff[4];
    
    *newbuffer = NULL;
    
    res = _recvall(h, lenbuff, 4);
    if (res < 0)
        return res;
    
    length = htonl(*(uint32_t*) lenbuff);
    
    if (length <= (int)buflength) {
        res = _recvall(h, buffer, length);
        return res < 0 ? res : length;
    } else {
        *newbuffer = malloc(length > 0 ? length : 1);
        if (*newbuffer == NULL)
            return MEMORY_ERROR;
        res = _recvall(h, *newbuffer, length);
        return res < 0 ? res : length;
    }
}

/*
 * Check whether any data is available for reading
 */

static int
poll(_HANDLE fd, double timeout)
{
    int res;
    fd_set rfds;
    struct timeval tv;
    
    FD_ZERO(&rfds);
    FD_SET(fd, &rfds);
    
    if (timeout < 0.0)
        timeout = 0.0;
    
    tv.tv_sec = (int)timeout;
    tv.tv_usec = (int)((timeout - tv.tv_sec) * 1e6);
    
    res = select(fd+1, &rfds, NULL, NULL, &tv);
    
    if (FD_ISSET(fd, &rfds)) {
        return TRUE;
    } else if (res == 0) {
        return FALSE;
    } else {
#ifdef MS_WINDOWS
        return SELECT_ERROR;
#else
        return STANDARD_ERROR;
#endif
    }
}

#endif /* _SOCKET_CONNECTION_H */

