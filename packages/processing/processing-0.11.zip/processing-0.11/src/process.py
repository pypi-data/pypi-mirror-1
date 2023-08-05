#
# Module providing the Process class which emulates threading.Thread
#
# processing/process.py
#
# Copyright (c) 2006, Richard Oudkerk
#

__all__ = [ 'Process', 'currentProcess' ]

import os, sys

class DummyProcess(object):

    def __init__(self):
        self._identity = ()
        self._name = 'MainProcess'

    def getName(self):
        return self._name

    def __repr__(self):
        if self._identity == ():
            return '<%s(MainProcess, started)>' % Process.__name__
        else:
            return '<%s(%s, started)>' % (type(self).__name__, self.getName())


class Process(DummyProcess):    
    '''
    Analogue of threading.Thread
    '''
    _this_process = DummyProcess()
    _counter = 0

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        self._group = group
        self._target = target
        self._args = args
        self._kwargs = kwargs

        self._state = 'initial'
        Process._counter += 1
        self._identity = Process._this_process._identity + (Process._counter,)

        if name is None:
            self._name = 'Process-' + ':'.join(map(str, self._identity))
        else:
            self._name = name

    def join(self):
        assert self._state == 'started'
        assert self is not currentProcess()
        res = os.waitpid(self._pid, 0)
        self._state = 'stopped'
        return res
    
    def run(self):        
        if self._target:
            self._target(*self._args, **self._kwargs)

    def _run(self):
        self._state = 'started'
        Process._this_process = self
        Process._counter = 0
        self.run()

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
            
    def setName(self, name):
        if self._state == 'initial':
            self._name = name
        else:
            raise NotImplementedError, 'cannot change name of started Process'

    def exit(n=0):
        os._exit(n)
    exit = staticmethod(exit)


class NonForkingProcess(Process):
    '''
    Analogue of threading.Thread which does not use os.fork

    This has to be used on windows
    '''

    def start(self):
        assert self._state == 'initial'

        import binascii, cPickle, nonforking

        default_dir = os.path.dirname(os.__file__)
        nonforkingpath = nonforking.__file__
        if sys.platform == 'win32':
            nonforkingpath = '"' + nonforkingpath + '"'
        modulenames = {}

        for key, value in sys.modules.items():
            path = getattr(value, '__file__', None)
            modulenames[key] = path

        modulenames['__main__'] = os.path.abspath(sys.argv[0])

        names_to_files = binascii.hexlify(cPickle.dumps(modulenames, 2))
        _self = binascii.hexlify(cPickle.dumps(self, 2))

        self._pid = os.spawnv(
            os.P_NOWAIT, sys.executable,
            [sys.executable, nonforking.__file__, names_to_files, _self]
            )

        self._state = 'started'

    def exit(n=0):
        sys.exit(n)
    exit = staticmethod(exit)


if not hasattr(os, 'fork'):
    Process = NonForkingProcess


def currentProcess():
    '''
    Analogue of threading.currentThread
    '''
    return Process._this_process

del DummyProcess

# If processing.manager loads it overwrites these functions
def _reset_all_proxies():
    pass

def _close_all_proxies():
    pass
