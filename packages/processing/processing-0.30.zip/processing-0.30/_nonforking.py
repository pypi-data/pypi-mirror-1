#
# A kludge used by `processing.py` because windows lacks `os.fork()`
#
# processing/fork.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#
# The `Process.start()` method spawns a new python interpreter running
# this module.  The commandline arguments passed contain `self`, and
# information about the loaded modules (encoded using `cPickle` and
# the `hex` codec).
#


import os, sys, imp, cPickle, StringIO, pkgutil
from os.path import dirname, splitext, basename, abspath

if not hasattr(pkgutil, 'get_loader'):
    from processing.compat import pkgutil


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


def get_module(name):
    path = modulename_to_path[name]
    
    if name in sys.modules:
        m = sys.modules[name]
    else:
        loader = pkgutil.get_loader(name)
        if loader is None:
            raise ImportError, 'could not find module %s, %r' % (name, path)
        m = loader.load_module(name)
        
    assert path is None or equal(m.__file__, path)
    return m
    

def find_global(modulename, attrname):
    if modulename == '__main__':
        m = main_module
    else:
        m = get_module(modulename)
    return getattr(m, attrname)


def get_process_instance(mdata, sdata):
    '''
    Return the process instance
    '''
    global modulename_to_path, main_module

    modules_data = mdata.decode('hex')
    self_data = sdata.decode('hex')

    if '' not in sys.path:
        sys.path.append('')

    modulename_to_path = cPickle.loads(modules_data)

    if '__main__' in modulename_to_path:
        path = modulename_to_path['__main__']
        main_name = splitext(basename(path))[0]
        if main_name == '__init__':
            main_name = basename(dirname(path))

        if main_name and not path.endswith('.exe') and main_name != 'ipython':
            if path is None:
                dirs = None
            elif equal(basename(path), '__init__.py'):
                dirs = [dirname(dirname(path))]
            else:
                dirs = [dirname(path)]

            file, pathname, etc = imp.find_module(main_name, dirs)
            try:
                main_module = imp.load_module(main_name, file, pathname, etc)
            finally:
                if file:
                    file.close()
                    
            sys.modules['__true_main__'] = sys.modules['__main__']
            sys.modules['__main__'] = main_module
            
    processing = get_module('processing')
    processing.currentProcess()._unpickling = True
    
    unpickler = cPickle.Unpickler(StringIO.StringIO(self_data))
    unpickler.find_global = find_global
    process_instance = unpickler.load()

    processing.currentProcess()._unpickling = False
                
    return process_instance        


def run(mdata, sdata):
    try:
        import processing._processing
    except ImportError:
        pass
    else:
        processing._processing.InheritCtrlC(True)
        
    self = get_process_instance(mdata, sdata)
    self._bootstrap()    
    
    
if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
