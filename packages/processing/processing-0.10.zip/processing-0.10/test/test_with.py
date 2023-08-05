#
# A test file for the processing package (and processing.dummy)
#

from __future__ import with_statement

import time, sys, random

#from processing import *
from processing.dummy import *
from Queue import Empty


#### TEST_NAMESPACE

def namespace_func(glob, mutex):    
    random.seed()
    time.sleep(random.random()*4)

    with mutex:
        print '\n\t\t\t' + str(currentProcess()) + ' has finished'
        glob.running -= 1


def test_namespace():
    glob = manager.Namespace()
    mutex = manager.Lock()
    
    glob.running = TASKS = 10

    for i in xrange(TASKS):
        Process(target=namespace_func, args=[glob, mutex]).start()

    while glob.running:
        time.sleep(0.08)
        with mutex:
            print glob.running,
            sys.stdout.flush()

    print
    print 'No more running processes'

    del glob.running
    glob.cat = 'lion'
    glob.country = 'laos'

    print
    print 'repr(glob) =', repr(glob)
    print 'Repr(glob) =', Repr(glob)


#### TEST_DICT

def test_dict():
    d = manager.dict()

    for i in xrange(10):
        d[i] = chr(65 + i)
    print d.copy()


#### TEST_LIST

def test_list():
    l = manager.list(range(10))
    
    l.extend(range(100, 105))
    l.reverse()
    print l[:]


#### TEST_SUBCLASS

class Subclass(Process):

    def __init__(self, mutex):
        Process.__init__(self)
        self.mutex = mutex

    def run(self):
        with self.mutex:
            print '\tchild has acquired'
            print '\t' + Repr(self.mutex)
            time.sleep(1)
            print '\tchild is releasing'

def test_subclass():
    mutex = manager.RLock()
    
    print Repr(mutex)
    p = Subclass(mutex)

    with mutex:
        print 'main has acquired'
        print Repr(mutex)

        p.start()

        time.sleep(2)
        print 'main is releasing'

    p.join()
    print 'main has joined'
    print Repr(mutex)


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
        print '\tchild has acquired'
        print '\t' + Repr(cond)
        print '\tchild is sleeping'
        time.sleep(2)
        cond.notify()
        print '\tchild has notified'
        print '\tchild is releasing'

def test_condition():    
    cond = manager.Condition()
    
    p = Process(target=condition_func, args=[cond])
    print Repr(cond)

    with cond:
        with cond:
            print 'main has acquired twice'
            print Repr(cond)

            p.start()

            print 'main is waiting'
            cond.wait()
            print 'main has woken up'

            print Repr(cond)
            print 'main is releasing twice'

    p.join()
    print 'main has joined'
    print Repr(cond)


#### TEST_SEMAPHORE

def semaphore_func(sema, mutex, glob):        
    with sema:
        with mutex:
            glob.running += 1
            print glob.running, 'tasks are running'

        random.seed()
        time.sleep(random.random()*2)

        with mutex:
            glob.running -= 1
            print currentProcess(), 'has finished:', glob.running, \
                  'tasks are running'

def test_semaphore():
    sema = manager.Semaphore(3)
    mutex = manager.RLock()
    glob = manager.Namespace()

    glob.running = 0
    
    processes = [Process(target=semaphore_func, args=[sema, mutex, glob])
                 for i in range(10)]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
      
#### TEST_WAIT

def wait_func(glob, cond):        
    time.sleep(5.5)

    with cond:
        glob.finished = True
        print '\nchild notifying that finished'
        cond.notify()


def test_wait():
    glob = manager.Namespace()
    cond = manager.Condition()

    glob.finished = False

    p = Process(target=wait_func, args=[glob, cond])
    p.start()

    print 'waiting for subprocess to finished'

    with cond:
        while 1:
            cond.wait(1)
            if glob.finished:
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

def queuespeed_func(q, iterations):
    t = time.time()
    
    for i in xrange(iterations):
        q.put(i)
        
    q.put('STOP')
    q.put(time.time()-t)

def test_queuespeed():
    q = manager.Queue()            

    elapsed = 0
    iterations = 1

    while elapsed < 1:
        iterations *= 2

        p = Process(target=queuespeed_func, args=[q, iterations])
        p.start()

        result = None

        while result != 'STOP':
            result = q.get()

        elapsed = q.get()
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
    t = time.time()
    send = c.send
    
    for i in xrange(iterations):
        send('hello')
        
    send('STOP')
    c.send(time.time()-t)

def test_client():
    l = Listener()
    elapsed = 0
    iterations = 1

    while elapsed < 1:
        iterations *= 2
        
        p = Process(target=client_func, args=[l.address, iterations])
        p.start()
        c = l.accept()
        recv = c.recv

        result = None
        while result != 'STOP':
            result = recv()

        elapsed = c.recv()
        p.join()

    print iterations, 'strings passed through connection in', \
          elapsed, 'seconds'
    print 'average number/sec:', iterations/elapsed


if __name__ == '__main__':

    with Manager() as manager:

        for func in (

            test_namespace, test_dict, test_list, test_subclass,
            test_queue, test_condition, test_semaphore, test_wait,
            test_event, test_recursion, test_bigdata, test_queuespeed,
            test_dictspeed, test_client,
            
            ):

            print
            print
            print '        ########', func.__name__
            print

            func()
