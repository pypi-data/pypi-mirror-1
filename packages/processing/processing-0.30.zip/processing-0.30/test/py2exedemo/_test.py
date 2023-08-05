import sys, time
from processing import Process, Manager

def foo(q):
    for i in range(10):
        q.put('hello world %d' % i)
        time.sleep(1)

def main():
    m = Manager()
    q = m.Queue()

    p = Process(target=foo, args=[q])
    p.start()

    for i in range(10):
        print q.get()
        sys.stdout.flush()

    p.join()
    
if __name__ == '__main__':
    main()
