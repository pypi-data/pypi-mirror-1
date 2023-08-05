#
# Analogue of `processing.connection` which uses queues instead of sockets
#
# processing/dummy/connection.py
#
# Copyright (c) 2006, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'Client', 'Listener' ]

from Queue import Queue

class Connection(object):
    def __init__(self, _in, _out):
        self.send = self.send_string = _out.put
        self.recv = self.recv_string = _in.get
        
class Listener(object):
    def __init__(self, address=None, family=None, backlog=1):
        self._backlog_queue = Queue(backlog)
    def accept(self):
        return Connection(*self._backlog_queue.get())
    address = property(lambda self: self)

def Client(address):
    _in, _out = Queue(), Queue()
    address._backlog_queue.put((_out, _in))
    return Connection(_in, _out)
