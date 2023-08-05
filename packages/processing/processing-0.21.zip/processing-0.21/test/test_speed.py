#
# Simple benchmarks for the processing package (and processing.dummy)
#

import time

if 'use_dummy' not in globals() or not use_dummy:
    from processing import *
    from processing.connection import *
else:
    from processing.dummy import *
    from processing.dummy.connection import *


#### TEST_QUEUESPEED

def queuespeed_func(q, c, iterations):
    c.acquire()
    c.notify()
    c.release()
    
    for i in xrange(iterations):
        q.put(i)

    q.put('STOP')

def test_queuespeed():
    q = manager.Queue()
    c = manager.Condition()
    
    elapsed = 0
    iterations = 1

    while elapsed < 1:
        iterations *= 2
        
        p = Process(target=queuespeed_func, args=[q, c, iterations])

        c.acquire()
        p.start()
        c.wait()
        c.release()
        
        result = None
        t = time.time()

        while result != 'STOP':
            result = q.get()

        elapsed = time.time() - t

        p.join()

    print iterations, 'integers passed through the queue in', \
          elapsed, 'seconds'
    print 'average number/sec:', iterations/elapsed


#### TEST_DICTSPEED

def test_dictspeed():
    d = manager.dict()
    
    d['x'] = 1
    elapsed = 0
    iterations = 1

    while elapsed < 1:
        iterations *= 2

        t = time.time()
        
        for i in xrange(iterations):
            a = d['x']

        elapsed = time.time()-t

    print iterations, 'iterations in', elapsed, 'seconds'
    print 'average number/sec:', iterations/elapsed


#### TEST_CLIENT

def client_func(address, iterations):
    c = Client(address)
    res = c.recv()
    assert res == 'START'

    for i in xrange(iterations):
        c.send(i)
        
    c.send('STOP')

def test_client():
    l = Listener()
    elapsed = 0
    iterations = 1

    while elapsed < 1:
        iterations *= 2

        p = Process(target=client_func, args=[l.address, iterations])
        p.start()
        
        c = l.accept()
        c.send('START')
        t = time.time()

        result = None
        while result != 'STOP':
            result = c.recv()

        elapsed = time.time() - t
        p.join()
        
    print iterations, 'objects passed through connection in', \
          elapsed, 'seconds'
    print 'average number/sec:', iterations/elapsed


####
    
def main():
    global manager

    manager = Manager()

    try:

        for func in [
            
            test_queuespeed, test_dictspeed, test_client
            
            ]:
            
            print
            print
            print '        ########', func.__name__
            print
            
            func()
            
    finally:
        
        manager.shutdown()


if __name__ == '__main__':
    main()
