===================================
 README for the processing package
===================================

:Author:  R Oudkerk
:Contact: r.m.oudkerk at gmail.com
:Url:     http://cheeseshop.python.org/pypi/processing

The processing package is and analogue of the `threading` module, but
using processes instead of threads. A sub-package `processing.dummy` has
the same API, but is a thin wrapper around `threading`.

For passing data between processes one can use pipes or queues.
Synchronization primitives like locks, semaphores conditions are also
available.  The sharing of objects between processes is possible by
using a "manager".

See `<INSTALL.txt>`_ for installation instructions.

The package is released under the BSD Licence, see `<LICENCE.txt>`_.

For further documentation see `<doc/index.html>`_.

