#
# Module providing the `SyncManager` class for dealing
# with shared objects
#
# processing/managers.py
#
# Copyright (c) 2006, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'BaseManager', 'SyncManager', 'BaseProxy', 'CreatorMethod' ]

import threading, os, types, sys, weakref, traceback

from Queue import Full, Empty
from processing.connection import Listener, Client
from processing.process import Process, currentProcess
from threading import Thread, currentThread
from cPickle import PicklingError

#
# Exception class
#

class RemoteError(Exception):
    '''
    Exception type raised by managers
    '''
    def __init__(self):
        info = sys.exc_info()
        self.args = (info[1], ''.join(traceback.format_exception(*info)))

    def __str__(self):
        return ('exception raised in manager process\n' + '-'*75 +
                '\nRemote ' + self.args[1] + '-'*75)

#
# Type for identifying shared objects
#

class Token(object):
    '''
    Type to uniquely indentify a shared object
    '''
    def __init__(self, typeid, address, id):
        self.typeid = typeid
        self.address = address
        self.id = id

    def __repr__(self):
        return 'Token(typeid=%r, address=%r, id=%r)' % \
               (self.typeid, self.address, self.id)

#
# Functions for finding the method names of an object
#

_method_types = [types.FunctionType, types.MethodType,
                 types.BuiltinFunctionType, types.BuiltinMethodType]

def all_methods(obj):
    '''
    Return a list of names of methods of `obj`
    '''
    temp = []
    for name in dir(obj):
        if type(getattr(obj, name)) in _method_types:
            temp.append(name)
    return temp

def public_methods(obj):
    '''
    Return a list of names of methods of `obj` which do not start with '_'
    '''
    return filter(lambda name: not name.startswith('_'), all_methods(obj))

#
# Server which is run in a process (or thread) controlled by a manager
#

class Server(object):
    '''
    The private part of a manager, instances of which are (usually) created
    in a subprocess or subthread
    '''
    exposed = ['shutdown', 'new', 'accept_connection', 'get_methods', 'info']
    inside_server_process = None

    def __init__(self, registry, address=None, family=None):
        self.listener = Listener(address=address, family=family, backlog=5)
        self.registry = registry
        self.address = self.listener.address
        self.id_to_obj = {}
        self.id_to_refcount = {}
        self.socket_to_name = {}
        self.socket_to_refcount = {}
        self.mutex = Lock()
        self.stop = False

    def info(self, c):
        return dict(
            len_id_to_obj = len(self.id_to_obj),
            len_id_to_refcount = len(self.id_to_refcount),
            len_socket_to_name = len(self.socket_to_name),
            len_socket_to_refcount = len(self.socket_to_refcount)
            )

    def shutdown(self, c):
        '''
        Shutdown this process --- this may not happen immediately
        '''
        self.stop = True
        
    def new(self, c, typeid, *args, **kwds):
        '''
        Create a new shared object and return it id
        '''
        Type = self.registry[typeid]
        obj = Type(*args, **kwds)
        i = id(obj)
        self.id_to_obj[i] = obj
        self.id_to_refcount[i] = 0
        return i

    def get_methods(self, c, token):
        '''
        Return the methods of the shared object indicated by token
        '''
        obj = self.id_to_obj[token.id]
        return public_methods(obj)

    def accept_connection(self, c):
        '''
        Spawn a new thread to serve this connection
        '''
        name = 'unnamed'
        self.socket_to_name[c] = name
        c.send(('#RETURN', None))
        t = Thread(target=self.serve_connection, args=[c], name=name)
        t.setDaemon(True)
        t._server = self
        t.start()

    def handle_requests(self):
        '''
        Respond to new requests -- spawns new threads when necessary
        '''
        try:
            while not self.stop:
                c = request = funcname = None

                try:
                    c = self.listener.accept()
                    request = c.recv()
                    ignore, funcname, args, kwds = request
                    assert funcname in self.exposed, \
                           '%r unrecongized' % funcname
                    func = getattr(self, funcname)
                    result = ('#RETURN', func(c, *args, **kwds))

                except (SystemExit, KeyboardInterrupt):
                    raise

                except Exception:
                    result = ('#ERROR', RemoteError())

                if funcname != 'accept_connection' or result[0] == '#ERROR':
                    try:
                        c.send(result)
                    except (SystemExit, KeyboardInterrupt):
                        raise
                    except Exception, e:
                        traceback.print_exc()
                    c.close()

        finally:
            self.listener.close()

    def serve_connection(self, connection):
        '''
        Handle requests from the proxies in a particular process/thread
        '''
        methodname = request = obj = None
        recv = connection.recv
        send = connection.send
        id_to_obj = self.id_to_obj
        self.socket_to_refcount[connection] = 0

        while not self.stop:
            
            try:
                
                methodname = None
                request = recv()
                ident, methodname, args, kwds = request
                obj = id_to_obj[ident]                
                function = getattr(obj, methodname)

                try:
                    result = function(*args, **kwds)
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception, e:
                    send(('#ERROR', e))
                else:
                    send(('#RETURN', result))
                    
            except AttributeError:

                if methodname == '#GETVALUE':
                    try:
                        send(('#RETURN', obj))                    
                    except (SystemExit, KeyboardInterrupt):
                        raise
                    except Exception:
                        send(('#ERROR', RemoteError()))

                elif methodname == '__cmp__':
                    send(('#RETURN', cmp(obj, *args)))                    

                elif methodname == '__repr__':
                    send(('#RETURN', repr(obj)))                    

                elif methodname == '__str__':
                    send(('#RETURN', str(obj)))

                elif methodname == '#DEREGISTER':
                    send(('#RETURN', None))
                    self.mutex.acquire()
                    try:
                        self.socket_to_refcount[connection] -= 1
                        self.id_to_refcount[ident] -= 1

                        if self.id_to_refcount[ident] == 0:
                            del obj, id_to_obj[ident],
                            del self.id_to_refcount[ident]

                        if self.socket_to_refcount[connection] == 0:
                            del self.socket_to_refcount[connection]
                            del self.socket_to_name[connection]
                            connection.close()
                            return
                    finally:
                        self.mutex.release()

                elif methodname == '#REGISTER':
                    send(('#RETURN', None))
                    self.mutex.acquire()
                    try:
                        self.id_to_refcount[ident] += 1
                        self.socket_to_refcount[connection] += 1
                    finally:
                        self.mutex.release()
                    
                elif methodname == '#SETNAME':
                    send(('#RETURN', None))
                    self.socket_to_name[connection] = args[0]
                    currentThread().setName(args[0])

                else:
                    send(('#ERROR', RemoteError()))

            except PicklingError:

                if hasattr(result, '__iter__') and hasattr(result, 'next'):
                    try:
                        i = id(result)
                        self.id_to_obj[i] = result
                        self.id_to_refcount[i] = 0                        
                        token = Token('iterator', self.address, i)
                        result = IteratorProxy(token, auto_connect=False)
                        send(('#RETURN', result))

                    except (SystemExit, KeyboardInterrupt):
                        raise
                    
                    except Exception:
                        send(('#ERROR', RemoteError()))
                
                else:
                    send(('#ERROR', RemoteError()))

            except (SystemExit, KeyboardInterrupt):
                raise

            except Exception:
                send(('#ERROR', RemoteError()))

#
# Definition of BaseManager
#

class BaseManager(object):
    '''
    Base class for managers

    The `spawn_type` parameter of the constructor can be either
    `Process` or `Thread`.  This determines whether the server is run
    in a subprocess or subthread.
    '''    
    def __init__(self, address=None, family=None, spawn_type=Process):
        '''
        `address`:
            The address on which manager should listen for new connections.
            If `address` is None then an arbitrary one is chosen.
            
        `family`:
            The type of connection to create if `address` is None.
            Permissible values are the strings 'AF_INET',
            'AF_UNIX', 'AF_PIPE'.  If `family` is none then a default is
            chosen.

        `spawn_type`:
            The server can be spawned either in a subprocess or subthread.
            This argument should be either `Process` or `Thread`.
        '''
        self._address = address
        self._family = family
        self._spawn_type = spawn_type        

        registry = {}
        
        for name in dir(self):
            obj = getattr(self, name)
            typeid = getattr(obj, '_typeid', None)
            if typeid is not None:
                registry[typeid] = obj._callable

        # create listener so that address of server can be retrieved
        l = Listener()
        
        # spawn process or thread which runs a server
        self._process_or_thread = self._spawn_type(
            target=_run_server,
            args=(registry, self._address, self._family, l.address),
            name=type(self).__name__ + self._spawn_type.__name__
            )
        self._process_or_thread.start()

        # retrieve the address of the server
        c = l.accept()
        try:
            self._address = c.recv()
            c.send('THANKS')
        finally:
            c.close()
            l.close()

    address = property(lambda self: self._address)

    def _newtoken(self, typeid, *args, **kwds):
        '''
        Create a new shared object and return the associated token
        '''
        c = Client(self.address)
        try:
            id = dispatch(c, None, 'new', (typeid,) + args, kwds)
            return Token(typeid, self.address, id)
        finally:
            c.close()
            
    def _info(self):
        c = Client(self.address)
        try:
            return dispatch(c, None, 'info', (), {})
        finally:
            c.close()        

    def shutdown(self):
        '''
        Shutdown the process or thread of the manager

        This is automatically called when the object is deleted
        '''
        if not getattr(self, '_finalized', False):
            c = Client(self._address)
            try:
                dispatch(c, None, 'shutdown')
                self._finalized = True
            finally:
                c.close()

    def __del__(self):
        self.shutdown()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


def _run_server(registry, address, family, temp_address):
    '''
    Instantiate a server and run it.

    This function is invoked in a subprocess or subthread.

    Really it should be a staticmethod of `BaseManager`, but that
    would cause problems with pickling.
    '''
    # create server
    server = Server(registry, address, family)
    currentThread()._server = server
    
    # inform parent process of the server's address
    c = Client(temp_address)
    try:
        c.send(server.address)
        response = c.recv()
        assert response == 'THANKS'
    finally:
        c.close()
        
    # run the manager
    server.handle_requests()

#
# Function for adding methods to managers
#

def CreatorMethod(callable, proxytype=None, exposed=None):
    '''
    Returns a method for a manager class which will create
    a shared object using `callable` and return a proxy for it.
    '''
    proxytype = proxytype or TokenToAutoProxy(exposed)
    typeid = _unique_label(callable.__name__)
                
    def temp(self, *args, **kwds):
        token = self._newtoken(typeid, *args, **kwds)
        return proxytype(token)
        
    temp.__name__ = temp._typeid = typeid
    temp._callable = callable
    return temp

def _unique_label(prefix, _count={}):
    '''
    Return a string beginning with 'prefix' which has not already been used.
    '''
    try:
        _count[prefix] += 1
    except KeyError:
        _count[prefix] = 0
        return prefix
    else:
        return prefix + '-' + str(_count[prefix])

#
# Definition of BaseProxy
#

class BaseProxy(object):
    '''
    A base for proxies of shared objects
    '''
    _key_to_connection = {}
    _socket_to_refcount = {}
    _mutex = threading.RLock()
    _id_to_proxy = weakref.WeakValueDictionary()
    
    def __init__(self, token, auto_connect=True):        
        self._token = token
        BaseProxy._id_to_proxy[id(self)] = self
        self._key = (os.getpid(), threading._get_ident(), self._token.address)
        self._id = self._token.id
        # if don't connect now take care not to muck up refcounting
        if auto_connect:
            self._reconnect()

    def _reconnect(self):
        assert not hasattr(self, '_connector')

        BaseProxy._mutex.acquire()
        try:
            connector = BaseProxy._key_to_connection.get(self._key, None)
            if connector is None:
                c = Client(self._token.address)
                dispatch(c, None, 'accept_connection')
                BaseProxy._socket_to_refcount[c] = 0
                BaseProxy._key_to_connection[self._key] = c
                self._connector = c
            else:
                self._connector = connector

            BaseProxy._socket_to_refcount[self._connector] += 1
            dispatch(self._connector, self._id, '#REGISTER')
        finally:
            BaseProxy._mutex.release()
        
    def _callmethod(self, methodname, args=(), kwds={}):
        # this method overwrites itself when it is called
        if not hasattr(self, '_connector'):
            self._reconnect()

        id = self._id
        connector = self._connector

        def _callmethod(methodname, args=(), kwds={}):
            return dispatch(connector, id, methodname, args, kwds)
        
        self._callmethod = _callmethod

        name = currentProcess().getName()
        if currentThread().getName() != 'MainThread':
            name += ':' + currentThread().getName()
        self._callmethod('#SETNAME', (name,))
        return self._callmethod(methodname, args, kwds)

    def _getvalue(self):
        return self._callmethod('#GETVALUE')

    def _close(self):
        '''
        Close the proxy

        This decrements refcounts for the shared object and the connection
        '''
        BaseProxy._mutex.acquire()
        try:
            if not hasattr(self, '_connector'):
                return

            connector = self._connector
            del self._connector

            assert connector is BaseProxy._key_to_connection[self._key]
            assert BaseProxy._socket_to_refcount[connector] >= 0

            BaseProxy._socket_to_refcount[connector] -= 1
            try:
                dispatch(connector, self._id, '#DEREGISTER', (), {})
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception:
                pass

            if BaseProxy._socket_to_refcount[connector] == 0:
                try:
                    connector.close()
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception:
                    pass
                del BaseProxy._key_to_connection[self._key]
                del BaseProxy._socket_to_refcount[connector]
        finally:
            BaseProxy._mutex.release()

    def __del__(self):
        self._close()

    def __reduce__(self):
        return (UnreduceProxy, (type(self), self._token))
    
    def __hash__(self):
        raise NotImplementedError

    def __repr__(self):
        addr = '0x%08x' % (id(self) & ((1 << 32)-1))
        return '<Proxy[%s] object at %s>' % (self._token.typeid, addr)

    def __str__(self):
        try:
            return self._callmethod('__repr__')
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            s = repr(self)
            return s[:-1] + "; failed '__str__()' call>"

#
# Functions used by BaseProxy
#

def dispatch(c, id, methodname, args=(), kwds={}):
    '''
    Send a message to manager and return its response
    '''
    c.send((id, methodname, args, kwds))
    kind, result = c.recv()
    if kind == '#RETURN':
        return result
    elif kind == '#ERROR':
        raise result
    else:
        raise ValueError


def UnreduceProxy(func, token, exposed=None):
    '''
    Function used for unpickling proxy objects.

    If possible the shared object is returned, or otherwise a proxy for it.
    '''
    server = getattr(currentThread(), '_server', None)
    
    if server and server.address == token.address:
        return server.id_to_obj[token.id]
    
    else:
        if func is AutoProxyType:
            assert exposed is not None
            func = AutoProxyType(exposed, token.typeid)
        return func(token)


def AutoProxyType(exposed, typeid='unnamed', _cache={}):
    '''
    Return a naive proxy type whose methods are given by `exposed`
    '''
    exposed = tuple(exposed)
    try:
        return _cache[(typeid, exposed)]
    except KeyError:
        pass
    
    def reducer(self):
        return (UnreduceProxy, (AutoProxyType, self._token, self._exposed))
            
    dic = { '__reduce__' : reducer, '_exposed' : exposed }
    
    for name in exposed:
        exec '''def %s(self, *args, **kwds):
        return self._callmethod(%r, args, kwds)''' % (name, name) in dic

    ProxyType = type('AutoProxy[%s]' % typeid, (BaseProxy,), dic)
    _cache[(typeid, exposed)] = ProxyType
    return ProxyType


def TokenToAutoProxy(exposed=None):
    '''
    Returns a function which creates auto-proxies for a given token
    '''
    def temp(token):
        exp = exposed
        if exp is None:
            try:
                conn = Client(token.address)
                exp = dispatch(conn, None, 'get_methods', (token,))
            finally:
                conn.close()
        return AutoProxyType(exp, token.typeid)(token)
    return temp

#
# Functions which override the default ones in `processing.process`
#

def _reset_all_proxies():
    '''
    Reset all proxies

    This is used by a (unix) child process just after it forks.
    This prevents the child process from trying to share a
    connection with its parent.
    '''
    BaseProxy._mutex.acquire()
    try:
        for proxy in BaseProxy._id_to_proxy.values():
            for key in ('_connector', '_callmethod'):
                try:
                    delattr(proxy, key)
                except AttributeError:
                    pass
                proxy._key = (os.getpid(), threading._get_ident(),
                              proxy._token.address)

    finally:
        BaseProxy._mutex.release()


def _close_all_proxies():
    '''
    Close all the proxies used in a process

    This is used immediately before a subprocess exits.
    '''
    BaseProxy._mutex.acquire()
    try:
        for proxy in BaseProxy._id_to_proxy.values():
            try:
                proxy._close()
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception:
                traceback.print_exc()  

    finally:
        BaseProxy._mutex.release()


import processing.process
processing.process._reset_all_proxies = _reset_all_proxies
processing.process._close_all_proxies = _close_all_proxies
del processing.process

#
# Types (or functions) which we will register with SyncManager
#

from threading import BoundedSemaphore, Condition, Event, \
     Lock, RLock, Semaphore
from Queue import Queue

class Namespace(object):
    '''
    Instances of this class can be used as namespaces.
    
    A namespace object has no public methods but does have writable
    attributes.  Its represention shows the values of its attributes.
    '''
    def __repr__(self):
        items = self.__dict__.items()
        temp = []
        for name, value in items:
            if not name.startswith('_'):
                temp.append('%s=%r' % (name, value))
        temp.sort()
        return 'Namespace(%s)' % str.join(', ', temp)

#
# Proxy types used by SyncManager
#

class IteratorProxy(BaseProxy):
    '''
    Proxy type for iterators
    '''
    def __iter__(self):
        return self
    def next(self):
        return self._callmethod('next')

class AcquirerProxy(BaseProxy):
    '''
    A base class for proxies which have acquire and release methods
    '''    
    def acquire(self, blocking=1):
        return self._callmethod('acquire', (blocking,))
    def release(self):
        return self._callmethod('release')
    def __enter__(self):
        self._callmethod('acquire')
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._callmethod('release')

class ConditionProxy(AcquirerProxy):
    def wait(self, timeout=None):
        return self._callmethod('wait', (timeout,))
    def notify(self):
        return self._callmethod('notify')
    def notifyAll(self):
        return self._callmethod('notifyAll')

class NamespaceProxy(BaseProxy):
    '''
    Proxy type for Namespace objects.

    Note that attributes beginning with '_' will "belong" to the proxy,
    while other attributes "belong" to the target.
    '''
    def __getattr__(self, key):
        if key.startswith('_'):
            return object.__getattribute__(self, key)
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('__getattribute__', (key,))
    
    def __setattr__(self, key, value):
        if key.startswith('_'):
            return object.__setattr__(self, key, value)
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('__setattr__', (key, value))
    
    def __delattr__(self, key):
        if key.startswith('_'):
            return object.__delattr__(self, key)
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('__delattr__', (key,))
    
ListProxy = AutoProxyType((
    '__add__', '__contains__', '__delitem__', '__delslice__',
    '__cmp__', '__getitem__', '__getslice__', '__iter__', '__len__',
    '__mul__', '__reversed__', '__rmul__', '__setitem__',
    '__setslice__', 'append', 'count', 'extend', 'index', 'insert',
    'pop', 'remove', 'reverse', 'sort'
    ))

class ListProxy(ListProxy):
    def __iadd__(self, value):
        self._callmethod('extend', (value,)) 
        return self
    def __imul__(self, value):
        # Inefficient since a copy of the target is transferred and discarded
        self._callmethod('__imul__', (value,))
        return self

#
# Definition of SyncManager
#

class SyncManager(BaseManager):
    '''
    Subclass of `BaseManager` which supports a number of shared object types.
    
    The types registered are those intended for the synchronization
    of threads, plus `dict`, `list` and `Namespace`.

    The `processing.Manager` function creates instances of this class.
    '''
    Event = CreatorMethod(Event)
    Queue = CreatorMethod(Queue)
    Lock = CreatorMethod(Lock, AcquirerProxy)
    RLock = CreatorMethod(RLock, AcquirerProxy)
    Semaphore = CreatorMethod(Semaphore, AcquirerProxy)
    BoundedSemaphore = CreatorMethod(BoundedSemaphore, AcquirerProxy)
    Condition = CreatorMethod(Condition, ConditionProxy)
    Namespace = CreatorMethod(Namespace, NamespaceProxy)
    list = CreatorMethod(list, ListProxy)
    dict = CreatorMethod(dict, exposed=(
        '__cmp__', '__contains__', '__delitem__', '__getitem__',
        '__iter__', '__len__', '__setitem__', 'clear', 'copy', 'get',
        'has_key', 'items', 'iteritems', 'iterkeys', 'itervalues',
        'keys', 'pop', 'popitem', 'setdefault', 'update', 'values'
        ))
