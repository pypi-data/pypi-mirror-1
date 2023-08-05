#
# Support for the API of the processing package using threads
#
# processing/dummy/__init__.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'Process', 'currentProcess', 'activeChildren',
            'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore',
            'Condition', 'Event', 'Queue',
            'Manager', 'LocalManager', 'Pipe'
            ]

import threading, sys

from processing.dummy.managers import SyncManager as Manager
from processing.dummy.connection import Pipe
from threading import Lock, RLock, Semaphore, BoundedSemaphore, \
         Condition, Event
from Queue import Queue, Full, Empty

LocalManager = Manager

class DummyProcess(threading.Thread):

    _count = 1
    
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        if name is None:
            name = 'Thread-%s' % Process._count
        Process._count += 1
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._pid = None

    def _Thread__bootstrap(self):
        self._pid = threading._get_ident()
        threading.Thread._Thread__bootstrap(self)

    def getAuthKey(self):
        pass
    
    def setAuthKey(self, value):
        pass
    
    def getExitCode(self):
        if self._Thread__stopped:
            return 0
        else:
            return None

    def getPid(self):
        return self._pid

Process = DummyProcess
currentProcess = threading.currentThread

def activeChildren():
    pass
