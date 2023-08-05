#
# Simple example which uses a pool of workers to carry out some tasks
#
# Note that a queue produced by `processing.Queue()` will have finite
# capacity meaning that its `put()` method can block.  Therefore we
# feed tasks to the queue using a subthread.  On the other hand a
# queue produced by `Queue.Queue()` (or using a manager) will by
# default has infinite capacity.
#
# Also notice that the results will probably not come out of the
# output queue in the same in the same order as the corresponding
# tasks were put on the input queue.  If it is important to get the
# results back in the original order matters then look at
# `examples/map.py` (or maybe `examples/apply.py`).
#

import time
import random

from processing import currentProcess, Process, Queue, freezeSupport
from threading import Thread

#
# Function run by worker processes
#

def worker(input, output):
    while 1:
        item = input.get()
        if item == 'STOP':
            break
        func, args = item
        output.put(calculate(func, args))

#
# Function to feed tasks to the task queue
#

def feed(queue, tasks):
    for t in tasks:
        queue.put(t)

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
    TASKS = [(mul, (i, 7)) for i in range(10)] + \
            [(plus, (i, 8)) for i in range(10)]
    
    # Create queues
    task_queue = Queue()
    done_queue = Queue()
    
    # Start worker processes
    for i in range(NUMBER_OF_PROCESSES):
        Process(target=worker, args=[task_queue, done_queue]).start()
        
    # Feed tasks to the task queue
    Thread(target=feed, args=[task_queue, TASKS]).start()
    
    # Get and print results
    print 'Unordered results:'
    for i in range(len(TASKS)):
        print '\t', done_queue.get()
        
    # Tell child processes to stop
    for i in range(NUMBER_OF_PROCESSES):
        task_queue.put('STOP')

        
if __name__ == '__main__':
    freezeSupport()
    test()
