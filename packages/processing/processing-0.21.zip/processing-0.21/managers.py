#
# Module providing the `SyncManager` class for dealing
# with shared objects
#
# processing/managers.py
#
# Copyright (c) 2006, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'BaseManager', 'SyncManager', 'BaseProxy', 'CreatorMethod' ]

import threading, os, sys, weakref, traceback

from processing.connection import Listener, Client, \
     deliver_challenge, answer_challenge
from processing.process import Process, currentProcess
from cPickle import PicklingError

#
# Exception class
#

class RemoteError(Exception):
    '''
    Exception type raised by managers
    '''
    def __init__(self, *args):
        if args:
            self.args = args
        else:
            info = sys.exc_info()
            self.args = (info[1], ''.join(traceback.format_exception(*info)))

    def get_exception(self):
        return self.args[0]

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
# Functions for communication with a manager's server process
#

def dispatch(c, id, methodname, args=(), kwds={}):
    '''
    Send a message to manager using connection `c` and return response
    '''
    c.send((id, methodname, args, kwds))
    kind, result = c.recv()
    if kind == '#RETURN':
        return result
    elif kind == '#ERROR':
        raise result
    else:
        raise ValueError


def transact(address, authkey, methodname, args=(), kwds={}):
    '''
    Create connection then send a message to manager and return response
    '''
    assert authkey is not None
    conn = Client(address, authkey=authkey)
    try:
        return dispatch(conn, None, methodname, args, kwds)
    finally:
        conn.close()

#
# Functions for finding the method names of an object
#

def all_methods(obj):
    '''
    Return a list of names of methods of `obj`
    '''
    temp = []
    for name in dir(obj):
        func = getattr(obj, name)
        if hasattr(func, '__call__'):
            temp.append(name)
    return temp

def public_methods(obj):
    '''
    Return a list of names of methods of `obj` which do not start with '_'
    '''
    return filter(lambda name: name[0] != '_', all_methods(obj))

#
# Server which is run in a process controlled by a manager
#

class Server(object):
    '''
    Server class which runs in a process controlled by a manager object
    '''
    public = ['shutdown', 'create', 'accept_connection',
              'getmethods', 'info']

    def __init__(self, registry, authkey, address):
        self.registry = registry
        self.authkey = authkey
        self.listener = Listener(
            address=address, backlog=5, authkey=None
            )
        self.address = self.listener.address
        self.id_to_obj = {}
        self.id_to_refcount = {}
        self.socket_to_refcount = {}
        self.mutex = threading.RLock()
        self.stop = False

    def serve_forever(self):
        '''
        Run the server forever
        '''
        try:
            while not self.stop:
                c = self.listener.accept()
                t = threading.Thread(
                    target=self.handle_request, args=[c], name='unnamed'
                    )
                t.setDaemon(True)
                t.start()
        finally:
            self.listener.close()

    def handle_request(self, c):
        '''
        Handle a new connection
        '''
        funcname = result = None
        try:
            deliver_challenge(c, self.authkey)
            answer_challenge(c, self.authkey)
            request = c.recv()
            ignore, funcname, args, kwds = request
            assert funcname in self.public, '%r unrecongized' % funcname
            func = getattr(self, funcname)

        except (SystemExit, KeyboardInterrupt):
            raise

        except Exception:
            c.send(('#ERROR', RemoteError()))

        else:
            try:
                try:
                    result = func(c, *args, **kwds)
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception:
                    c.send(('#ERROR', RemoteError()))
                else:
                    c.send(('#RETURN', result))
            finally:
                c.close()

    def serve_client(self, connection):
        '''
        Handle requests from the proxies in a particular process/thread
        '''
        recv = connection.recv
        send = connection.send
        id_to_obj = self.id_to_obj
        self.socket_to_refcount[connection] = 0

        while not self.stop:
            
            try:                
                methodname = obj = None
                request = recv()
                ident, methodname, args, kwds = request
                obj, exposed = id_to_obj[ident]

                if methodname not in exposed:
                    raise AttributeError, (
                        'method %r of %r object is not in exposed=%r' %
                        (methodname, type(obj), exposed)
                        )
                
                function = getattr(obj, methodname)

                try:
                    result = function(*args, **kwds)
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception, e:
                    send(('#ERROR', e))
                else:
                    send(('#RETURN', result))
                    
            except AttributeError, e:
                if methodname is None:
                    send(('#ERROR', RemoteError()))
                    continue

                try:
                    fallback_func = self.fallback_mapping[methodname]
                    result = fallback_func(
                        self, connection, ident, obj, *args, **kwds
                        )
                    send(('#RETURN', result))
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception:
                    send(('#ERROR', RemoteError()))

            except PicklingError:
                if hasattr(result, '__iter__') and hasattr(result, 'next'):
                    try:
                        # send a proxy for this iterator
                        res_ident, _ = self.create(None, 'iter', obj)
                        res_obj, res_exposed = self.id_to_obj[res_ident]
                        token = Token('iter', self.address, res_ident)
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

    def fallback_getvalue(self, connection, ident, obj):
        return obj

    def fallback_str(self, connection, ident, obj):
        return str(obj)

    def fallback_repr(self, connection, ident, obj):
        return repr(obj)

    def fallback_cmp(self, connection, ident, obj, *args):
        return cmp(obj, *args)
        
    def fallback_incref(self, connection, ident, obj):
        self.mutex.acquire()
        try:
            self.id_to_refcount[ident] += 1
            self.socket_to_refcount[connection] += 1
        finally:
            self.mutex.release()

    def fallback_decref(self, connection, ident, obj):
        self.mutex.acquire()
        try:
            self.socket_to_refcount[connection] -= 1
            self.id_to_refcount[ident] -= 1

            if self.id_to_refcount[ident] == 0:
                del self.id_to_obj[ident]
                del self.id_to_refcount[ident]

            if self.socket_to_refcount[connection] == 0:
                del self.socket_to_refcount[connection]
                connection.send(('#RETURN', None))
                raise SystemExit
        finally:
            self.mutex.release()
        
    fallback_mapping = {
        '__str__':fallback_str, '__repr__':fallback_repr,
        '__cmp__':fallback_cmp, '#INCREF':fallback_incref,
        '#DECREF':fallback_decref, '#GETVALUE':fallback_getvalue
        }

    def info(self, c):
        '''
        Return some info --- useful to spot problems with refcounting
        '''
        return dict(
            len_id_to_obj = len(self.id_to_obj),
            len_id_to_refcount = len(self.id_to_refcount),
            len_socket_to_refcount = len(self.socket_to_refcount)
            )

    def shutdown(self, c):
        '''
        Shutdown this process --- this may not happen immediately
        '''
        self.stop = True
        
    def create(self, c, typeid, *args, **kwds):
        '''
        Create a new shared object and return it id
        '''
        self.mutex.acquire()
        try:
            callable, exposed = self.registry[typeid]
            obj = callable(*args, **kwds)
            
            if exposed is None:
                exposed = public_methods(obj)
                
            ident = id(obj)

            self.id_to_obj[ident] = (obj, set(exposed))
            self.id_to_refcount[ident] = 0
            return ident, tuple(exposed)
        finally:
            self.mutex.release()

    def getmethods(self, c, token):
        '''
        Return the methods of the shared object indicated by token
        '''
        return tuple(self.id_to_obj[token.id][1])

    def accept_connection(self, c, name):
        '''
        Spawn a new thread to serve this connection
        '''
        threading.currentThread().setName(name)
        c.send(('#RETURN', None))
        self.serve_client(c)

#
# Definition of BaseManager
#

def _run_server(registry, authkey, address, temp_address):
    '''
    Instantiate a server and run it.

    This function is invoked in a subprocess

    Really it should be a staticmethod of `BaseManager`, but that
    would cause problems with pickling.
    '''
    # create server
    server = Server(registry, authkey, address)
    currentProcess()._inside_server = server
    
    # inform parent process of the server's address
    assert authkey is not None
    c = Client(temp_address, authkey=authkey)
    try:
        c.send(server.address)
        response = c.recv()
        assert response == 'THANKS'
    finally:
        c.close()
        
    # run the manager
    server.serve_forever()


class BaseManager(object):
    '''
    Base class for managers
    '''
    def __init__(self, address=None, authkey=None):
        '''
        `address`:
            The address on which manager should listen for new connections.
            If `address` is None then an arbitrary one is chosen.

        `authkey`:
            Only connections from clients which are using `authkey` as an
            authentication key will be accepted.  If `authkey` is `None`
            then `currentProcess().getAuthKey()` is used.
        '''
        self._address = address
        if authkey is None:
            self._authkey = authkey = currentProcess().getAuthKey()
        else:
            self._authkey = authkey

        registry = {}
        
        for name in dir(self):
            obj = getattr(self, name)
            info = getattr(obj, '_manager_info', None)
            if info is not None and hasattr(obj, '__call__'):
                typeid, callable, exposed = info
                registry[typeid] = (callable, exposed)

        # create listener so that address of server can be retrieved
        l = Listener(authkey=authkey)
        try:
            # spawn process which runs a server
            self._process = Process(
                target=self._run_server,
                args=(registry, authkey, self._address, l.address),
                name=type(self).__name__ + 'Process'
                )
            self._process.setAuthKey(self._authkey)
            self._process.start()

            # retrieve the address of the server
            c = l.accept()
            try:
                self._address = c.recv()
                c.send('THANKS')
            finally:
                c.close()
                
        finally:
            l.close()

    _run_server = staticmethod(_run_server)

    address = property(lambda self: self._address)

    def _create(self, typeid, *args, **kwds):
        '''
        Create a new shared object; return the token and exposed tuple
        '''
        id, exposed = transact(
            self._address, self._authkey, 'create', (typeid,) + args, kwds
            )
        return Token(typeid, self._address, id), exposed
            
    def _info(self):
        return transact(self._address, self._authkey, 'info')

    def shutdown(self):
        '''
        Shutdown the process of the manager

        This is automatically called when the object is deleted
        '''
        if not getattr(self, '_finalized', False):
            try:
                transact(self._address, self._authkey, 'shutdown')
                transact(self._address, self._authkey, 'shutdown')
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception:
                pass
            self._finalized = True
            self._process.join()

    def __del__(self):
        self.shutdown()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

#
# Function for adding methods to managers
#

def CreatorMethod(callable, proxytype=None, exposed=None):
    '''
    Returns a method for a manager class which will create
    a shared object using `callable` and return a proxy for it.
    '''
    if exposed is None and hasattr(callable, '__exposed__'):
        exposed = callable.__exposed__

    typeid = _unique_label(callable.__name__)
                
    def temp(self, *args, **kwds):
        token, exp = self._create(typeid, *args, **kwds)
        if proxytype is None:
            return MakeAutoProxy(token, authkey=self._authkey, exposed=exp)
        else:
            return proxytype(token, authkey=self._authkey)
        
    temp.__name__ = typeid
    temp._manager_info = (typeid, callable, exposed)
    return temp

def _unique_label(prefix, _count={}):
    '''
    Return a string beginning with 'prefix' which has not already been used.
    '''
    try:
        _count[prefix] += 1
        return prefix + '-' + str(_count[prefix])
    except KeyError:
        _count[prefix] = 0
        return prefix

#
# Definition of BaseProxy
#

class _Private(object):
    # These could be class attributes of BaseProxy or globals
    _key_to_socket = {}
    _socket_to_refcount = {}
    _mutex = threading.RLock()
    _id_to_proxy = weakref.WeakValueDictionary()


class BaseProxy(object):
    '''
    A base for proxies of shared objects
    '''
    def __init__(self, token, auto_connect=True, authkey=None):
        self._token = token
        _Private._id_to_proxy[id(self)] = self
        self._key = (os.getpid(), threading._get_ident(), self._token.address)
        self._id = self._token.id

        # if we don't connect now then we must worry about refcounting
        if auto_connect:
            self._connect(authkey)

    def _connect(self, authkey):
        assert not hasattr(self, '_connector')

        if authkey is None:
            authkey = currentProcess().getAuthKey()

        _Private._mutex.acquire()
        try:
            connector = _Private._key_to_socket.get(self._key, None)
            if connector is None:
                name = currentProcess().getName()
                if threading.currentThread().getName() != 'MainThread':
                    name += '|' + threading.currentThread().getName()
                connector = Client(self._token.address, authkey=authkey)
                dispatch(connector, None, 'accept_connection', (name,))
                _Private._socket_to_refcount[connector] = 0
                _Private._key_to_socket[self._key] = connector

            self._connector = connector
            _Private._socket_to_refcount[connector] += 1
            self._callmethod('#INCREF')            
        finally:
            _Private._mutex.release()

    def _callmethod(self, methodname, args=(), kwds={}):
        '''
        Try to call a method of the referrent and return a copy of the result
        '''
        return dispatch(self._connector, self._id, methodname, args, kwds)

    def _getvalue(self):
        '''
        Get a copy of the value of the referent
        '''
        return self._callmethod('#GETVALUE')

    def _close(self):
        '''
        Close the proxy

        This decrements refcounts for the shared object and the connection
        '''
        _Private._mutex.acquire()
        try:
            if not hasattr(self, '_connector'):
                return

            connector = self._connector
            del self._connector

            assert connector is _Private._key_to_socket[self._key]
            assert _Private._socket_to_refcount[connector] >= 0

            _Private._socket_to_refcount[connector] -= 1
            try:
                dispatch(connector, self._token.id, '#DECREF', (), {})
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception:
                pass

            if _Private._socket_to_refcount[connector] == 0:
                try:
                    connector.close()
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception:
                    pass
                del _Private._key_to_socket[self._key]
                del _Private._socket_to_refcount[connector]

        finally:
            _Private._mutex.release()

    def __del__(self):
        self._close()

    def __reduce__(self):
        if hasattr(self, '_exposed'):
            return (RebuildProxy, (MakeAutoProxy, self._token,
                                   {'exposed':self._exposed}))
        else:
            return (RebuildProxy, (type(self), self._token))

    def __hash__(self):
        raise NotImplementedError

    def __repr__(self):
        addr = '0x%08x' % (id(self) & 0xFFFFFFFF)
        return '<Proxy[%s] object at %s>' % (self._token.typeid, addr)

    def __str__(self):
        '''
        Return representation of the referent (or a fall-back if that fails)
        '''
        try:
            return self._callmethod('__repr__')
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            return repr(self)[:-1] + "; '__str__()' falled>"

#
# Function used for unpickling
#

def RebuildProxy(func, token, kwds={}):
    '''
    Function used for unpickling proxy objects.

    If possible the shared object is returned, or otherwise a proxy for it.
    '''
    server = getattr(currentProcess(), '_inside_server', None)
    
    if server and server.address == token.address:
        return server.id_to_obj[token.id][0]    
    else:
        auto_connect = (currentProcess()._state != 'pre-started')
        return func(token, auto_connect=auto_connect, authkey=None, **kwds)

#
# Functions to create proxies and proxy types
#

def MakeAutoProxyType(exposed, typeid='unnamed', _cache={}):
    '''
    Return an auto-proxy type whose methods are given by `exposed`
    '''
    exposed = tuple(exposed)
    try:
        return _cache[(typeid, exposed)]
    except KeyError:
        pass
    
    dic = {}
    
    for name in exposed:
        exec '''def %s(self, *args, **kwds):
        return self._callmethod(%r, args, kwds)''' % (name, name) in dic

    ProxyType = type('AutoProxy[%s]' % typeid, (BaseProxy,), dic)
    ProxyType._exposed = exposed
    _cache[(typeid, exposed)] = ProxyType
    return ProxyType


def MakeAutoProxy(token, auto_connect=True, authkey=None, exposed=None):
    '''
    Return an auto-proxy for `token`
    '''
    if exposed is None:
        exposed = transact(token.address, authkey, 'getmethods', (token,))
    ProxyType = MakeAutoProxyType(exposed, token.typeid)
    proxy = ProxyType(token, auto_connect=auto_connect, authkey=authkey)
    proxy._exposed = exposed
    return proxy

#
# Functions which override the default ones in `processing.process`
#

def _reset_all_proxies():
    '''
    Reset all proxies
    '''
    _Private._mutex.acquire()
    try:
        for proxy in _Private._id_to_proxy.values():
            try:
                del proxy._connector
            except AttributeError:
                pass
            proxy._key = (os.getpid(), threading._get_ident(),
                          proxy._token.address)
            
            proxy._connect(authkey=None)
    finally:
        _Private._mutex.release()

def _close_all_proxies():
    '''
    Close all proxies
    '''
    _Private._mutex.acquire()
    try:
        for proxy in _Private._id_to_proxy.values():
            try:
                proxy._close()
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception:
                traceback.print_exc()
    finally:
        _Private._mutex.release()


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
    __exposed__ = ('__getattribute__', '__setattr__', '__delattr__')
    
    def __repr__(self):
        items = self.__dict__.items()
        temp = []
        for name, value in items:
            if not name.startswith('_'):
                temp.append('%s=%r' % (name, value))
        temp.sort()
        return 'Namespace(%s)' % str.join(', ', temp)

#
# Proxy type used by BaseManager
#

class IteratorProxy(BaseProxy):
    '''
    Proxy type for iterators
    '''    
    def __iter__(self):
        return self
    def next(self):
        return self._callmethod('next')

BaseManager._Iter = CreatorMethod(iter, IteratorProxy, ('next', '__iter__'))

#
# Proxy types used by SyncManager
#

class AcquirerProxy(BaseProxy):
    '''
    Base class for proxies which have acquire and release methods
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
    while other attributes "belong" to the referent.
    '''    
    def __getattr__(self, key):
        if key[0] == '_':
            return object.__getattribute__(self, key)
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('__getattribute__', (key,))
    
    def __setattr__(self, key, value):
        if key[0] == '_':
            return object.__setattr__(self, key, value)
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('__setattr__', (key, value))
    
    def __delattr__(self, key):
        if key[0] == '_':
            return object.__delattr__(self, key)
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('__delattr__', (key,))


_list_exposed = (
    '__add__', '__contains__', '__delitem__', '__delslice__',
    '__cmp__', '__getitem__', '__getslice__', '__iter__', '__imul__',
    '__len__', '__mul__', '__reversed__', '__rmul__', '__setitem__',
    '__setslice__', 'append', 'count', 'extend', 'index', 'insert',
    'pop', 'remove', 'reverse', 'sort'
    )

ListProxy = MakeAutoProxyType(_list_exposed)

class ListProxy(ListProxy):
    # augmented assignment functions must return self
    def __iadd__(self, value):
        self._callmethod('extend', (value,)) 
        return self
    def __imul__(self, value):
        # Inefficient since a copy of the target is transferred and discarded
        self._callmethod('__imul__', (value,))
        return self

    
_dict_exposed=(
    '__cmp__', '__contains__', '__delitem__', '__getitem__',
    '__iter__', '__len__', '__setitem__', 'clear', 'copy', 'get',
    'has_key', 'items', 'iteritems', 'iterkeys', 'itervalues',
    'keys', 'pop', 'popitem', 'setdefault', 'update', 'values'
    )

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
    list = CreatorMethod(list, ListProxy, exposed=_list_exposed)
    dict = CreatorMethod(dict, exposed=_dict_exposed)

