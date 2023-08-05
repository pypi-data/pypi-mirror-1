#
# A kludge used by `processing` package because windows lacks `os.fork()`
#
# processing/fork.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#
# The `Process.start()` method spawns a new python interpreter which
# runs the `run()` function of this module.  The commandline arguments
# passed contain `self`, and information about the loaded modules
# (encoded using `cPickle` and the `hex` codec).
#

__all__ = []


import os, sys, imp, cPickle, StringIO
from os.path import dirname, splitext, basename, abspath


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


def prepare(main_path, sys_path, curdir):
    '''
    Try to get parents __main__ module and record it as sys.module['__main__']
    '''
    if curdir is not None:
        try:
            os.chdir(curdir)
        except OSError:
            print >>sys.stderr, 'could not change to directory %r' % curdir
            # raise
            
    if sys_path is not None:
        sys.path = sys_path

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


def run(preparation_data, self_data):
    '''
    Run code specifed by encoded process object
    '''
    preparation_data = preparation_data.decode('hex')
    self_data = self_data.decode('hex')
    
    # on Windows try to inherit SIGINT signals from console
    try:
        from processing import _processing
        if hasattr(_processing, 'InheritCtrlC'):
            _processing.InheritCtrlC(True)
    except ImportError:
        pass

    # fix up this child process to resemble parent process
    preparation_data = cPickle.loads(preparation_data)
    prepare(*preparation_data)

    # unpickle data
    import processing
    processing.currentProcess()._unpickling = True
    self = cPickle.loads(self_data)
    processing.currentProcess()._unpickling = False

    # run code of process object
    self._bootstrap()


if __name__ == '__main__':
    assert len(sys.argv) == 3
    run(sys.argv[1], sys.argv[2])
