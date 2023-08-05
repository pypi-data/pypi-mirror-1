#
# A kludge used by ``processing.py`` if the platform lacks ``os.fork``
#
# processing/nonforking.py
#
# Copyright (c) 2006, R Oudkerk --- see COPYING.txt
#
# The ``NonForkingProcess.start`` method spawns a new python interpreter
# running this module.  The commandline arguments passed contain
# ``self`` and information about the loaded modules (encoded using
# ``cPickle`` and the ``hex`` codec).
#
 

if __name__ == '__main__':

    import os, sys, imp, cPickle, cStringIO

    def get_module(name, path):        
        '''
        Loads and returns a module given its name and path
        '''        
        try:
            exec 'import %s as m' % name
        except ImportError:
            pass
        else:
            if (path is None or not hasattr(m, '__file__') or
                os.path.splitext(path)[0] == os.path.splitext(m.__file__)[0]):
                return m

        names = name.split('.')
        if len(names) > 1:
            for n in names:
                m = get_module(n, path)
            return m

        assert path is not None

        dir = os.path.split(path)[0]
        while 1:
            try:
                file, pathname, description = imp.find_module(name, [dir])
            except ImportError:
                dir = os.path.split(dir)[0]
            else:
                break
        else:
            raise ImportError

        m = imp.load_module(name, file, pathname, description)

        if file:
            file.close()
        return m


    def find_global(modulename, name):
        '''
        Return a global from a module
        '''
        path = names_to_files.get(modulename, None)
        if modulename == '__main__':
            modulename = os.path.splitext(os.path.basename(path))[0]
        m = get_module(modulename, path)
        return getattr(m, name)


    def get_process_instance():
        '''
        Decode the commandline arguments to produce an instance of a
        subclass of NonForkingProcess
        '''
        global names_to_files

        _, names_to_files, process_instance = sys.argv
        names_to_files = cPickle.loads(names_to_files.decode('hex'))
        process_instance = process_instance.decode('hex')
        
        unpickler = cPickle.Unpickler(cStringIO.StringIO(process_instance))
        unpickler.find_global = find_global
        return unpickler.load()



    process_instance = get_process_instance()

    try:
        process_instance._run()
        
    finally:
        from processing.process import _close_all_proxies
        _close_all_proxies()
