#ifndef PROCESSING_DEFS_H
#define PROCESSING_DEFS_H

#define PY_SSIZE_T_CLEAN

#include "Python.h"

#if PY_VERSION_HEX < 0x02050000 && !defined(PY_SSIZE_T_MIN)
   typedef int Py_ssize_t;
#  define PY_SSIZE_T_MAX INT_MAX
#  define PY_SSIZE_T_MIN INT_MIN
#  define N_FMT "i"
#else
#  define N_FMT "n"
#endif

#endif /* PROCESSING_DEFS_H */
