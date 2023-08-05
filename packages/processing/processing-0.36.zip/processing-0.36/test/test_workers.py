#
# Simple example which uses a pool of workers to carry out some tasks.
#
# Note that a queue produced by `processing.Queue()` will have finite
# capacity meaning that its `put()` method can block.  Therefore we
# use a queue using `processing.BufferedQueue()`.  This has the
# guarantee that the `put()` (or `putmany()`) method will succeed
# without blocking.  Therefore putting all the tasks on this queue
# will not cause a deadlock, regardless of how many tasks there are,
# or whether there is another process which is already consuming the
# tasks.
#
# Also notice that the results will probably not come out of the
# output queue in the same in the same order as the corresponding
# tasks were put on the input queue.  If it is important to get the
# results back in the original order then consider using `Pool.map()`
# or `Pool.imap()`.
#

import time
import random

from processing import currentProcess, Process, freezeSupport
from processing import Queue, BufferedQueue

#
# Function run by worker processes
#

def worker(input, output):
    for item in iter(input.get, 'STOP'):
        func, args = item
        result = calculate(func, args)
        output.put(result)

#
# Function used to calculate result
#

def calculate(func, args):
    result = func(*args)
    return '%s says that %s%s = %s' % \
        (currentProcess().getName(), func.__name__, args, result)

#
# Functions referenced by tasks
#

def mul(a, b):
    time.sleep(0.5*random.random())
    return a * b

def plus(a, b):
    time.sleep(0.5*random.random())
    return a + b

#
#
#

def test():
    NUMBER_OF_PROCESSES = 4
    TASKS1 = [(mul, (i, 7)) for i in range(20)]
    TASKS2 = [(plus, (i, 8)) for i in range(10)]
    
    # Create queues
    task_queue = BufferedQueue()
    done_queue = Queue()
    
    # Submit tasks -- no deadlock possible since `task_queue` is buffered
    for task in TASKS1:
        task_queue.put(task)
        
    # Start worker processes
    for i in range(NUMBER_OF_PROCESSES):
        Process(target=worker, args=[task_queue, done_queue]).start()
        
    # Get and print results
    print 'Unordered results:'
    for i in range(len(TASKS1)):
        print '\t', done_queue.get()
        
    # Add more tasks -- `putmany()` is an alternative to `put()` and a for-loop
    task_queue.putmany(TASKS2)
    
    # Get and print some more results
    for i in range(len(TASKS2)):
        print '\t', done_queue.get()
        
    # Tell child processes to stop
    for i in range(NUMBER_OF_PROCESSES):
        task_queue.put('STOP')


if __name__ == '__main__':
    freezeSupport()
    test()
