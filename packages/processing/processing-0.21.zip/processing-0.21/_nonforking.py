#
# A kludge used by ``processing.py`` if the platform lacks ``os.fork``
#
# processing/nonforking.py
#
# Copyright (c) 2006, R Oudkerk --- see COPYING.txt
#
# The `NonForkingProcess.start` method spawns a new python interpreter
# running this module.  The commandline arguments passed contain
# `self`, the current directory and information about the loaded
# modules (encoded using `cPickle` and the `hex` codec).
#


if __name__ == '__main__':

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


    def get_module(name):
        '''
        Get a module by name

        Only modules known to `modulename_to_path` will be loaded
        '''
        parts = name.split('.')

        for i in range(len(parts)):
            subname = '.'.join(parts[:i+1])
            subpath = modulename_to_path[subname]

            try:
                m = sys.modules[subname]
                assert subpath is None or equal(m.__file__, subpath)
                continue
            except KeyError:
                pass

            if subpath is None:
                dirs = None
            elif equal(basename(subpath), '__init__.py'):
                dirs = [dirname(dirname(subpath))]
            else:
                dirs = [dirname(subpath)]
            lastname = subname.split('.')[-1]

            file, pathname, description = imp.find_module(lastname, dirs)
            try:
                m = imp.load_module(subname, file, pathname, description)
            finally:
                if file:
                    file.close()

            assert getattr(m, '__file__', None) is None or \
                   equal(m.__file__, subpath)

        return m


    def find_global(modulename, attrname):
        '''
        Return a global from a module --- used by unpickler
        '''
        if modulename == '__main__':
            modulename = main_name
        m = get_module(modulename)
        return getattr(m, attrname)


    def get_process_instance():
        '''
        Decode the commandline arguments to produce an instance of a
        subclass of NonForkingProcess
        '''
        process_instance = sys.argv[3]
        process_instance = process_instance.decode('hex')

        unpickler = cPickle.Unpickler(StringIO.StringIO(process_instance))
        unpickler.find_global = find_global
        return unpickler.load()


    def initialize():        
        '''
        Set some globals
        '''
        global modulename_to_path, main_name

        curdir = sys.argv[1].decode('hex')
        os.chdir(curdir)
        if '' not in sys.path:
            sys.path.append('')

        modulename_to_path = sys.argv[2]
        modulename_to_path = cPickle.loads(modulename_to_path.decode('hex'))

        if '__main__' in modulename_to_path:
            path = modulename_to_path['__main__']
            main_name = splitext(basename(path))[0]
            if main_name == '__init__':
                main_name = basename(dirname(path))
            assert main_name not in modulename_to_path
            modulename_to_path[main_name] = path

        processing = get_module('processing')
        processing.currentProcess()._state = 'pre-started'

        return modulename_to_path, main_name


    initialize()
    process_instance = get_process_instance()
    process_instance._run()
