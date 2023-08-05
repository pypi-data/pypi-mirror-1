import processing.test

manager_type = globals().get('manager_type', 'normal')

if manager_type == 'normal':
    from processing import *
elif manager_type == 'dummy':
    from processing.dummy import *
else:
    raise ValueError


def test_list():
    '''
    >>> a = manager.list(range(10))
    >>> print a
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    >>> b = manager.list()
    >>> print b
    []

    >>> b.extend(range(5))
    >>> print b
    [0, 1, 2, 3, 4]

    >>> b[2]
    2

    >>> b[2:10]
    [2, 3, 4]

    >>> b *= 2
    >>> print b
    [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]

    >>> b + [5, 6]
    [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 5, 6]

    >>> a == manager.list(range(10))
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
    >>> e = manager.list(d)
    >>> print e
    [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]]

    >>> it = iter(a)
    >>> tuple(it)
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)

    >>> f = manager.list([a])
    >>> print f
    [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
    
    >>> a.append('hello')
    >>> print f
    [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'hello']]
    '''


def test_dict():
    '''
    >>> d = manager.dict()
    >>> for i in range(8):
    ...     d[i] = chr(65 + i)
    ...
    >>> print d.copy()
    {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H'}

    >>> for item in d.iteritems():
    ...     print item,
    ...
    (0, 'A') (1, 'B') (2, 'C') (3, 'D') (4, 'E') (5, 'F') (6, 'G') (7, 'H')
    '''


def test_namespace():
    '''
    >>> n = manager.Namespace()
    >>> n.name = 'Bob'
    >>> n.job = 'Builder'
    >>> print n                                         # doctest: +ELLIPSIS
    Namespace(...='...', ...='...')
    
    >>> hasattr(n, 'job')
    True
    
    >>> del n.job
    >>> print n
    Namespace(name='Bob')
    
    >>> hasattr(n, 'job')
    False
    '''


def test_bigdata():
    '''
    >>> n = manager.Namespace()
    >>> x = range(100000)
    >>> n.value = x
    >>> y = n.value
    >>> x == y
    True
    '''


def test_process_repr():
    '''
    >>> import time
    >>> p = Process(target=time.sleep, args=[0.1])
    >>> print p, p.getExitCode()                        # doctest: +ELLIPSIS
    <...Process(..., initial)> None
    
    >>> p.start()
    >>> print p, p.getExitCode()                        # doctest: +ELLIPSIS
    <...Process(..., started)> None
    
    >>> p.join()
    >>> print p, p.getExitCode()                        # doctest: +ELLIPSIS
    <...Process(..., stopped)> 0
    '''
    
def test_condition_repr(cond):
    '''
    >>> cond = manager.Condition()
    >>> print cond
    <Condition(<_RLock(None, 0)>, 0)>
    
    >>> cond.acquire()
    True
    
    >>> print cond                                      # doctest: +ELLIPSIS
    <Condition(<_RLock(Main..., 1)>, 0)>

    >>> p = Process(target=test_condition_repr, args=[cond])
    >>> p.start()
    >>> cond.wait()
    >>> print cond                                      # doctest: +ELLIPSIS
    <Condition(<_RLock(Main..., 1)>, 1)>

    >>> cond.notify()
    >>> cond.release()
    '''
    cond.acquire()
    cond.notify()
    cond.wait()
    cond.release()
    

class Subclass(Process):
    '''
    >>> l = manager.list([2, 8, 16])
    >>> p = Subclass(l)
    >>> p.start()
    >>> p.join()
    >>> print l
    [4, 64, 256]
    '''
    def __init__(self, data):
        Process.__init__(self)
        self.data = data

    def run(self):
        for i in range(len(self.data)):
            self.data[i] **= 2


def test_recursion(output, level=3):
    '''
    >>> output = manager.list()
    >>> test_recursion(output)
    >>> for line in output[:]:
    ...     print line                                  # doctest: +ELLIPSIS
    ...
    <_Main...(Main..., started)>
        <...Process(...-..., started)>
            <...Process(...-..., started)>
                <...Process(...-..., started)>
                <...Process(...-..., started)>
            <...Process(...-..., started)>
                <...Process(...-..., started)>
                <...Process(...-..., started)>
        <...Process(...-..., started)>
            <...Process(...-..., started)>
                <...Process(...-..., started)>
                <...Process(...-..., started)>
            <...Process(...-..., started)>
                <...Process(...-..., started)>
                <...Process(...-..., started)>
    '''
    output.append('    ' * (3-level) + str(currentProcess()))
    if level > 0:
        for i in range(2):
            p = Process(target=test_recursion, args=[output, level-1])
            p.start()
            p.join()


def test(verbose=False):
    global manager

    import doctest, sys
    reload(doctest)       # prevent warnings from `DocTestRunner.merge()`

    manager = Manager()

    res = doctest.testmod(sys.modules[__name__],
                          verbose=verbose, exclude_empty=True)

    if not verbose:
        doctest.master.summarize(verbose=True)


if __name__ == '__main__':
    test(verbose=True)
