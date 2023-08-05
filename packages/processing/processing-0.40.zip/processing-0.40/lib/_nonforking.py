#
# A kludge used by `processing` package because Windows lacks `os.fork()`
#
# processing/fork.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#
# The `Process.start()` method spawns a new python interpreter which
# runs the `run()` function of this module.  The commandline arguments
# passed contain `self`, and some other information (encoded using
# `cPickle` and the `hex` codec).
#

__all__ = []


import os
import sys
import imp
import cPickle
import StringIO
import encodings.hex_codec      # hint to freeze tools that we need hex codec
import signal
import processing

from os.path import dirname, splitext, basename, abspath


WINEXE = (sys.platform == 'win32' and getattr(sys, 'frozen', False))
_dir = os.getcwd()
pyexts = ('.py', '.pyc', '.pyo', '.pyw')


def equal(path1, path2):
    '''
    Test whether the paths match (more or less)
    '''
    path1 = abspath(path1)
    path2 = abspath(path2)
    if path1 == path2:
        return True
    path1 = splitext(path1)
    path2 = splitext(path2)
    if path1[0] != path2[0]:
        return False
    return path1[1] in pyexts and path2[1] in pyexts


def is_forking(argv):
    '''
    Return whether commandline indicates we are forking
    '''
    if len(argv) >= 2 and argv[1] == '--processing-fork':
        assert len(argv) == 2
        return True
    else:
        return False


def freezeSupport():
    '''
    Run code for process object if this in not the main process
    '''
    if is_forking(sys.argv):
        main()
        sys.exit()
        

def get_commandline():
    '''
    Returns the commandline used for spawning a child interpreter process
    '''
    if processing.currentProcess()._identity == () and is_forking(sys.argv):
        raise RuntimeError, '''
        Attempt to start a new process before the current process
        has finished its bootstrapping phase.

        This probably means that you are on Windows and you have
        forgotten to use the proper idiom in the main module:

            if __name__ == '__main__':
                freezeSupport()
                ...

        The "freezeSupport()" line can be omitted if the program
        is not going to be frozen to produce a Windows executable.'''

    prog = 'from processing._nonforking import main; main()'
    if getattr(sys, 'frozen', False):
        return [sys.executable, '--processing-fork']
    elif sys.executable.lower().endswith('pythonservice.exe'):
        exe = os.path.join(os.path.dirname(os.__file__), '..', 'python.exe')
        return [exe, '-c', prog, '--processing-fork']
    else:
        return [sys.executable, '-c', prog, '--processing-fork']


def get_preparation_data(name, new_console):
    '''
    Return info about parent process will be passed to child process
    '''
    if sys.argv[0] not in ('', '-c') and not WINEXE:
        _mainpath = getattr(sys.modules['__main__'], '__file__', None)
        if _mainpath and not os.path.isabs(_mainpath):
            _mainpath = os.path.join(_dir, _mainpath)
    else:
        _mainpath = None
    return [name, _mainpath, sys.path, sys.argv, os.getcwd(), new_console]


def prepare(name, main_path, sys_path, sys_argv, curdir, new_console):
    '''
    Try to get parent __main__ module and record it as sys.module['__main__']
    '''
    processing.currentProcess().setName(name)

    if curdir is not None:
        try:
            os.chdir(curdir)
        except OSError:
            print >>sys.stderr, '*** could not change to directory %r' % curdir
            # raise
            
    if sys_path is not None:
        sys.path = sys_path
        
    if new_console:
        from processing import ProcessExit
        from processing._processing import SetConsoleCtrlHandler, NULL

        def _STOP_PROCESS_handler(signum, frame):
            raise ProcessExit

        SetConsoleCtrlHandler(NULL, False)      # don't ignore Ctrl-C
        signal.signal(signal.SIGBREAK, _STOP_PROCESS_handler)

    if main_path is not None:
        main_name = splitext(basename(main_path))[0]
        if main_name == '__init__':
            main_name = basename(dirname(main_path))
            
        if not main_path.lower().endswith('.exe') and main_name != 'ipython':
            if main_path is None:
                dirs = None
            elif equal(basename(main_path), '__init__.py'):
                dirs = [dirname(dirname(main_path))]
            else:
                dirs = [dirname(main_path)]
                
            file, pathname, etc = imp.find_module(main_name, dirs)
            try:
                main_module = imp.load_module(main_name, file, pathname, etc)
            finally:
                if file:
                    file.close()

            sys.modules['__true_main__'] = sys.modules['__main__']
            sys.modules['__main__'] = main_module
            
    if sys_argv is not None:            # this should come last 
        sys.argv = sys_argv


def main():
    '''
    Run code specifed by data passed from stdin
    '''
    assert is_forking(sys.argv)

    # get data from stdin
    preparation_data = sys.stdin.readline().rstrip()
    self_data = sys.stdin.readline().rstrip()
    
    # decode data
    preparation_data = preparation_data.decode('hex')
    self_data = self_data.decode('hex')
    
    # fix up this child process to resemble parent process
    preparation_data = cPickle.loads(preparation_data)
    prepare(*preparation_data)

    # unpickle data
    processing.currentProcess()._unpickling = True
    self = cPickle.loads(self_data)
    processing.currentProcess()._unpickling = False

    del preparation_data, self_data

    # run code of process object
    self._bootstrap()
