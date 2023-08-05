import time, sys, processing


def foo(n):
    
    for i in range(50):
        try:
            time.sleep(0.1)
            sys.stderr.write('-')
            sys.stderr.flush()
        except processing.ProcessExit:
            print
            if n == 0:
                print >>sys.stderr, 'exiting normally'
                break
            elif n == 1:
                print >>sys.stderr, 'exiting with exit code 1'
                sys.exit(1)
            elif n == 2:
                print >>sys.stderr, 'reraising ProcessExit'
                raise
            else:
                print >>sys.stderr, 'trying to ignore ProcessExit'
                continue
            

def run():
    '''
    The output shown below only includes output from the parent process:
    
    >>> run()                          #doctest: +ELLIPSIS
    <BLANKLINE>
    TEST 1
    <Process(Process-..., stopped)>
    <BLANKLINE>
    TEST 2
    <Process(Process-..., stopped[1])>
    <BLANKLINE>
    TEST 3
    <Process(Process-..., stopped[ProcessExit])>
    <BLANKLINE>
    TEST 4
    <Process(Process-..., stopped)>
    '''
    for i in range(4):
        print '\nTEST %d' % (i+1)
        p = processing.Process(target=foo, args=[i])
        p.start()
        time.sleep(3)
        p.stop()
        p.join()
        print p


def test(use_doctest=False):
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__], verbose=False)
    print
    if res[0] != 0:
        print '%s failures out of %s tests.' % res
    else:
        print 'All tests passed.'
    
        
if __name__ == '__main__':
    run()
