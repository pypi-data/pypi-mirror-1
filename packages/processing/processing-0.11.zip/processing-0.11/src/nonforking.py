#
# A kludge used by processing.py if the platform lacks os.fork
#
# processing/nonforking.py
#
# Copyright (c) 2006, Richard Oudkerk
#

# The 'NonForkingProcess.start' method spawns a new python interpreter
# running this module.  The commandline arguments passed contain
# 'self' and information about the loaded modules (encoded using
# cPickle and hexlify).
#
 

if __name__ == '__main__':

    import os, imp, sys, cPickle, cStringIO, binascii

    #
    # this searches for a module, but is probably not reliable
    #
    def get_module(name, path):        
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
        path = names_to_files.get(modulename, None)
        if modulename == '__main__':
            modulename = os.path.splitext(os.path.basename(path))[0]
        m = get_module(modulename, path)
        return getattr(m, name)

    _, names_to_files, self = sys.argv
    names_to_files = cPickle.loads(binascii.unhexlify(names_to_files))
    self = binascii.unhexlify(self)

    unpickler = cPickle.Unpickler(cStringIO.StringIO(self))
    unpickler.find_global = find_global
    self = unpickler.load()

    del unpickler, find_global, get_module, names_to_files

    self._run()

    # help __del__ be called for each proxy 
    self.__dict__.clear()
