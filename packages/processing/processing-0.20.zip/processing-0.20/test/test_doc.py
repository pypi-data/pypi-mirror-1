teststring = '''
>>> from processing import *
>>> m = Manager()

>>> a = m.list(range(10))
>>> print a, repr(a)                    # doctest: +ELLIPSIS
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] <Proxy[list] object at 0x...>

>>> b = m.list()
>>> print b
[]

>>> b.extend(range(5))
>>> print b
[0, 1, 2, 3, 4]

>>> b *= 2
>>> print b, repr(b)                     # doctest: +ELLIPSIS
[0, 1, 2, 3, 4, 0, 1, 2, 3, 4] <Proxy[list] object at 0x...>

>>> b + [5, 6]
[0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 5, 6]

>>> a == m.list(range(10))
True
>>> a == range(10)
True
>>> a == range(11)
False

>>> a > range(9)
True
>>> range(11) > a
True

>>> d = [a, b]
>>> d                                   # doctest: +ELLIPSIS
[<Proxy[list] object at 0x...>, <Proxy[list] object at 0x...>]

>>> e = m.list(d)
>>> print e
[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]]

>>> it = iter(a)
>>> it                                  # doctest: +ELLIPSIS
<Proxy[iterator] object at 0x...>

>>> tuple(it)
(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)

>>> f = m.list([a])
>>> print f
[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
>>> a.append('hello')
>>> print f
[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'hello']]

>>> m.shutdown()
'''

def main():
    import doctest, warnings
    warnings.filterwarnings("ignore", ".*class Tester is deprecated.*")
    
    print 'Running doctest'
    result = doctest.Tester(globs={}).runstring(teststring, 'teststring')
    print 'Finished doctest, failures = %d/%d' % result

if __name__ == '__main__':
    main()
