#
# This module shows how to use a user defined type with a subclass of
# BaseProcessManager.  (Instead of registering a type with it you can
# also register a Factory function.)
#
# By default the proxy object will have methods corresponding to each
# attribute of the shared object which is a method or function and
# does not start with '_'.  There are two ways to override this
# default behaviour:
#
# (1) If the shared object has a '__expose_to_proxy__' attribute then
#     that is used to determine the methods/functions to expose via the
#     proxy.
#
# (2) If the 'register' classmethod is called using the 'exposed'
#     argument then this is used to determine the methods/functions to
#     expose via the proxy.
#


from processing import manager
#from processing.dummy import manager

class FooFoo(object):
    # __expose_to_proxy__ = ['bar']  # expose bar method via proxy
    def bar(self):
        print 'you called FooFoo.bar'

class NewManager(manager.ProcessBaseManager):
    pass

NewManager.register(
    'Foo',                      # add a 'Foo' method to NewManager
    FooFoo                      # callable to use when NewManager.Foo is called
    # exposed=['bar']           # expose bar method via proxy
    )

if __name__ == '__main__':
    manager = NewManager()

    f = manager.Foo()
    f.bar()
