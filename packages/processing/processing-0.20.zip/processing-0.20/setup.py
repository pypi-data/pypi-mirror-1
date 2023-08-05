import sys
from distutils.core import setup, Extension

if sys.platform == 'win32':
    ext_modules = [
        Extension('processing.connection._socket_connection',
                  sources=['connection/socket_connection.c'],
                  libraries=['Ws2_32']),
        Extension('processing.connection._pipe_connection',
                  sources=['connection/pipe_connection.c'])
        ]
else:
    ext_modules = [
        Extension('processing.connection._socket_connection',
                  sources=['connection/socket_connection.c'])
        ]

testfiles = [
    'test/__init__.py', 'test/test_processing.py',
    'test/test_newtype.py', 'test/test_doc.py'
    ]
if sys.version_info >= (2, 5, 0):
    testfiles.append('test/test_with.py')


setup(
    name='processing',
    version='0.20',
    description='Package for using processes which mimics the threading module',
    author='R Oudkerk',
    author_email='r.m.oudkerk at gmail.com',
    url='http://cheeseshop.python.org/pypi/processing',
    license='BSD Licence',
    ext_modules=ext_modules,
    packages=['processing', 'processing.dummy', 'processing.connection'],
    package_dir={'processing': '.'},
    package_data={'processing': testfiles +
                  ['*.txt', 'doc/*.html', 'doc/*.css']},
    platforms='Unix and Windows',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        ],
    long_description='''
Package for using processes which mimics the threading module, and
allows the sharing of objects between processes.  Communication
between processes happens via sockets or (on Windows) named pipes.

The ``processing.Process`` class follows the API of ``threading.Thread``.
One can also use a *manager* to create shared objects.  The types
supported by default are ::

    Lock, RLock, Condition, Event, Semaphore,
    BoundedSemaphore, Queue, list, dict, Namespace.

For example::

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

on earlier versions.  This will run each test script twice: once using
processes and once using threads.

See ``README.txt`` and ``doc/index.html`` for more information.
'''
    )
