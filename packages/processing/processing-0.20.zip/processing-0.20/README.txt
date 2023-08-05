===================================
 README for the processing package
===================================

:Author:  R Oudkerk
:Contact: r.m.oudkerk at gmail.com
:Url:     http://cheeseshop.python.org/pypi/processing

The processing package is intended to be a portable analogue of the
threading module, but using processes instead of threads. A
sub-package processing.dummy has the same API, but is a thin wrapper
around threading.

Objects can be shared between processes by using a manager.
Communication between processes is achieved using sockets (or
alternatively on Windows by named pipes).


See `<INSTALL.txt>`_ for installation instructions.

The package is released under the BSD Licence, see `<LICENCE.txt>`_.

For further documentation see `<doc/index.html>`_.

