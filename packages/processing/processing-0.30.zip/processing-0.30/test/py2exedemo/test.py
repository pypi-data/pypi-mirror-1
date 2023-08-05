#
# This file is just a wrapper around `_test.py` to support freezing by py2exe
#
# To modify it for your own projects set `__main_function__` to be
# the main entry point of the program
#

from _test import main as __main_function__

#
# Don't edit the rest of this file
#

import sys, processing

if __name__ == '__main__':
    
    if (sys.argv[0].endswith('.exe') and
        not sys.argv[0].lower().endswith('python.exe')):
        
        processing.currentProcess()._fork_commandline = [sys.argv[0], '--fork']

        if len(sys.argv) > 1 and sys.argv[1] == '--fork':
            processing._nonforking.run(sys.argv[2], sys.argv[3])
        else:
            __main_function__()
    else:
            __main_function__()
    
