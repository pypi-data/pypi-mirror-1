#
# This module shows how to use arbitrary callables with a subclass of
# `BaseManager`.
#

import processing.test

manager_type = globals().get('manager_type', 'normal')

if manager_type == 'normal':
    from processing import *
    from processing.managers import *
elif manager_type == 'dummy':
    from processing.dummy import *
    from processing.dummy.managers import *
else:
    raise ValueError

##

class Foo(object):
    def f(self):
        print 'you called Foo.f()'
    def g(self):
        print 'you called Foo.g()'
    def _h(self):
        print 'you called Foo._h()'

# A simple generator function
def baz():
    for i in xrange(10):
        yield i*i

# Proxy type for generator objects
class GeneratorProxy(BaseProxy):
    def __iter__(self):
        return self
    def next(self):
        return self._callmethod('next')
        
##

class MyManager(BaseManager):
    # register the Foo class; make all public methods accessible via proxy
    Foo1 = CreatorMethod(Foo)

    # register the Foo class; make only `g()` and `_h()` accessible via proxy
    Foo2 = CreatorMethod(Foo, exposed=('g', '_h'))

    # register the generator function baz; use `GeneratorProxy` to make proxies
    baz = CreatorMethod(baz, proxytype=GeneratorProxy)

##

class A(object):
    @staticmethod
    def f():
        return 'A.f()'

##

def test():
    manager = MyManager()
    manager.start()
    
    print '-' * 20

    f1 = manager.Foo1()
    f1.f()
    f1.g()

    print '-' * 20

    f2 = manager.Foo2()
    f2.g()
    f2._h()

    print '-' * 20

    it = manager.baz()

    for i in it:
        print '<%d>' % i,

    print

##

if __name__ == '__main__':
    test()

