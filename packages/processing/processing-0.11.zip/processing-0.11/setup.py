import sys, os, shutil
from distutils.core import setup, Extension

if sys.platform == 'win32':
    ext_modules = [
        Extension('processing.socket_connection',
                  sources=['src/socket_connection.c'],
                  libraries=['Ws2_32']),
        Extension('processing.pipe_connection',
                  sources=['src/pipe_connection.c'])
        ]
else:
    ext_modules = [
        Extension('processing.socket_connection',
                  sources=['src/socket_connection.c'])
        ]

    
setup(
    name='processing',
    version='0.11',
    description='Package for using processes which mimics the threading module',
    author='Richard Oudkerk',
    author_email='r.m.oudkerk at gmail.com',
    url='http://cheeseshop.python.org/pypi/processing',
    license='BSD Licence',
    ext_modules=ext_modules,
    packages=['processing'],
    package_dir={'processing': 'src'},
    platforms='Unix and Windows',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python',
        ],
    long_description='''
Package for using processes which mimics the threading module, and
allows the sharing of objects between processes.  Communication
between processes happens via sockets or named pipes.

The 'processing.Process' class follows the API of 'threading.Thread'.
One can also use a manager to create shared objects.  The types
supported by default are: Lock, RLock, Condition, Event, Semaphore,
BoundedSemaphore, Queue, list, dict, set.  For example

>>> from processing import Manager, Repr
>>> manager = Manager()
>>> l = manager.list(range(10))
>>> l.reverse()
>>> print l
<Proxy[list] object at 0x00c33470)>
>>> print Repr(l)
[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
'''
    )

