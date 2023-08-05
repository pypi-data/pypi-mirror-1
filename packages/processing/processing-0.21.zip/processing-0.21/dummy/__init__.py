#
# Support for the API of the processing package using threads
#
# processing/dummy/__init__.py
#
# Copyright (c) 2006, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'Process', 'currentProcess', 'Manager' ]

import threading

from processing.dummy.managers import SyncManager as Manager

class DummyProcess(threading.Thread):
    def getAuthKey(self):
        pass
    def setAuthKey(self, value=None):
        pass

Process = DummyProcess
currentProcess = threading.currentThread
