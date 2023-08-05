'''
Package for using processes which mimics the threading module, and
allows the sharing of objects between processes.

The ``processing.Process`` class follows the API of ``threading.Thread``.
For example ::

    from processing import Process, Queue

    def f(q):
        q.put('hello world')

    if __name__ == '__main__':
        q = Queue()
        p = Process(target=f, args=[q])
        p.start()
        print q.get()
        p.join()

Synchronization primitives like locks, semaphores and conditions are
available, for example ::

    >>> from processing import Condition
    >>> c = Condition()
    >>> print c
    <Condition(<RLock(None, 0)>), 0>
    >>> c.acquire()
    True
    >>> print c
    <Condition(<RLock(MainProcess, 1)>), 0>

One can also use a manager to create shared objects either in shared
memory or in a server process, for example ::

    >>> from processing import Manager
    >>> manager = Manager()
    >>> l = manager.list(range(10))
    >>> l.reverse()
    >>> print l
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    >>> print repr(l)
    <Proxy[list] object at 0x00E1B3B0>

After installation you can run the test scripts by doing either ::

    python -m processing.test

on Python 2.5 or ::

    python -c "from processing.test import main; main()"

on Python 2.4.  This will run various test scripts using both
processes and threads.

See ``README.txt`` and ``doc/index.html`` in the package directory for
more information.
'''

#
# Imports
#

import sys, os
from glob import glob
from os.path import join, dirname
from distutils.core import setup, Extension
from __init__ import __version__

#
# Function to check for features using sysconf
#

def have_feature(name):
    try:
        return int(os.sysconf(name) not in (0, -1))
    except (ValueError, OSError):
        return 0

#
# Basic configuration
#
# The `macros` dict determines the macros that will be defined when the
# C extension is compiled.  Each value should be either `1` or `0`.
#
# The `libraries` dict determines the libraries to which the C
# extension will be linked.  This should probably be either `['rt']`
# if you need `librt` or else `[]`.
#

if sys.platform == 'win32':
    macros = dict()
    libraries = ['Ws2_32']
    
elif sys.platform == 'cygwin':
    macros = dict(
        USE_POSIX_SEMAPHORE=1,
        NO_SEM_UNLINK=1,        # `sem_unlink()` is missing from <semaphore.h>
        NO_SENDFD=1             # cannot send file descriptors over sockets
        )
    libraries = []              # we don't have/need librt
    
elif sys.platform == 'darwin':
    macros = dict(
        USE_POSIX_SEMAPHORE=1,
        NO_SEM_TIMED=1          # we don't have sem_timedwait()
        )
    libraries = []              # we don't have/need librt
    
else:
    macros = dict(
        # should we include support for posix semaphores?
        USE_POSIX_SEMAPHORE=have_feature('SC_SEMAPHORES'),
        # should we include support for posix message queues?
        USE_POSIX_QUEUE=have_feature('SC_MESSAGE_PASSING'),
        # does semaphore support lack sem_timedwait()?
        NO_SEM_TIMED=0,
        # does posix queue support lack mq_timedsend() and mq_timedreceive()?
        NO_MQ_TIMED=0
        )
    # linux needs librt - other unices may not
    libraries = ['rt']
    
#
# Print configuration info
#

print 'Macros:'

for name, value in macros.items():
    print '\t%s = %r' % (name, value)

print '\nLibraries:\n\t%r\n' % libraries

#
# Keyword parameters for `setup()`
#

kwds = dict(
    name='processing',
    version=__version__,
    description=('Package for using processes mimicking ' +
                 'the `threading` module'),
    long_description=__doc__,
    author='R Oudkerk',
    author_email='r.m.oudkerk at gmail.com',
    url='http://cheeseshop.python.org/pypi/processing',
    license='BSD Licence',
    platforms='Unix and Windows',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        ],
    package_dir={'processing': '.'},
    packages=['processing', 'processing.dummy', 'processing']
    )

#
# Compilation of `_processing` extension
#

if sys.platform == 'win32':
    sources = [
        'src/win_processing.c',
        'src/win_semaphore.c',
        'src/pipe_connection.c',
        'src/socket_connection.c'
        ]

else:
    sources = [
        'src/posix_processing.c',
        'src/socket_connection.c'
        ]

    if macros.get('USE_POSIX_SEMAPHORE', False):
        sources.append('src/posix_semaphore.c')
    if macros.get('USE_POSIX_QUEUE', False):
        sources.append('src/posix_queue.c')

kwds['ext_modules'] = [
    Extension(
        'processing._processing',
        sources=sources,
        libraries=libraries,
        define_macros=macros.items(),
        depends=glob('src/*.h')
        )
    ]

#
# Extra files to install
#

data = ['*.txt', '*.html', 'doc/*.html', 'doc/*.css'] + glob('test/*.py')

if sys.version_info < (2, 5, 0):
    data = [x for x in data if 'test_with.py' not in x]

if sys.version_info >= (2, 4, 0):
    kwds['package_data'] = {'processing': data}
else:
    # not sure if it will install on Python 2.3 -- probably not
    processing_path = join(dirname(os.__file__), 'site-packages', 'processing')
    kwds['data_files'] = [(join(processing_path, dirname(pat)), glob(pat))
                          for pat in data]

#
# Setup
#

setup(**kwds)
