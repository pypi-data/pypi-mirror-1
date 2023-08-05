THE PROCESSING PACKAGE

The 'processing' package is intended to be a portable analogue of
'threading', but using processes instead of threads.  A module
'processing.dummy_processing' has the same api but is a thin wrapper
around 'threading'.

On Unix os.fork() is used to launch the child processes, but on
Windows it is necessary to launch a new interpreter for each process
(which involves some kludgery and another module
'processing.nonforking').  The class 'processing.Process' is modelled
on 'threading.Thread', and can be used in much the same way.

Processes communicate with each other via sockets or named pipes.
Mutexes, Recursive Mutexes, Semaphores, Bounded Semaphore, Conditions
and Queues are all implemented, as well as some other 'shared objects'
like dictionaries and namespaces.  (User defined types can also be
shared -- see below).  These are held by a 'Manager' which runs in its
own process.  Processes make use of proxies for objects which exist in
the Manager's process.  (It is also possible to create a proxy to an
object on a separate machine if the firewalls allow that.)

(The manager serves about 20,000 requests a second on a Pentium 4 
2.5 Ghz laptop.)


INSTALLATION

If you have the correct C compiler setup then the source distribution
can be installed the usual way:

   unzip processing-X.Y.zip
   cd processing-X.Y
   python setup.py install

Without the C compiler you can install just the python modules by
replacing the last line with

   python setup.py build_py install --skip-build

Apart from being slower everything should work the same.


EXAMPLE

Consider this simple multithreaded example program:

   from threading import Thread
   from Queue import Queue

   def f(q):
       for i in range(10):
           q.put(i*i)
       q.put('STOP')

   if __name__ == '__main__':
       queue = Queue(10)

       t = Thread(target=f, args=[queue])
       t.start()

       result = None
       while result != 'STOP':
           result = queue.get()
           print result

       t.join()

By modifying it to use 'processing' we get the following:

!  from processing import Process, Manager

   def f(q):
       for i in range(10):
           q.put(i*i)
       q.put('STOP')

   if __name__ == '__main__':
!      manager = Manager()
!      queue = manager.Queue(10)

!      t = Process(target=f, args=[queue])
       t.start()

       result = None
       while result != 'STOP':
           result = queue.get()
           print result

       t.join()

To go back to using threads you can just change the import line to
use 'processing.dummy' instead of 'processing':

    from processing.dummy import Process, Manager

'test/test_processing.py' has lots more examples.  There is another
file 'test/test_with.py' which does the same tests but makes use of
the new 'with' statement introduced in Python 2.5.
'test/test_newproxytype.py' shows how to register a new type for use
with a manager.


USE OF A MANAGER

To create a manager you use

    manager = Manager()

('manager' will be an instance of 'processing.manager.DefaultManager'
which is a subclass of 'Process'.)  To create a shared object you call
the appropriately named method of 'manager'.  For instance to create a
shared list you do

    l = manager.list()

The returned object 'l' is a proxy which can be used in much the same
way as a normal list.

Arguments to the constructor can also be passed, so

    l = manager.list(range(10))

will execute 'list(range(10))' in the manager to produce the shared
list.

The types (or factory functions) supported by default are

    dict, list, set, Namespace, BoundedSemaphore, Condition, Event,
    Lock, Queue, RLock, Semaphore

Namespace is discussed below, and the others all correspond to builtin
types or types from the standard library.


NAMESPACE

The only supported shared object type which is not a builtin or from
the standard library is 'Namespace'.  Instances of this type have
writable attributes.  Note however that when accessed via a proxy,
attributes starting with '_' are not guaranteed to be shared with
other processes.  An example:

    >>> manager = Manager()
    >>> n = manager.Namespace()
    >>> n.x = 10                # attribute is shared with other processes
    >>> n.y = 'hello'           # attribute is shared with other processes
    >>> n._z = 12.3             # attribute is NOT shared with other processes
    >>> print Repr(n)
    <Namespace(x=10, y='hello')>


USING NEW TYPES WITH A MANAGER

User defined classes (or factory functions) can be registered with
subclasses of 'processing.manager.ProcessBaseManager'.  For example

    from processing.manager import ProcessBaseManager

    class Foo(object):
        def bar(self):
            print 'BAR'

    class NewManager(ProcessBaseManager):
        pass

    NewManager.register('Foo', Foo, exposed=['bar'])

    if __name__ == '__main__':
        manager = NewManager()
        foo = manager.Foo()
        foo.bar()

If you want to keep the default types of shared objects then subclass
'processing.manager.DefaultManager' instead.


SHARING OF PROXY OBJECTS

Proxy objects cannot be shared between processes.  However care has
been taken to ensure that if you pass a proxy as an argument to the
target function of a process (or save a proxy on an instance of a
subclass of Process) then the newly created process will get a safe
copy of the proxy.  So, for example, it is safe to do

    manager = Manager()
    cond = manager.Condition()
    cond.acquire()
    p = Process(target=foo, args=[cond])
    p.start()
    ...


REPR

The representation of a proxy instance is uninformative:

    >>> manager = Manager()
    >>> l = manager.list(range(10))
    >>> l
    <Proxy[list] object at 0x00c143b0)>

To see the representation of the underlying object you use the 'Repr'
function:

    >>> Repr(l)
    '[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]'


SPEED

As one would expect, communication between processes is slower than
communication between threads.  Using the C extensions windows (using
named pipes) and linux (using unix domain sockets) are roughly equal
in speed.

For example (on a Pentium 4 2.5 Ghz laptop) a value can be retreived
from a shared dictionary 18,000-20,000 times/sec compared to around 5
million times/sec for a normal dictionary.

With one process sending objects to another process using a shared
Queue I get around 7,500 times/sec.  Doing the same using a
normal Queue and threads I get 18,000-50,000 times/sec.  (For some
reason on linux it is usually around 18,000 but sometimes around
45,000, whereas on windows it is consistently 45,000-50,000.)

For communication between two processes one can use 'Listener' and
'Client' for a much faster and simpler alternative to a Queue.  See
below.

(Using SimpleXMLRPCServer/xmlrpclib with logging turned off I get
about 180 transactions/sec on windows and 400 transactions/sec on
linux.)


CLEANUP

Proxies have a __del__ method which is called when they are deleted.
The underlying shared object will be deleted when all proxies
referring to it have been deleted.

Manager objects also have a __del__ method which shuts down the
subprocess which holds the shared objects.  You can also call the
'shutdown' method explicitly.


LISTENER AND CLIENT

To setup a connection between two processes one can use the functions
'Listener' and 'Client'.  An example of usage is

    >>> from processing import *
    >>> l = Listener(family='AF_INET')
    >>> l.address
    ('127.0.0.1', 45291)
    >>> client = Client(l.address)
    >>> server = l.accept()
    >>> client.send(['this', range(10), None])
    >>> server.recv()
    ['this', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], None]
    >>> client.send_string('some string')
    >>> server.recv_string()
    'some string'

The connection type is determined by the 'family' argument to
'Listener'.  Possible values are 'AF_INET' (for a TCP Socket), 'AF_UNIX'
(for a Unix Domain Socket) or 'AF_PIPE' (for a Windows Named Pipe).
On Windows Named Pipes are much faster than normal TCP sockets.


GENERAL USAGE GUIDLINES

(1) Ensure that the arguments to the methods of proxies are
picklable.


EXTRA USAGE GUIDELINES FOR WINDOWS

The following restrictions only apply to windows (or other platforms
which do not have os.fork).

(1) When using the constructor

    Process(target=function, args=(...), kwds={...})

make sure that 'args' and 'kwds' are picklable.  (Note that proxies
ARE picklable.)  

Similarly, make sure that an instance of a subclass
of Process is picklable at the time you call the 'start' method.

(2) Before a manager is shutdown/garbage collected all proxies
referring to it must be closed/garbage collected.  This means you
should join all child processes which use a manager before the manager
shutsdown or is garbage collected.  (Note that a proxy returned by a
manager's method will be garbage collected before the manager is: for
instance 'queue' in the example above need not be deleted explicitly.)

(3) Make sure that the module containing the target of a Process can
be safely imported by a new Python interpreter without causing side
effects (such a starting a new process).

For example, under Windows running the following module would
recursively create new processes until you get a crash:

    import processing

    def f():
        print 'hello'

    p = processing.Process(target=f)
    p.start()
    p.join()

Instead hide creation of the new process by using
"if __name__ == '__main__':" as follows:

    import processing

    def f():
        print 'hello'

    if __name__ == '__main__':
        p = processing.Process(target=f)
        p.start()
        p.join()

(4) Do not let the code which runs in a child process try to access
any globals except for those that are effectively module level
constants.  (If you really need to use globals then create a new
'Namespace' using a manager.)  In particular, a child process should
not try to use a proxy it finds in the global namespace.


DIFFERENCES FROM threading.py

(1) The constructor for threading.Condition optionally takes a
Lock/RLock object as an argument.  This will not work with when
creating a Condition using a manager.

(2) There is no equivalent of threading.local.

(3) activeCount, enumerate, settrace, setprofile, Timer,
Thread.isAlive, Thread.setDaemon from threading are not supported.

(4) Process.join does not support the optional timeout parameter
that threading.join does.  Also Process.setName only works before
the process has been started.

(5) The default names of threads use an integer identifer, e.g.
'Thread-23'.  Processes are identified using tuples.  For instance
the 3rd child process of the 4th child process of the 7th child
process of the main process will be named 'Process-7:4:3'


LICENCE

Copyright (c) 2006, Richard Oudkerk
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. Neither the name of author nor the names of any contributors may be
   used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.


EMAIL: r.m.oudkerk at gmail.com