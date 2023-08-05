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
    author='R Oudkerk',
    author_email='roudkerk at users.berlios.de',
    url='http://developer.berlios.de/projects/pyprocessing',
    license='BSD Licence',
    platforms='Unix and Windows',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        ],
    package_dir={'processing': '.'},
    packages=['processing', 'processing.dummy']
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

kwds['package_data'] = {'processing': data}

#
# Get `long_description` from `README.txt`
#

doc = open('README.txt', 'rU').read()
start_string = ':Licence:       BSD Licence\n\n'
end_string = '.. raw:: html'
start = doc.index(start_string) + len(start_string)
end = doc.index(end_string)
doc = doc[start:end]
doc = doc.replace('<./', '<http://pyprocessing.berlios.de/')
kwds['long_description'] = doc

#
# Setup
#

setup(**kwds)
