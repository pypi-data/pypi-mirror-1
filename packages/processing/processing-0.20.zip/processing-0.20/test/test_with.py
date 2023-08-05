#
# A test file for the processing package (and processing.dummy)
#

from __future__ import with_statement

import time, sys, random
from Queue import Empty

if 'use_dummy' not in globals() or not use_dummy:
    from processing import *
    from processing.connection import *
else:
    from processing.dummy import *
    from processing.dummy.connection import *


#### TEST_NAMESPACE

def namespace_func(Global, mutex):    
    random.seed()
    time.sleep(random.random()*4)

    with mutex:
        print '\n\t\t\t' + str(currentProcess()) + ' has finished'
        Global.running -= 1


def test_namespace():
    Global = manager.Namespace()
    mutex = manager.Lock()
    
    Global.running = TASKS = 10

    for i in xrange(TASKS):
        Process(target=namespace_func, args=[Global, mutex]).start()

    while Global.running:
        time.sleep(0.08)
        with mutex:
            print Global.running,
            sys.stdout.flush()

    print
    print 'No more running processes'

    del Global.running
    Global.cat = 'lion'
    Global.country = 'laos'

    print
    print 'repr(Global) =', repr(Global)
    print 'str(Global) =', str(Global)


#### TEST_DICT

def test_dict():
    d = manager.dict()
    
    for i in xrange(10):
        d[i] = chr(65 + i)

    print d.copy()

    for item in d.items():
        print item


#### TEST_LIST

def test_list():
    l = manager.list(range(10))
    
    l.extend(range(100, 105))
    l.reverse()
    print l[:]
    print tuple(l)


#### TEST_SUBCLASS

class Subclass(Process):

    def __init__(self, mutex):
        Process.__init__(self)
        self.mutex = mutex

    def run(self):
        with self.mutex:
            print '\t' + str(self.mutex)
            time.sleep(1)

def test_subclass():
    mutex = manager.RLock()
    
    print mutex
    p = Subclass(mutex)

    with mutex:
        print mutex
        p.start()
        time.sleep(2)

    p.join()
    print 'main has joined'
    print mutex


#### TEST_QUEUE

def queue_func(queue):
    for i in xrange(30):
        time.sleep(0.5 * random.random())
        queue.put(i*i)
    queue.put('STOP')

def test_queue():
    q = manager.Queue()
    
    Process(target=queue_func, args=[q]).start()
    
    o = None
    while o != 'STOP':
        try:
            o = q.get(timeout=0.3)
            print o,
            sys.stdout.flush()
        except Empty:
            print 'TIMEOUT'


#### TEST_CONDITION

def condition_func(cond):    
    with cond:
        print '\t' + str(cond)
        time.sleep(2)
        print '\tchild is notifying'
        cond.notify()
        print '\t' + str(cond)

def test_condition():    
    cond = manager.Condition()
    
    p = Process(target=condition_func, args=[cond])
    print cond

    with cond:
        print cond

        with cond:
            print cond
            p.start()
            print 'main is waiting'
            cond.wait()
            print 'main has woken up'
            print cond

        print cond


    p.join()
    print cond


#### TEST_SEMAPHORE

def semaphore_func(sema, mutex, Global):        
    with sema:
        with mutex:
            Global.running += 1
            print Global.running, 'tasks are running'

        random.seed()
        time.sleep(random.random()*2)

        with mutex:
            Global.running -= 1
            print '%s has finished' % currentProcess()

def test_semaphore():
    sema = manager.Semaphore(3)
    mutex = manager.RLock()
    Global = manager.Namespace()

    Global.running = 0
    
    processes = [Process(target=semaphore_func, args=[sema, mutex, Global])
                 for i in range(10)]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
      
#### TEST_WAIT

def wait_func(Global, cond):        
    time.sleep(5.5)

    with cond:
        Global.finished = True
        print '\nchild notifying that finished'
        cond.notify()

def test_wait():
    Global = manager.Namespace()
    cond = manager.Condition()

    Global.finished = False

    p = Process(target=wait_func, args=[Global, cond])
    p.start()

    print 'waiting for subprocess to finished'

    with cond:
        while 1:
            cond.wait(1)
            if Global.finished:
                break
            else:
                print '.',
                sys.stdout.flush()

    print '\njoining'
    p.join()


#### TEST_EVENT

def event_func(event):
    print '\t%r is waiting' % currentProcess()
    event.wait()
    print '\t%r has woken up' % currentProcess()

def test_event():
    event = manager.Event()
    
    processes = [Process(target=event_func, args=[event]) for i in range(5)]

    for p in processes:
        p.start()
        
    print 'main is sleeping'
    time.sleep(2)

    print 'main is setting event'
    event.set()

    for p in processes:
        p.join()
        

#### TEST_RECURSION

def test_recursion(level=3):
    print '    ' * (3-level), currentProcess()
    if level > 0:
        for i in range(2):
            p = Process(target=test_recursion, args=[level-1])
            p.start()
            p.join()


#### TEST_BIGDATA

def test_bigdata():
    n = manager.Namespace()

    x = range(100000)
    n.value = x
    y = n.value
    if x == y:
        print "x == y as required"
    else:
        print "x != y --- error"


#### TEST_QUEUESPEED

def queuespeed_func(q, c, iterations):
    with c:
        c.notify()
    
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

        with c:
            p.start()
            c.wait()

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
    
    
def main():
    global manager

    with Manager() as manager:

        for func in [

            test_namespace, test_dict, test_list, test_subclass,
            test_queue, test_condition, test_semaphore, test_wait,
            test_event, test_recursion, test_bigdata, test_queuespeed,
            test_dictspeed, test_client,
            
            ]:

            print
            print
            print '        ########', func.__name__
            print

            func()

        print
        print 'manager._info() =', manager._info()
        

if __name__ == '__main__':
    main()
