#
# Module providing the ``Process`` class which emulates ``threading.Thread``
#
# processing/process.py
#
# Copyright (c) 2006, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'Process', 'currentProcess' ]

import os, sys


class BaseProcess(object):
    _counter = 0
    
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        self._group = group
        self._target = target
        self._args = args
        self._kwargs = kwargs

        self._state = 'initial'
        BaseProcess._counter += 1
        try:
            self._identity = (BaseProcess._this_process._identity +
                              (BaseProcess._counter,))
        except AttributeError:
            self._identity = ()
            
        self._name = name or 'Process-' + ':'.join(map(str, self._identity))

    def join(self):
        assert self is not currentProcess()
        if self._state == 'started':
            res = os.waitpid(self._pid, 0)
            self._state = 'stopped'
            return res
        else:
            assert self._state == 'stopped'
    
    def run(self):        
        if self._target:
            self._target(*self._args, **self._kwargs)

    def _run(self):
        self._state = 'started'
        BaseProcess._this_process = self
        BaseProcess._counter = 0
        try:
            self.run()
        except:
            import traceback
            traceback.print_exc()
            
    def getName(self):
        return self._name

    def setName(self, name):
        if self._state == 'initial':
            self._name = name
        else:
            raise NotImplementedError, 'cannot change name of started Process'

    def __repr__(self):
        return '<%s(%s, started)>' % (type(self).__name__, self._name)

BaseProcess._this_process = BaseProcess(name='MainProcess')


class ForkingProcess(BaseProcess):
    '''
    Analogue of `threading.Thread`

    Works on unix and other platforms which have `os.fork`
    '''    
    def start(self):
        assert self._state == 'initial'
            
        self._pid = os.fork()
        if self._pid == 0:
            _reset_all_proxies()
            try:
                self._run()
            finally:
                _close_all_proxies()
                os._exit(0)
        else:
            self._state = 'started'


class NonForkingProcess(BaseProcess):
    '''
    Analogue of `threading.Thread`

    This is used on Windows and other platforms lacking `os.fork`
    '''
    def start(self):
        assert self._state == 'initial'

        import cPickle, _nonforking

        nonforkingpath = _nonforking.__file__
        if sys.platform == 'win32':
            nonforkingpath = '"' + nonforkingpath + '"'
        modulenames = {}

        for key, value in sys.modules.items():
            path = getattr(value, '__file__', None)
            modulenames[key] = path

        modulenames['__main__'] = os.path.abspath(sys.argv[0])

        names_to_files = cPickle.dumps(modulenames, 2).encode('hex')
        _self = cPickle.dumps(self, 2).encode('hex')

        self._pid = os.spawnv(
            os.P_NOWAIT, sys.executable,
            [sys.executable, nonforkingpath, names_to_files, _self]
            )

        self._state = 'started'


def currentProcess():
    '''
    Analogue of `threading.currentThread`.

    Returns the instance of a subclass of BaseProcess which represents
    the current process.
    '''
    return BaseProcess._this_process
    

if hasattr(os, 'fork'):
    Process = ForkingProcess
else:
    Process = NonForkingProcess
Process.__name__ = 'Process'


# If `processing.managers` loads then it overwrites these functions
def _reset_all_proxies():
    pass

def _close_all_proxies():
    pass
