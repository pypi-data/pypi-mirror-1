#
# A test file for the processing package (and processing.dummy)
#

import time, sys, random
from Queue import Empty

if 'use_dummy' not in globals() or not use_dummy:
    from processing import *
else:
    from processing.dummy import *


#### TEST_NAMESPACE

def namespace_func(Global, mutex):
    random.seed()
    time.sleep(random.random()*4)

    mutex.acquire()
    print '\n\t\t\t' + str(currentProcess()) + ' has finished'
    Global.running -= 1
    mutex.release()

def test_namespace():
    Global = manager.Namespace()
    mutex = manager.Lock()
    
    Global.running = TASKS = 10

    processes = [Process(target=namespace_func, args=[Global, mutex])
                 for i in range(TASKS)]

    for p in processes:
        p.start()

    while Global.running:
        time.sleep(0.08)
        mutex.acquire()
        print Global.running,
        sys.stdout.flush()
        mutex.release()

    print
    print 'No more running processes'

    for p in processes:
        p.join()

    del Global.running
    Global.cat = 'lion'
    Global.country = 'laos'

    print
    print 'repr(Global) =', repr(Global)
    print 'str(Global) =', str(Global)


#### TEST_DICT

def test_dict():
    d = manager.dict()
    
    for i in xrange(8):
        d[i] = chr(65 + i)

    print d.copy()

    for item in d.iteritems():
        print item,


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
        self.mutex.acquire()
        print '\t' + str(self.mutex)
        time.sleep(1)
        self.mutex.release()

def test_subclass():
    mutex = manager.RLock()
    
    print mutex
    p = Subclass(mutex)

    mutex.acquire()
    print mutex
    p.start()
    time.sleep(2)
    mutex.release()

    p.join()
    print mutex

    
#### TEST_QUEUE

def queue_func(queue):
    for i in xrange(30):
        time.sleep(0.5 * random.random())
        queue.put(i*i)
    queue.put('STOP')
    
def test_queue():
    q = manager.Queue()
    
    p = Process(target=queue_func, args=[q])
    p.start()

    o = None
    while o != 'STOP':
        try:
            o = q.get(timeout=0.3)
            print o,
            sys.stdout.flush()
        except Empty:
            print 'TIMEOUT'

    p.join()

    
#### TEST_CONDITION

def condition_func(cond):
    cond.acquire()
    print '\t' + str(cond)
    time.sleep(2)
    print '\tchild is notifying'
    print '\t' + str(cond)
    cond.notify()
    cond.release()

def test_condition():
    cond = manager.Condition()
    
    p = Process(target=condition_func, args=[cond])
    print cond

    cond.acquire()
    print cond
    cond.acquire()
    print cond
    
    p.start()
    
    print 'main is waiting'
    cond.wait()
    print 'main has woken up'
    
    print cond
    cond.release()
    print cond
    cond.release()

    p.join()
    print cond


#### TEST_SEMAPHORE

def semaphore_func(sema, mutex, Global):
    sema.acquire()

    mutex.acquire()
    Global.running += 1
    print Global.running, 'tasks are running'
    mutex.release()

    random.seed()
    time.sleep(random.random()*2)

    mutex.acquire()
    Global.running -= 1
    print '%s has finished' % currentProcess()
    mutex.release()

    sema.release()

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

    cond.acquire()
    Global.finished = True
    print '\nchild notifying that finished'
    cond.notify()
    cond.release()

def test_wait():
    Global = manager.Namespace()
    cond = manager.Condition()
    
    Global.finished = False

    p = Process(target=wait_func, args=[Global, cond])
    p.start()

    print 'waiting for process to finished'

    cond.acquire()

    while 1:
        cond.wait(1)
        if Global.finished:
            break
        else:
            print '.',
            sys.stdout.flush()

    cond.release()

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
    

####
        
def main():
    global manager

    manager = Manager()

    try:

        for func in [
            
            test_namespace, test_dict, test_list, test_subclass,
            test_queue, test_condition, test_semaphore, test_wait,
            test_event, test_recursion, test_bigdata
            
            ]:
            
            print
            print
            print '        ########', func.__name__
            print
            
            func()
            
        values = manager._info().values()
        assert values == [0] * len(values)


    finally:
        
        manager.shutdown()


if __name__ == '__main__':
    main()
