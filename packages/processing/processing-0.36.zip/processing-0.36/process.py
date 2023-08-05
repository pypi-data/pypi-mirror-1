#
# Module providing the ``Process`` class which emulates ``threading.Thread``
#
# processing/process.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#

__all__ = [
    'Process', 'currentProcess', 'activeChildren', 'freezeSupport',
    'ProcessExit', 'Finalize', 'getLogger', 'enableLogging'
    ]

#
# Imports
#

import os, sys, signal, subprocess, time, atexit, weakref, random, itertools
import encodings.hex_codec      # hint to freeze tools that we need hex codec

#
# Compatibility
#

try:
    set
except NameError:
    from sets import Set as set

#
# `ProcessExit` exception
#

class ProcessExit(SystemExit):
    pass

#
# Public functions
#

def currentProcess():
    '''
    Return process object representing the current process
    '''
    return _current_process


def activeChildren():
    '''
    Return list of process objects corresponding to live child processes
    '''
    _cleanup()
    return list(_current_process._children)


def freezeSupport():
    '''
    Check whether this is a fake forked process in a frozen executable.

    If so then run code specified by commandline and exit.
    '''
    if (WINEXE and len(sys.argv) > 1 and sys.argv[1] == '--processing-fork'):
        assert len(sys.argv) == 4
        _nonforking.run(sys.argv[2], sys.argv[3])
        sys.exit(0)

#
# Set commandline prefix for spawning child processes on Windows
#

WINEXE = (sys.platform == 'win32' and getattr(sys, 'frozen', False))

if WINEXE:
    import _nonforking
    _fork_commandline = [sys.executable, '--processing-fork']
    
elif sys.platform == 'win32':
    import _nonforking
    if sys.executable.lower().endswith('pythonservice.exe'):
        # we are running as a windows service using `pywin32`
        exe = os.path.join(os.path.dirname(os.__file__), '..', 'python.exe')
    else:
        exe = sys.executable
    _fork_commandline = [exe, _nonforking.__file__]

#
# The `Process` class
#

class Process(object):
    '''
    Process objects represent activity that is run in a separate process

    The class is analagous to `threading.Thread`
    '''
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        _current_process._counter += 1
        counter = _current_process._counter

        self._target = target
        self._args = args
        self._kwargs = kwargs
        self._stoppable = False
        self._parent_pid = os.getpid()
        self._popen = None
        self._identity = _current_process._identity + (counter,)
        self._authkey = _current_process._authkey
        self._daemonic = _current_process._daemonic
        self._logargs = _current_process._logargs
        self._name = name or 'Process-' + ':'.join(map(str, self._identity))
        self._counter = 0
        self._children = set()

    def run(self):
        '''
        Method to be run in sub-process; can be overridden in sub-class
        '''
        if self._target:
            self._target(*self._args, **self._kwargs)
            
    def start(self):
        '''
        Start child process
        '''
        assert self._popen is None, 'cannot start a process twice'
        assert self._parent_pid == os.getpid(), \
               'can only start a process object created by current process'
        _cleanup()
        sys.stdout.flush()
        sys.stderr.flush()
        self._popen = Popen(self, self._stoppable)
        _current_process._children.add(self)

    def stop(self):
        '''
        Raise `KeyboardInterrupt` in the process to stop it
        '''
        assert self._stoppable, '`setStoppable(True)` was not used'
        self._popen.stop()

    def terminate(self):
        '''
        Terminate process; sends `SIGTERM` signal or uses `TerminateProcess()`
        '''
        self._popen.terminate()
        
    def join(self, timeout=None):
        '''
        Wait until child process terminates
        '''
        assert self._parent_pid == os.getpid(), 'can only join a child process'
        assert self._popen is not None, 'can only join a started process'
        if timeout == 0:
            res = self._popen.poll()
        elif timeout == None:
            # avoid using `Popen.wait()` because that is uninterruptible
            res = _sleep_until_neq(self._popen.poll, None, 1e100)
        else:
            res = _sleep_until_neq(self._popen.poll, None, timeout)
        if res is not None:
            _cleanup()

    def isAlive(self):
        '''
        Return whether child process is alive
        '''
        if self is _current_process:
            return True
        assert self._parent_pid == os.getpid(), 'can only test a child process'
        if self._popen is None:
            return False
        self._popen.poll()
        return self._popen.returncode is None

    def getName(self):
        '''
        Return name of process
        '''
        return self._name

    def setName(self, name):
        '''
        Set name of process
        '''
        assert type(name) is str, 'name must be a string'
        self._name = name

    def isDaemon(self):
        '''
        Return whether process is a daemon
        '''
        return self._daemonic

    def setDaemon(self, daemonic):
        '''
        Set whether process is a daemon
        '''
        assert self._popen is None, 'process has already started'
        assert hasattr(self, 'stop'), 'process needs a `stop()` method'
        self._daemonic = daemonic

    def getAuthKey(self):
        '''
        Return authorization key of process
        '''
        return self._authkey

    def setAuthKey(self, authkey):
        '''
        Set authorization key of process
        '''
        assert type(authkey) is str, 'value must be a string'

        self._authkey = authkey

    def getExitCode(self):
        '''
        Return exit code of process or `None` if it has yet to stop
        '''
        if self._popen is None:
            return self._popen
        if self._popen.poll() == 0x10000:
            return -signal.SIGTERM
        return self._popen.poll()

    def getPid(self):
        '''
        Return PID of process or `None` if it has yet to start
        '''
        return self._popen and self._popen.pid

    def getStoppable(self):
        '''
        Returns whether process supports the `stop()` method and `ProcessExit`
        '''
        return self._stoppable

    def setStoppable(self, value):
        '''
        Set whether process supports the `stop()` method and `ProcessExit`
        '''
        assert self._popen is None, 'process has already started'
        self._stoppable = value

    def __repr__(self):
        if self is _current_process:
            status = 'started'
        elif self._parent_pid != os.getpid():
            status = 'unknown'
        elif self._popen is None:
            status = 'initial'
        else:
            if self._popen.poll() is not None:
                status = self.getExitCode()
            else:
                status = 'started'

        if type(status) is int:
            if status == 0:
                status = 'stopped'
            else:
                status = 'stopped[%s]' % _exitcode_to_name.get(status, status)

        return '<%s(%s, %s)>' % (type(self).__name__, self._name, status)

    ##

    def _bootstrap(self):
        global _current_process
        try:
            random.seed()
            sys.stdin.close()
            Finalize._registry.clear()
            _reset_all_proxies(self.getAuthKey(), self.getName())
            _current_process = self
            if sys.platform == 'win32' and self._logargs is not None:
                enableLogging(*self._logargs)
            info('process starting up')
            try:
                self.run()
                exitcode = 0
            finally:
                sys.stdout.flush()
                sys.stderr.flush()
                _exit_func()
        except ProcessExit:
            exitcode = 127
        except SystemExit, e:
            if not e.args:
                exitcode = 1
            elif type(e.args[0]) is int:
                exitcode = e.args[0]
            else:
                print >>sys.stderr, e.args[0]
                exitcode = 1
        except:
            exitcode = 1
            import traceback
            print >>sys.stderr, 'Process %s:' % self.getName()
            traceback.print_exc()

        info('process exiting with `os.exit(0)`')
        os._exit(exitcode)

#
# Create object representing the main process
#

class _MainProcess(Process):

    def __init__(self):
        self._identity = ()
        self._daemonic = False
        self._name = 'MainProcess'
        self._parent_pid = None
        self._popen = None
        self._logargs = None
        self._counter = 0
        self._children = set()

        # calculate authentication key
        try:
            self._authkey = os.urandom(16).encode('hex')
        except AttributeError:
            import random
            key = [chr(random.randrange(256)) for i in range(16)]
            self._authkey = ''.join(key).encode('hex')

_current_process = _MainProcess()
del _MainProcess

#
# Private functions
#

def _cleanup():
    '''
    Purge `_children` of dead processes
    '''
    for p in list(_current_process._children):
        if p._popen.poll() is not None:
            _current_process._children.discard(p)

def _sleep_until_neq(func, value, timeout):
    '''
    Sleep until `func() != value` or timeout elapses
    Returns the last value returned by `func()`
    '''
    deadline = time.time() + timeout
    delay = 0.0005
    while 1:
        res = func()
        if res != value:
            break
        remaining = deadline - time.time()
        if remaining <= 0:
            break
        delay = min(delay * 2, remaining, 0.05)
        time.sleep(delay)
    return res

def _reset_all_proxies(authkey, process_name):
    '''
    Dummy function that will be overwritten if `processing.managers` loads
    '''

#
# We define a subclass of `subprocess.Popen`.
# The constructor takes a process object as its argument.
#

if sys.platform != 'win32':

    class Popen(subprocess.Popen):

        def __init__(self, process_obj, ignore=None):
            subprocess._cleanup()
            self.returncode = None
            self.pid = os.fork()
            if self.pid == 0:
                process_obj._bootstrap()
                os._exit(0)
            if not hasattr(subprocess.Popen, '__del__'):  # Python 2.4
                subprocess._active.append(self)
            else:                                         # Python 2.5
                self._child_created = True

        def stop(self):
            if self.returncode is None:
                try:
                    os.kill(self.pid, STOP_PROCESS_SIGNAL)
                except OSError, e:
                    if self.returncode is not None:
                        raise

        def terminate(self):
            if self.returncode is None:
                try:
                    os.kill(self.pid, signal.SIGTERM)
                except OSError, e:
                    if self.returncode is not None:
                        raise

else:
    
    import cPickle

    try:
        import _processing
        _cflags = 0x00000200           # CREATE_NEW_PROCESS_GROUP
    except ImportError:
        _cflags = 0
    
    _dir = os.getcwd()                 # remember in case os.chdir() used later

    class Popen(subprocess.Popen):

        def __init__(self, process_obj, new_console=1):
            if sys.argv[0] not in ('', '-c') and not WINEXE:
                _mainpath = getattr(sys.modules['__main__'], '__file__', None)
                if _mainpath and not os.path.isabs(_mainpath):
                    # might be wrong if os.chdir() was used before this
                    # module loaded 
                    _mainpath = os.path.join(_dir, _mainpath)
            else:
                _mainpath = None
            preparation_data = [_mainpath, sys.path, os.getcwd(), new_console]

            flags = new_console and _cflags
            args = _fork_commandline + [
                cPickle.dumps(preparation_data, 2).encode('hex')
                ]

            pickled_process = cPickle.dumps(process_obj, 2)

            if len(pickled_process) < 2000:
                args.append(pickled_process.encode('hex'))
                subprocess.Popen.__init__(self, args, creationflags=flags)
            else:
                debug('process object is big so use pipe not commandline')
                from processing.connection import Listener
                l = Listener()
                args.append(cPickle.dumps(l.address, 2).encode('hex'))
                subprocess.Popen.__init__(self, args, creationflags=flags)
                conn = l.accept()
                conn.sendbytes(pickled_process)
                conn.close()
                l.close()
                

        if '_processing' in globals():
            
            def stop(self):
                if self.returncode is None:
                    try:
                        _processing.GenerateConsoleCtrlEvent(1, self.pid)
                    except WindowsError:
                        if self.returncode is not None:
                            raise

            def terminate(self):
                if self.returncode is None:
                    try:
                        _processing.TerminateProcess(self._handle, 0x10000)
                    except WindowsError:
                        if self.returncode is not None:
                            raise
            
        else:
            del Process.stop
            del Process.terminate

#
# In Python 2.5 `subprocess.Popen` has a `__del__()` method which often
# seems to raise `AttributeError` when the interpreter shuts down.  We
# overwrite it.
#

if hasattr(Popen, '__del__'):
    def __del__(self):
        if Popen is not None:
            try:
                super(Popen, self).__del__()
            except AttributeError:
                pass
    Popen.__del__ = __del__
    del __del__

#
# Give names to some return codes
#

_exitcode_to_name = { 127 : 'ProcessExit' }

for name, signum in signal.__dict__.items():
    if name[:3]=='SIG' and '_' not in name:
        _exitcode_to_name[-signum] = name

#
# Signal handling
#

if sys.platform == 'win32':
    STOP_PROCESS_SIGNAL = signal.SIGBREAK
else:
    STOP_PROCESS_SIGNAL = signal.SIGUSR1

    def _STOP_PROCESS_handler(signum, frame):
        raise ProcessExit

    # On Windows signal handler is set in `_nonforking`
    signal.signal(STOP_PROCESS_SIGNAL, _STOP_PROCESS_handler)

#
# Support for finalization of objects using weakrefs
#

class Finalize(object):
    '''
    Register a callback to be run once before 'obj' is garbage collected.
    
    If 'obj' is not collected by time of process termination then the
    callback will be run if 'atexit' parameter of constructor was true.
    '''
    _registry = {}
    _getindex = itertools.count().next
    
    def __init__(self, obj, callback, args=(), atexit=False):
        self._weakref = weakref.ref(obj, self)
        self._callback = callback
        self._args = args
        self._atexit = atexit
        self._index = Finalize._getindex()
        Finalize._registry[self] = None
        
    def __call__(self, ignore=None):
        '''
        Run the callback if it has not already been run
        '''
        log(5, 'calling %s from finalizer', self._callback)
        try:
            del Finalize._registry[self]
        except KeyError:
            pass
        else:
            self._callback(*self._args)
            self._weakref = self._callback = self._args = None

    def __repr__(self):
        return '<Finalizer(callback=%r, args=%r, atexit=%r)>' % \
               (self._callback, self._args, self._atexit)

    # staticmethod
    def _run_all_finalizers():
        '''
        Run remaining callbacks (in reverse order of registration)
        '''
        L = Finalize._registry.keys()
        L.sort(cmp=lambda x,y: -cmp(x._index, y._index))

        for finalizer in L:
            if finalizer._atexit:
                try:
                    finalizer()
                except Exception:
                    import traceback
                    traceback.print_exc()

    _run_all_finalizers = staticmethod(_run_all_finalizers)

#
# Logging
#

_logger = None

def debug(msg, *args):
    if _logger:
        _logger.debug(msg, *args)

def info(msg, *args):
    if _logger:
        _logger.info(msg, *args)

def log(level, msg, *args):
    if _logger:
        _logger.log(level, msg, *args)

def getLogger():
    '''
    Returns logger used by processing
    '''
    return _logger

def enableLogging(level, HandlerType=None, handlerArgs=(), format=None):
    '''
    Enable logging using `level` as the debug level
    '''
    global _logger
    import logging

    logging._acquireLock()
    try:
        if _logger is None:
            _logger = logging.getLogger('processing-7bb69610')
            _logger.propagate = 0

            # we want `_logger` to support the "%(processName)s" format
            def makeRecord(self, *args):
                record = self.__class__.makeRecord(self, *args)
                record.processName = _current_process._name
                return record
            _logger.makeRecord = makeRecord.__get__(_logger, type(_logger))

            # cleanup func of `processing` should run before that of `logging`
            atexit._exithandlers.remove((_exit_func, (), {}))
            atexit._exithandlers.append((_exit_func, (), {}))

        if not _logger.handlers or HandlerType:
            HandlerType = HandlerType or logging.StreamHandler
            format = format or '[%(levelname)s/%(processName)s] %(message)s'

            handler = HandlerType(*handlerArgs)
            handler.setFormatter(logging.Formatter(format))
            _logger.addHandler(handler)       
            _logger.setLevel(level)
            _current_process._logargs = [level,HandlerType,handlerArgs,format]
        else:
            _logger.setLevel(level)
            _current_process._logargs[0] = level
    finally:
        logging._releaseLock()

#
# Clean up on exit
#

def _exit_func():
    try:
        info('running all "atexit" finalizers')
        Finalize._run_all_finalizers()
        
    finally:
        for p in activeChildren():
            if p._daemonic and p._stoppable:
                info('calling `stop()` for daemon %s', p.getName())
                p._popen.stop()

        deadline = time.time() + 0.1

        for p in activeChildren():
            if p._daemonic and p._stoppable:
                info('calling `join(timeout)` for daemon %s', p.getName())
                p.join(deadline - time.time())
            
        for p in activeChildren():
            if p._daemonic:
                info('calling `terminate()` for daemon %s', p.getName())
                p._popen.terminate()

        for p in activeChildren():
            if not p._daemonic:
                info('calling `join()` for normal process %s', p.getName())
                p.join()

atexit.register(_exit_func)
