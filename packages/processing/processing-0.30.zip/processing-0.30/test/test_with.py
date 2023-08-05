#
# A test file for the processing package (and processing.dummy)
#

from __future__ import with_statement

import time, sys, random

from processing import *
from Queue import Empty


#### TEST_NAMESPACE

def namespace_func(running, mutex):
    random.seed()
    time.sleep(random.random()*4)

    with mutex:
        print '\n\t\t\t' + str(currentProcess()) + ' has finished'
        running.value -= 1

def test_namespace():
    TASKS = 10    
    running = manager.SharedValue('i', TASKS)
    mutex = manager.Lock()

    for i in range(TASKS):
        Process(target=namespace_func, args=[running, mutex]).start()
        
    while running.value > 0:
        time.sleep(0.08)
        with mutex:
            print running.value,
            sys.stdout.flush()
        
    print
    print 'No more running processes'
    
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

    print


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

def semaphore_func(sema, mutex, running):        
    with sema:
        with mutex:
            running.value += 1
            print running.value, 'tasks are running'

        random.seed()
        time.sleep(random.random()*2)

        with mutex:
            running.value -= 1
            print '%s has finished' % currentProcess()

def test_semaphore():
    sema = manager.Semaphore(3)
    mutex = manager.RLock()
    running = manager.SharedValue('i', 0)
    
    processes = [Process(target=semaphore_func, args=[sema, mutex, running])
                 for i in range(10)]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
      

#### TEST_JOIN_TIMEOUT

def join_timeout_func():
    print '\tchild sleeping'
    time.sleep(5.5)
    print '\n\tchild terminating'

def test_join_timeout():
    p = Process(target=join_timeout_func)
    p.start()

    print 'waiting for process to finish'
    
    while 1:
        p.join(timeout=1)
        if not p.isAlive():
            break
        print '.',
        sys.stdout.flush()


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


####    
    
def main():
    global manager

    with Manager() as manager:

        for func in [ test_namespace, test_queue, test_condition,
                      test_semaphore, test_join_timeout, test_event ]:
            
            print '\n\t######## %s\n' % func.__name__
            func()

        ignore = activeChildren()        # cleanup any old processes
        info = manager._debug_info()
        if info is not None:
            print info
            raise ValueError, 'there should be no positive refcounts left'
        

if __name__ == '__main__':
    main()
