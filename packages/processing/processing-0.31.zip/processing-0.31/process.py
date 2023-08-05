#
# Module providing the ``Process`` class which emulates ``threading.Thread``
#
# processing/process.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'Process', 'currentProcess', 'activeChildren',
            'ProcessExit', 'Finalize' ]

#
# Imports
#

import os, sys, signal, subprocess, time, atexit, weakref, random

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
        self._parent_pid = os.getpid()
        self._popen = None
        self._identity = _current_process._identity + (counter,)
        self._authkey = _current_process._authkey
        self._daemonic = _current_process._daemonic
        self._fork_commandline = _current_process._fork_commandline
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
        self._popen = Popen(self)
        _current_process._children.add(self)
        
    def stop(self):
        '''
        Raise `KeyboardInterrupt` in the process to stop it
        '''
        self._popen.stop()

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
        return self._popen and self._popen.poll()

    def getPid(self):
        '''
        Return PID of process or `None` if it has yet to start
        '''
        return self._popen and self._popen.pid

    def __repr__(self):
        if self is _current_process:
            status = 'started'
        elif self._parent_pid != os.getpid():
            status = 'unknown'
        elif self._popen is None:
            status = 'initial'
        else:
            if self._popen.poll() is not None:
                status = self._popen.returncode
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
            Finalize._registry.clear()
            _reset_all_proxies(self.getAuthKey(), self.getName())
            _current_process = self
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
            traceback.print_exc()
            
        os._exit(exitcode)
        
#
# Create object representing the main process
#

class _MainProcess(Process):
    
    def __init__(self):
        self._identity = ()
        self._authkey = os.urandom(16).encode('hex')
        self._daemonic = False
        self._name = 'MainProcess'
        self._parent_pid = None
        self._popen = None
        self._counter = 0
        self._children = set()
        self._fork_commandline = None
        
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

def _close_all_proxies():
    '''
    Dummy function that will be overwritten if `processing.managers` loads
    '''

#
# We define a subclass of `subprocess.Popen` with (if possible) a
# `stop()` method.  The constructor takes a process object as its argument.
#

if sys.platform != 'win32':
    
    class Popen(subprocess.Popen):
        
        def __init__(self, process_obj):
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
            try:
                os.kill(self.pid, STOP_PROCESS_SIGNAL)
            except OSError, e:
                if e.args[0] != 3: # no such process
                    raise
                
else:
    
    import cPickle
    from processing import _nonforking

    try:
        from processing import _processing
        _cflags = 0x00000200              # CREATE_NEW_PROCESS_GROUP
    except ImportError:
        _cflags = 0

    class Popen(subprocess.Popen):
        
        def __init__(self, process_obj):
            modulenames = {}
            for key, value in sys.modules.items():
                path = getattr(value, '__file__', None)
                if path is not None:
                    path = os.path.abspath(path)
                modulenames[key] = path
                
            if sys.argv[0] != '':
                modulenames['__main__'] = os.path.abspath(sys.argv[0])
            else:
                modulenames.pop('__main__', None)
                
            fork_commandline = process_obj._fork_commandline
            if fork_commandline is None:
                fork_commandline = [sys.executable, _nonforking.__file__]
            
            args = fork_commandline + [
                cPickle.dumps(modulenames, 2).encode('hex'),
                cPickle.dumps(process_obj, 2).encode('hex')
                ]
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            subprocess.Popen.__init__(self, args, creationflags=_cflags)
            
        if '_processing' in globals():
            def stop(self):
                CTRL_BREAK_EVENT = 1
                _processing.GenerateConsoleCtrlEvent(CTRL_BREAK_EVENT,self.pid)
        else:
            del Process.stop

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
_exitcode_to_name.update((-v,k) for (k,v) in signal.__dict__.iteritems()
                         if k[:3]=='SIG' and '_' not in k)

#
# Signal handling
#

if sys.platform == 'win32':
    STOP_PROCESS_SIGNAL = signal.SIGBREAK    
else:
    STOP_PROCESS_SIGNAL = signal.SIGUSR1

def _STOP_PROCESS_handler(signum, frame):
    raise ProcessExit
signal.signal(STOP_PROCESS_SIGNAL, _STOP_PROCESS_handler)

#
# Support for finalization of objects using weakrefs
#

class Finalize(object):
    '''
    Register a callback to be run once before 'obj' is garbage collected.
    '''
    _registry = {}
    
    def __init__(self, obj, callback, args=()):
        self._weakref = weakref.ref(obj, self)
        self._callback = callback
        self._args = args
        Finalize._registry[self._weakref] = self
        
    def __call__(self, ignore=None):
        '''
        Run the callback if it has not already been run
        '''
        try:
            del self._registry[self._weakref]
        except KeyError:
            pass
        else:
            self._callback(*self._args)
            self._weakref = self._callback = self._args = None
            
    @staticmethod
    def _run_all_finalizers():
        '''
        Run all registered callbacks which have not yet been run
        '''
        for finalizer in Finalize._registry.values():
            finalizer()
            
#
# Clean up on exit
#

def _exit_func():
    try:
        _close_all_proxies()

        if hasattr(Process, 'stop'):
            for p in activeChildren():
                if p._daemonic:
                    p._popen.stop()


        for p in activeChildren():
            if not p._daemonic:
                p.join()
    finally:
        _current_process._children.clear()
        Finalize._run_all_finalizers()
        
atexit.register(_exit_func)
