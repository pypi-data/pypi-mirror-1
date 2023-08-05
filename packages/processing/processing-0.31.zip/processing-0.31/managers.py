#
# Module providing the `SyncManager` class for dealing
# with shared objects
#
# processing/managers.py
#
# Copyright (c) 2006, 2007, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'BaseManager', 'SyncManager', 'BaseProxy',
            'CreatorMethod', 'Token' ]

import threading, os, sys, weakref, traceback, array, copy_reg

from processing.connection import Listener, Client, \
     deliver_challenge, answer_challenge, AuthenticationError
from processing.process import Process, currentProcess, Finalize
from cPickle import PicklingError

#
# Register `array.array` for pickling
#

def reduce_array(a):
    return array.array, (a.typecode, a.tostring())

copy_reg.pickle(array.array, reduce_array)

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
            
    def __str__(self):
        return ('\n' + '-'*75 + '\nRemote ' + self.args[1] + '-'*75)
            
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
        return 'Token(typeid=%r, address=%s, id=%s)' % \
               (self.typeid, self.address, '0x%x' % (self.id & 0xffffffff))

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
              'getmethods', 'debug_info', 'dummy']

    def __init__(self, registry, address, authkey):
        assert type(authkey) is str
        self.registry = registry
        self.authkey = authkey

        # do authentication later
        self.listener = Listener(address=address, backlog=5)  

        self.address = self.listener.address
        if type(self.address) is tuple:
            import socket
            self.address = (socket.getfqdn(self.address[0]), self.address[1])

        self.id_to_obj = {}
        self.id_to_refcount = {}
        self.connection_to_idset = {}
        self.mutex = threading.RLock()
        self.stop = 0

    def serve_forever(self):
        '''
        Run the server forever
        '''
        try:
            try:
                while 1:
                    c = self.listener.accept()
                    t = threading.Thread(target=self.handle_request, args=[c])
                    t.setDaemon(True)
                    t.start()
            except KeyboardInterrupt:
                pass
        finally:
            self.stop = 999
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
            msg = ('#ERROR', RemoteError())
        else:
            try:
                result = func(c, *args, **kwds)
                msg = ('#RETURN', result)
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception:
                msg = ('#ERROR', RemoteError())

        try:
            c.send(msg)
        except (SystemExit, KeyboardInterrupt):
            raise
        except:
            if msg[0] == '#ERROR':
                print >>sys.stderr, 'Failure to send exception: %s' % msg[1]
            else:
                print >>sys.stderr, 'Failure to send result: %s' % msg[1]
            print >>sys.stderr

        self.mutex.acquire()
        try:
            if c in self.connection_to_idset:
                del self.connection_to_idset[c]
        finally:
            self.mutex.release()
            c.close()

    def serve_client(self, connection):
        '''
        Handle requests from the proxies in a particular process/thread
        '''
        recv = connection.recv
        send = connection.send
        id_to_obj = self.id_to_obj
        
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
                    msg = ('#RETURN', result)
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception, e:
                    msg = ('#ERROR', e)
                                    
            except AttributeError, e:
                if methodname is None:
                    msg = ('#ERROR', RemoteError())
                else:
                    try:
                        fallback_func = self.fallback_mapping[methodname]
                        result = fallback_func(
                            self, connection, ident, obj, *args, **kwds
                            )
                        msg = ('#RETURN', result)
                    except (SystemExit, KeyboardInterrupt):
                        raise
                    except Exception:
                        msg = ('#ERROR', RemoteError())

            except (SystemExit, KeyboardInterrupt):
                raise

            except Exception:
                msg = ('#ERROR', RemoteError())

            try:
                try:
                    send(msg)
                except PicklingError:
                    result = msg[1]
                    if hasattr(result, '__iter__') and hasattr(result, 'next'):
                        try:
                            # send a proxy for this iterator
                            res_ident, _ = self.create(
                                connection, 'iter', result
                                )
                            res_obj, res_exposed = self.id_to_obj[res_ident]
                            token = Token('iter', self.address, res_ident)
                            result = IteratorProxy(token, auto_connect=False)
                            msg = ('#RETURN', result)
                        except (SystemExit, KeyboardInterrupt):
                            raise
                        except Exception:
                            msg = ('#ERROR', RemoteError())
                    else:
                        msg = ('#ERROR', RemoteError())
                    send(msg)
            except (SystemExit, KeyboardInterrupt):
                raise
            except:
                idset = self.connection_to_idset.pop(connection, None)
                connection.close()
                sys.exit(1)

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
            try:
                self.id_to_refcount[ident] += 1
            except TypeError:
                assert self.id_to_refcount[ident] is None
                self.id_to_refcount[ident] = 1
            self.connection_to_idset[connection].add(ident)
        finally:
            self.mutex.release()

    def fallback_decref(self, connection, ident, obj):
        self.mutex.acquire()
        try:
            self.connection_to_idset[connection].remove(ident)
            self.id_to_refcount[ident] -= 1

            if self.id_to_refcount[ident] == 0:
                del self.id_to_obj[ident]
                del self.id_to_refcount[ident]

            if not self.connection_to_idset[connection]:
                del self.connection_to_idset[connection]
                connection.send(('#RETURN', None))
                sys.exit()
        finally:
            self.mutex.release()
        
    fallback_mapping = {
        '__str__':fallback_str, '__repr__':fallback_repr,
        '__cmp__':fallback_cmp, '#INCREF':fallback_incref,
        '#DECREF':fallback_decref, '#GETVALUE':fallback_getvalue
        }

    def dummy(self, c):
        pass

    def debug_info(self, c):
        '''
        Return some info --- useful to spot problems with refcounting
        '''
        self.mutex.acquire()
        try:
            result = []
            result.append('Object reference counts:')
            
            for ident in sorted(self.id_to_obj):
                result.append('  %s:       refcount=%s\n    %s' %
                              (hex(ident), self.id_to_refcount[ident],
                               str(self.id_to_obj[ident][0])[:75]))

            result.append('\nConnections and the objects they reference:')

            for conn, ids in sorted(self.connection_to_idset.items()):
                result.append('  %s:' % conn)
                for ident in ids:
                    result.append('    %s: %s' %
                        (hex(ident), str(self.id_to_obj[ident][0])[:63]))
        finally:
            self.mutex.release()

        if len(result) > 2:
            return '\n'.join(result)
    
    def shutdown(self, c):
        '''
        Shutdown this process --- this may not happen immediately
        '''
        import thread
        thread.interrupt_main()
        
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
            self.id_to_refcount[ident] = None
            self.connection_to_idset.get(c, set()).add(ident)
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
        self.connection_to_idset[c] = set()
        self.serve_client(c)

#
# Definition of BaseManager
#

def _run_server(registry, address, authkey, parent_address):
    '''
    Instantiate a server and run it.

    This function is invoked in a subprocess

    Really it should be a staticmethod of `BaseManager`, but that
    would cause problems with pickling.
    '''
    # create server
    server = Server(registry, address, authkey)
    currentProcess()._server = server
    
    # inform parent process of the server's address
    connection = Client(parent_address)
    connection.send(server.address)
    connection.close()
    
    # run the manager
    server.serve_forever()


class BaseManager(object):
    '''
    Base class for managers
    '''
    def __init__(self, address=None, authkey=None):
        '''
        `address`:
            The address on which manager should listen for new
            connections.  If `address` is None then an arbitrary one
            is chosen (which will be available as `self.adress`).

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
        assert type(authkey) is str
        self._started = False

    def start(self):
        '''
        Spawn a server process for this manager object
        '''
        assert not self._started
        self._started = True
        
        self._registry, _ = BaseManager._get_registry_creators(self)

        # create a listener so that address of server can be retrieved
        l = Listener()

        # spawn process which runs a server
        self._process = Process(
            target=self._run_server,
            args=(self._registry, self._address, self._authkey, l.address),
            name=type(self).__name__ + 'Process'
            )
        self._process.setAuthKey(self._authkey)
        try:
            self._process.setDaemon(True)
        except AssertionError:
            pass
        self._process.start()

        # get address of server
        conn = l.accept()
        self._address = conn.recv()
        conn.close()
        l.close()

        # register a finalizer
        self.shutdown = Finalize(
            self, BaseManager._finalize,
            args=(self._process, self._address, self._authkey)
            )
        
    def serve_forever(self):
        '''
        Start server in the current process
        '''
        assert not self._started
        self._started = True
        registry, _ = BaseManager._get_registry_creators(self)
        server = Server(registry, self._address, self._authkey)
        currentProcess()._server = server
        print >>sys.stderr, '%s serving at address %s' % \
              (type(self).__name__, server.address)
        server.serve_forever()

    def connect(self):
        '''
        Associate `self` with a pre-existing server process
        '''
        transact(self._address, self._authkey, 'dummy')
        self._started = True

    def _create(self, typeid, *args, **kwds):
        '''
        Create a new shared object; return the token and exposed tuple
        '''
        assert self._started
        id, exposed = transact(
            self._address, self._authkey, 'create', (typeid,) + args, kwds
            )
        return Token(typeid, self._address, id), exposed
    
    def join(self, timeout=None):
        '''
        Join the manager process (if it has been spawned)
        '''
        self._process.join(timeout)
        
    def _debug_info(self):
        '''
        Return some info about the servers shared objects and connections
        '''
        return transact(self._address, self._authkey, 'debug_info')

    def _proxy_from_token(self, token):
        '''
        Create a proxy for a token
        '''
        assert token.address == self.address
        _, creators = BaseManager._get_registry_creators(self)
        proxytype = creators[token.typeid]._proxytype
        return proxytype(token, authkey=self._authkey)
        
    @staticmethod
    def _get_registry_creators(self_or_cls):
        registry = {}
        creators = {}
        for name in dir(self_or_cls):
            obj = getattr(self_or_cls, name)
            info = getattr(obj, '_manager_info', None)
            if info is not None and hasattr(obj, '__call__'):
                creators[name] = obj
                typeid, callable, exposed = info
                assert typeid not in registry, 'typeids must be unique'
                registry[typeid] = (callable, exposed)
        return registry, creators

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    @staticmethod
    def _finalize(process, address, authkey):
        '''
        Shutdown the manager process; will be registered as a finalizer
        '''
        if process.isAlive():
            try:
                transact(address, authkey, 'shutdown')
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception:
                pass
            
            process.join(timeout=0.1)
            if process.isAlive():
                #print >>sys.stderr, "*** failed to stop manager gracefully"
                if hasattr(process, 'stop'):
                    #print >>sys.stderr, "*** stoppping manager ungracefully"
                    process.stop()

    _run_server = staticmethod(_run_server)

    address = property(lambda self: self._address)
    
#
# Function for adding methods to managers
#

def CreatorMethod(callable=None, proxytype=None, exposed=None, typeid=None):
    '''
    Returns a method for a manager class which will create
    a shared object using `callable` and return a proxy for it.
    '''
    if exposed is None and hasattr(callable, '__exposed__'):
        exposed = callable.__exposed__

    if proxytype is None:
        proxytype = MakeAutoProxy

    typeid = typeid or _unique_label(callable.__name__)
            
    def temp(self, *args, **kwds):
        token, exp = self._create(typeid, *args, **kwds)
        return proxytype(token, authkey=self._authkey, exposed=exp)
        
    temp.__name__ = typeid
    temp._manager_info = (typeid, callable, exposed)
    temp._proxytype = proxytype
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
    _connection_to_refcount = {}
    _mutex = threading.RLock()
    _id_to_proxy = weakref.WeakValueDictionary()


class BaseProxy(object):
    '''
    A base for proxies of shared objects
    '''
    def __init__(self, token, authkey=None, exposed=None, auto_connect=True):
        self._token = token
        _Private._id_to_proxy[id(self)] = self
        self._key = (os.getpid(), threading._get_ident(), self._token.address)
        self._id = self._token.id
        
        # if we don't connect now then we must worry about refcounting
        if auto_connect:
            self._connect(authkey)
            
    def _connect(self, authkey, name=None):
        assert not hasattr(self, '_connection')

        if authkey is None:
            authkey = currentProcess().getAuthKey()

        _Private._mutex.acquire()
        try:
            if self._key in _Private._key_to_socket:
                self._connection = _Private._key_to_socket[self._key]
                try:
                    self._callmethod('#INCREF')
                except RemoteError:
                    del self._connection
                    raise KeyError, 'token not found: %s' % self._token
                else:
                    _Private._connection_to_refcount[self._connection] += 1
            else:
                if name is None:
                    name = currentProcess().getName()
                    if threading.currentThread().getName() != 'MainThread':
                        name += '|' + threading.currentThread().getName()
                        
                connection = Client(
                    self._token.address, authkey=authkey
                    )
                
                dispatch(connection, None, 'accept_connection', (name,))
                try:
                    dispatch(connection, self._id, '#INCREF')
                except RemoteError:
                    connection.close()
                    raise KeyError, 'token not found: %s' % self._token
                else:
                    _Private._connection_to_refcount[connection] = 1
                    _Private._key_to_socket[self._key] = connection
                    self._connection = connection
        finally:
            _Private._mutex.release()

    def _callmethod(self, methodname, args=(), kwds={}):
        '''
        Try to call a method of the referrent and return a copy of the result
        '''
        return dispatch(self._connection, self._id, methodname, args, kwds)
            
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
            if not hasattr(self, '_connection'):
                return

            connection = self._connection
            del self._connection

            assert connection is _Private._key_to_socket[self._key]
            assert _Private._connection_to_refcount[connection] >= 0

            _Private._connection_to_refcount[connection] -= 1
            try:
                dispatch(connection, self._token.id, '#DECREF', (), {})
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception:
                pass

            if _Private._connection_to_refcount[connection] == 0:
                connection.close()
                del _Private._key_to_socket[self._key]
                del _Private._connection_to_refcount[connection]

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
        return '<Proxy[%s] object at %s>' % (self._token.typeid,
                                             '0x%x' % (id(self) & 0xffffffff))
    
    def __str__(self):
        '''
        Return representation of the referent (or a fall-back if that fails)
        '''
        try:
            return self._callmethod('__repr__')
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            return repr(self)[:-1] + "; '__str__()' failed>"

#
# Function used for unpickling
#

def RebuildProxy(func, token, kwds={}):
    '''
    Function used for unpickling proxy objects.

    If possible the shared object is returned, or otherwise a proxy for it.
    '''
    server = getattr(currentProcess(), '_server', None)
    
    if server and server.address == token.address:
        return server.id_to_obj[token.id][0]    
    else:
        auto_connect = not getattr(currentProcess(), '_unpickling', False)
        try:
            return func(token, authkey=None, auto_connect=auto_connect, **kwds)
        except AuthenticationError:
            raise AuthenticationError, 'cannot rebuild proxy without authkey'
    
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


def MakeAutoProxy(token, authkey=None, exposed=None, auto_connect=True):
    '''
    Return an auto-proxy for `token`
    '''
    if exposed is None:
        exposed = transact(token.address, authkey, 'getmethods', (token,))
    ProxyType = MakeAutoProxyType(exposed, token.typeid)
    proxy = ProxyType(token, authkey=authkey, auto_connect=auto_connect)
    proxy._exposed = exposed
    return proxy

#
# Functions which override the default ones in `processing.process`
#

def _reset_all_proxies(authkey, process_name):
    '''
    Reset all proxies
    '''
    _Private._mutex.acquire()
    try:
        for proxy in _Private._id_to_proxy.values():
            if hasattr(proxy, '_connection'):
                del proxy._connection
            proxy._key = (os.getpid(), threading._get_ident(),
                          proxy._token.address)
            try:
                proxy._connect(authkey=authkey, name=process_name)
            except KeyError:
                pass
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

class SharedValue(object):
    '''
    Instances have a settable 'value' property
    '''
    def __init__(self, format, value):
        self._format = format
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value

    def __repr__(self):
        return '%s(%r, %r)'%(type(self).__name__, self._format, self._value)

    value = property(get, set)

class SharedStruct(SharedValue):
    pass

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

ListProxy = MakeAutoProxyType(_list_exposed, 'BaseListProxy')

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


class SharedValueProxy(BaseProxy):
    def get(self):
        return self._callmethod('get')
    def set(self, value):
        return self._callmethod('set', (value,))
    value = property(get, set)


_arr_exposed = (
        '__len__', '__iter__', '__getitem__', '__setitem__',
        '__getslice__', '__setslice__'
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
    SharedValue = CreatorMethod(SharedValue, SharedValueProxy)
    SharedStruct = CreatorMethod(SharedStruct, SharedValueProxy)
    SharedArray = CreatorMethod(array.array, exposed=_arr_exposed)
