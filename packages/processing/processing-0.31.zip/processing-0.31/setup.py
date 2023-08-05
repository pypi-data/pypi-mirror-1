import sys
from distutils.core import setup, Extension

#
# Configuration
#

if sys.platform == 'win32':
    macros = dict()
    libraries = ['Ws2_32']

elif sys.platform == 'cygwin':
    macros = dict(
        USE_SENDFD=0,
        USE_POSIX_SEMAPHORE=1,
        USE_POSIX_QUEUE=0,
        NO_SEM_UNLINK=None    # sem_unlink seems to be missing from semaphore.h
        )
    libraries = []

else:
    macros = dict(
        USE_SENDFD=1,         # send file descriptors over unix domain sockets
        USE_POSIX_SEMAPHORE=1,# use posix name semaphores
        USE_POSIX_QUEUE=1     # use posix message queues
        )
    libraries = ['rt']

#
# Python files to install
#

packages = [ 'processing', 'processing.dummy' ]

datafiles = [
    '*.txt',
    'doc/*.html',
    'doc/*.css',
    'test/__init__.py',
    'test/test_processing.py',
    'test/test_newtype.py',
    'test/test_doc.py',
    'test/test_speed.py',
    'test/test_stop.py',
    'test/test_connection.py',
    'test/test_reduction.py'
    ]

if sys.version_info >= (2, 5, 0):
    datafiles += ['test/test_with.py']

if sys.platform == 'win32':
    datafiles += [
        'test/py2exedemo/setup.py',
        'test/py2exedemo/test.py',
        'test/py2exedemo/_test.py'
        ]

if sys.platform == 'win32' and sys.version_info < (2, 5, 0):
    packages += ['processing.compat']

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

    if macros['USE_POSIX_SEMAPHORE']:
        sources.append('src/posix_semaphore.c')
    if macros['USE_POSIX_QUEUE']:
        sources.append('src/posix_queue.c')


extension = Extension(
    'processing._processing',
    sources=sources,
    libraries=libraries,
    define_macros=macros.items()
    )

#
# Description
#

description = '''\
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
        p.join()
        print q.get()

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

See `README.txt` and `doc/index.html` in the package directory for
more information.
'''

#
# Setup
#

setup(
    name='processing',
    version='0.31',
    description='Package for using processes mimicking the `threading` module',
    author='R Oudkerk',
    author_email='r.m.oudkerk at gmail.com',
    url='http://cheeseshop.python.org/pypi/processing',
    license='BSD Licence',
    ext_modules=[extension],
    packages=packages,
    package_dir={'processing': '.'},
    package_data={'processing': datafiles},
    platforms='Unix and Windows',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        ],
    long_description=description
    )
