#
# Module providing the DefaultManager for dealing with shared objects
#
# processing/manager.py
#
# Copyright (c) 2006, Richard Oudkerk
#

__all__ = [ 'BaseManager', 'ProcessBaseManager', 'DefaultManager' ]

import threading, os, types, sys, weakref

from Queue import Full, Empty
from processing.connection import Listener, Client
from processing.process import Process, currentProcess

class Token(object):
    '''
    Type to uniquely indentify a shared object
    '''
    def __init__(self, type, address, id):
        self.type = type
        if self.type.__class__ is not str:
            self.type = self.type.__name__
        self.address = address
        self.id = id

    def __repr__(self):
        return 'Token(type=%r, address=%r, id=%r)' % \
               (self.type, self.address, self.id)


class InnerManager(object):
    '''
    The private part of a manager, instances of which are (usually) created
    in a subprocess
    '''
    exposed = ['shutdown', 'delete', 'new', 'accept_connection', 'get_methods']

    def __init__(self, registry, address=None, family=None):
        self.listener = Listener(address=address, family=family, backlog=5)
        self.registry = registry
        self.address = self.listener.address
        self.id_to_obj = {}
        self.id_to_refcount = {}
        self.connection_to_refcount = {}
        self.socket_to_name = {}
        self.socket_to_refcount = {}
        self.mutex = Lock()
        self.stop = False        

    def print_exc(self, c, extra=None):
        import traceback
        name = self.socket_to_name.get(c, None)
        print >>sys.stderr, '\n' + '-'*75
        print >>sys.stderr, 'LAST CLIENT PROCESS:', name
        if extra is not None:
            print >>sys.stderr, 'EXTRA:', extra
        traceback.print_exc()
        print >>sys.stderr, '-'*75 + '\n'

    def shutdown(self, c):
        self.stop = True

    def delete(self, c, token):
        assert token.address == self.address, \
               'token does not match address of server'
        del self.id_to_obj[token.id]
        del self.id_to_refcount[token.id]
        
    def new(self, c, Type, *args, **kwds):
        Type = self.registry[Type][0]
        obj = Type(*args, **kwds)
        i = id(obj)
        self.id_to_obj[i] = obj
        self.id_to_refcount[i] = 0
        return i

    def get_methods(self, c, token):
        obj = self.id_to_obj[token.id]
        if hasattr(obj, '__expose_to_proxy__'):
            return set(obj.__expose_to_proxy__)
        elif self.registry[token.type][2] is not None:
            return self.registry[token.type][2]
        else:
            return _guess_exposed(obj)

    def accept_connection(self, c):
        name = 'unnamed'
        self.socket_to_name[c] = name
        c.send(('#RETURN', None))
        t = threading.Thread(target=self.serve_connection, args=[c], name=name)
        t.start()

    def handle_requests(self):
        try:
            while not self.stop:
                c = None
                request = None

                try:
                    c = self.listener.accept()
                    request = c.recv()
                    ignore, funcname, args, kwds = request
                    assert funcname in self.exposed, \
                           '%r unrecongized' % funcname
                    func = _getattr(self, funcname)
                    result = ('#RETURN', func(c, *args, **kwds))

                except (SystemExit, KeyboardInterrupt):
                    raise

                except Exception, e:
                    ret = ('#ERROR', e)
                    self.print_exc(c, request)

                else:
                    if funcname != 'accept_connection':
                        try:
                            c.send(result)
                        except Exception, e:
                            self.print_exc(c, request)

                        c.close()
        finally:
            self.listener.close()
        
    def serve_connection(self, connection):
        funcname = request = obj = None
        recv = connection.recv
        send = connection.send
        id_to_obj = self.id_to_obj
        self.socket_to_refcount[connection] = 0

        while not self.stop:
            try:
                request = recv()
                id, funcname, args, kwds = request
                obj = id_to_obj[id]
                function = getattr(obj, funcname)
                result = function(*args, **kwds)
                send(('#RETURN', result))        
                
            except (Empty, Full), e:
                send(('#ERROR', e))
                
            except AttributeError, e:
                
                if funcname == '#DEREGISTER':
                    send(('#RETURN', None))
                    self.mutex.acquire()
                    try:
                        self.socket_to_refcount[connection] -= 1
                        self.id_to_refcount[id] -= 1

                        if self.id_to_refcount[id] == 0:
                            del obj, id_to_obj[id],
                            del self.id_to_refcount[id]

                        if self.socket_to_refcount[connection] == 0:
                            del self.socket_to_refcount[connection]
                            connection.close()
                            return
                    finally:
                        self.mutex.release()

                elif funcname == '#REGISTER':
                    send(('#RETURN', None))
                    self.mutex.acquire()
                    try:
                        self.id_to_refcount[id] += 1
                        self.socket_to_refcount[connection] += 1
                    finally:
                        self.mutex.release()
                    
                elif funcname == '#SETNAME':
                    send(('#RETURN', None))
                    self.socket_to_name[connection] = args[0]
                    threading.currentThread().setName(args[0])

                elif funcname == '__repr__':
                    send(('#RETURN', repr(obj)))                    

                else:
                    self.print_exc(connection, request)
                    send(('#ERROR', e))

            except (SystemExit, KeyboardInterrupt):
                raise

            except Exception, e:
                self.print_exc(connection, request)
                try:
                    send(('#ERROR', e))
                except:
                    return
                

_proxy_type_cache = {}
_proxy_type_cache_lock = threading.Lock()

def GenericProxy(token):
    '''
    Returns a proxy for the object associated with token

    This creates a new proxy type if necessary
    '''
    _proxy_type_cache_lock.acquire()
    try:
        try:
            return _proxy_type_cache[(token.type, token.address)](token)
        except KeyError:
            pass

        dummy_proxy = BaseProxy(token) 
        conn = Client(token.address)
        _methods = dispatch(conn, None, 'get_methods', token)

        class Proxy(BaseProxy):
            def __init__(self, token):
                BaseProxy.__init__(self, token)
            def __reduce__(self):
                return (GenericProxy, (self._token,))
            def _get_methods(self):
                return list(_methods)
            for name in _methods:
                exec '''def %s(self,*args,**kwds):
                return self._apply(self._id,%r,*args,**kwds)''' % (name,name)
            del name

        _proxy_type_cache[(token.type, token.address)] = Proxy
        return Proxy(token)
    finally:
        _proxy_type_cache_lock.release()


class BaseManager(object):
    '''
    The public part of a manager
    '''
    _registry = {}

    def __init__(self, address=None, family=None):
        self._address = address
        self._family = family

    def serve_forever(self):
        self._manager = InnerManager(
            registry=self._registry,
            address=self._address,
            family=self._family
            )
        self._address = self._manager.address
        self._manager.handle_requests()

    address = property(lambda self: self._address)

    def _newtoken(self, Type, *args, **kwds):
        assert type(Type) is str
        c = Client(self.address)
        id = dispatch(c, None, 'new', Type, *args, **kwds)
        return Token(Type, self.address, id)

    def shutdown(self):
        '''
        Shutdown the managers subprocess

        This is automatically called when the object is deleted
        '''
        if hasattr(self, 'address'):
            c = Client(self.address)
            dispatch(c, None, 'shutdown')
            del self._address

    def register(cls, name, type, proxytype=GenericProxy, exposed=None):
        '''
        Register a type/callable with the class
        '''
        assert name not in cls._registry
        if '_registry' not in cls.__dict__:
            cls._registry = cls._registry.copy()
        cls._registry[name] = (type, proxytype, exposed)

        def temp(self, *args, **kwds):
            token = self._newtoken(name, *args, **kwds)
            p = proxytype(token)
            p._manager = self        # make sure original proxy is 
            return p                 # ... garbage collected before manager

        temp.__name__ = name
        setattr(cls, name, temp)
        
    register = classmethod(register)


class ProcessBaseManager(BaseManager, Process):
    '''
    Subclass of BaseManager which runs InnerManager.serve_forever
    in a subprocess
    '''
    def __init__(self, address=None, family=None, autostart=True):
        BaseManager.__init__(self, address, family)
        Process.__init__(self)
        if autostart:
            self.start()

    def start(self):
        temp = Listener()
        self._temp_address = temp.address
        Process.start(self)
        c = temp.accept()
        self._address = c.recv()

    def run(self):
        temp = Client(self._temp_address)
        self._manager = InnerManager(
            registry=self._registry,
            address=self._address,
            family=self._family
            )
        self._address = self._manager.address
        temp.send(self._address)
        del temp
        self._manager.handle_requests()

    def __del__(self):
        self.shutdown()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

class RemoteManager(BaseManager):
    def __init__(self, address):
        self._address = address
    def serve_forever(self):
        raise NotImplementedError

#
# Proxy related stuff
#

def dispatch(c, id, funcname, *args, **kwds):
    '''
    Send a message to manager and return its response
    '''
    c.send((id, funcname, args, kwds))
    kind, result_from_server = c.recv()
    if kind == '#RETURN':
        return result_from_server
    elif kind == '#ERROR':
        raise result_from_server
    else:
        raise ValueError


class BaseProxy(object):
    '''
    A base for proxies of shared objects

    Note that 'Repr' and the method '_repr' returns the representation
    of the underlying object.
    '''
    _key_to_connection = {}
    _socket_to_refcount = {}
    _mutex = threading.RLock()
    _weakrefs = set()
    _saved_connectors = set()
    
    def __init__(self, token):
        self._token = token
        BaseProxy._weakrefs.add(weakref.ref(self))
        self._reconnect()

    def _reconnect(self):
        self._key = (os.getpid(), threading._get_ident(), self._token.address)
        self._id = self._token.id
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
    
    def _copy(self):
        return type(self)(self._token)
    
    def __reduce__(self):
        return (type(self), (self._token,))

    def _apply(self, id, funcname, *args, **kwds):
        # this method overwrites itself
        if not hasattr(self, '_connector'):
            self._reconnect()
        self._apply = dispatch.__get__(self._connector, BaseProxy)
        name = currentProcess().getName()
        if threading.currentThread().getName() != 'MainThread':
            name += ':' + threading.currentThread().getName()
        self._apply(id, '#SETNAME', name)
        return self._apply(id, funcname, *args, **kwds)

    def _repr(self):
        return self._apply(self._id, '__repr__')

    def _close(self):
        BaseProxy._mutex.acquire()
        try:
            if not hasattr(self, '_connector'):
                return

            connector = self._connector
            del self._connector

            assert connector is BaseProxy._key_to_connection[self._key]
            assert BaseProxy._socket_to_refcount[connector] >= 0

            BaseProxy._socket_to_refcount[connector] -= 1
            dispatch(connector, self._id, '#DEREGISTER')

            if BaseProxy._socket_to_refcount[connector] == 0:
                connector.close()
                del BaseProxy._key_to_connection[self._key]
                del BaseProxy._socket_to_refcount[connector]
        finally:
            BaseProxy._mutex.release()

    def __del__(self):
        self._close()

    def __repr__(self):
        a = '%s0x%08x' % (id(self)<0 and '-' or '', abs(id(self)))
        return '<Proxy[%s] object at %s>' % (self._token.type, a)

    def _reset_all():
        for wr in BaseProxy._weakrefs:
            proxy = wr()
            if proxy is not None:
                if hasattr(proxy, '_connector'):
                    BaseProxy._saved_connectors.add(proxy._connector)
                    del proxy._connector, proxy._key
                try:
                    del proxy._apply
                except AttributeError:
                    pass
    _reset_all = staticmethod(_reset_all)

    def _close_all():
        for wr in BaseProxy._weakrefs:
            try:
                proxy = wr()
                if proxy is not None:
                    proxy._close()
            except Exception:
                traceback.print_exc()  
    _close_all = staticmethod(_close_all)

import processing.process
processing.process._reset_all_proxies = BaseProxy._reset_all
processing.process._close_all_proxies = BaseProxy._close_all
del processing.process


class AcquirerProxy(BaseProxy):
    '''
    A base class for proxies which have acquire and release methods
    '''    
    def acquire(self, blocking=1):
        return self._apply(self._id, 'acquire', blocking)
    def release(self):
        return self._apply(self._id, 'release')
    def __enter__(self):
        self._apply(self._id, 'acquire')
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._apply(self._id, 'release')


_MethodTypes = [types.FunctionType, types.UnboundMethodType,
                types.BuiltinFunctionType, types.BuiltinMethodType,
                type(list.append)]

def _guess_exposed(obj):
    methods = [name for name in dir(obj)
               if type(getattr(obj, name)) in _MethodTypes]
    return set([name for name in methods if not name.startswith('_')])

#
# Types (or factory functions) which we will register with DefaultManager
#

from threading import BoundedSemaphore, Condition, Event, \
     Lock, RLock, Semaphore
from Queue import Queue

class Namespace(object):
    '''
    Instances of this class can be used as namespaces

    Instances of this class have writable attributes, and can be used
    as namespaces via a proxy.  Note however that if you try to
    set/get/delete an attribute beginning with '_' then this is not
    guaranteed to effect the underlying shared object.

    You can use 'Repr' function to see a representation of the
    attributes set on the underlying object.  For example

    >>> manager = Manager()
    >>> n = manager.Namespace()
    >>> n.x = 10                # attribute is shared with other processes
    >>> n.y = 'hello'           # attribute is shared with other processes
    >>> n._z = 12.3             # attribute is NOT shared with other processes
    >>> print Repr(n)
    <Namespace(x=10, y='hello')>
    '''
    def __repr__(self):
        temp = self.__dict__.items()
        temp = ['%s=%r' % i for i in temp if not i[0].startswith('_')]
        temp.sort()
        return '<Namespace(%s)>' % str.join(', ', temp)

#
# Registration of types with DefaultManager
#

class DefaultManager(ProcessBaseManager):
    pass

DefaultManager.register('Event', Event)
DefaultManager.register('Queue', Queue)
DefaultManager.register('Lock', Lock, AcquirerProxy)
DefaultManager.register('RLock', RLock, AcquirerProxy)
DefaultManager.register('Semaphore', Semaphore, AcquirerProxy)
DefaultManager.register('BoundedSemaphore', BoundedSemaphore, AcquirerProxy)

class ConditionProxy(AcquirerProxy):
     def wait(self, timeout=None):
         return self._apply(self._id, 'wait', timeout)    
     def notify(self):
         return self._apply(self._id, 'notify')
     def notifyAll(self):
         return self._apply(self._id, 'notifyAll')
DefaultManager.register('Condition', Condition, ConditionProxy)

DefaultManager.register(
    'dict', dict, exposed = (
        _guess_exposed(dict) | 
        set(['__getitem__', '__setitem__', '__delitem__', '__len__']) -
        set(['iteritems', 'iterkeys', 'itervalues'])
        ))

DefaultManager.register(
    'list', list, exposed = (
        _guess_exposed(list) |
        set(['__getitem__', '__setitem__', '__delitem__', '__len__',
             '__getslice__', '__setslice__', '__delslice__'])
        ))

DefaultManager.register(
    'set', set, exposed=(_guess_exposed(set) | set(['__len__','__contains__']))
    )

_getattr = object.__getattribute__
_setattr = object.__setattr__
_delattr = object.__delattr__

class NamespaceProxy(BaseProxy):
    def __getattr__(self, key):
        if key.startswith('_'):
            return _getattr(self, key)
        return _getattr(self, '_apply')(self._id, '__getattribute__', key)
    def __setattr__(self, key, value):
        if key.startswith('_'):
            return _setattr(self, key, value)
        return _getattr(self, '_apply')(self._id, '__setattr__', key, value)
    def __delattr__(self, key):
        if key.startswith('_'):
            return _delattr(self, key)
        return _getattr(self, '_apply')(self._id, '__delattr__', key)
DefaultManager.register('Namespace', Namespace, NamespaceProxy)
