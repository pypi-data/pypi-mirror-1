manager_type = globals().get('manager_type', 'normal')

if manager_type == 'normal':
    from processing import *
    from processing.connection import Listener, Client, families
elif manager_type == 'dummy':
    from processing.dummy import *
    from processing.dummy.connection import Listener, Client, families
else:
    raise ValueError


import socket, threading

#
#
#

long_list = range(1000)
long_string = str(long_list)
length = len(long_string)

#
# Test functions for connection objects
#

def foo(address):
    conn = Client(address)
    
    conn.send(long_list)
    conn._send_string(long_string)


def test_conn(conn, use_wrapped_socket=False):
    obj = conn.recv()
    assert obj == long_list, (len(obj), len(long_string))
    print 'Test passed: send() / recv()'

    s = conn._recv_string()
    assert s == long_string, (len(s), len(long_string))
    print 'Test passed: send_string() / recv_string()'

#
# Test functions for socket objects produced by `socket.fromfd()`
#

def bar(address):
    conn = Client(address)
    sock = socket.fromfd(conn.fileno(), socket.AF_INET, socket.SOCK_STREAM)
    sock = socket.socket(_sock=sock)
    
    ##
    
    sock.sendall(long_string)
    
    ##
    
    s = long_string
    while s:
        n = sock.send(s)
        s = s[n:]
        
    ##
        
    f = sock.makefile()
    f.write(long_string + '\n')
    f.write('the end\n')
    f.flush()
    del f

    ##
        
    sock.close()


def test_fromfd(fd):
    sock = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
    sock = socket.socket(_sock=sock)
    
    ##
    
    remaining = length
    s = ''
    while remaining > 0:
        bufsize = min(8192, remaining)
        temp = sock.recv(bufsize)
        s += temp
        remaining -= len(temp)
    assert s == long_string, (len(s), len(long_string))
    print 'Test passed: sendall() / recv()'
    
    ###

    remaining = length
    s = ''
    while remaining > 0:
        bufsize = min(8192, remaining)
        temp = sock.recv(bufsize)
        s += temp
        remaining -= len(temp)
    assert s == long_string, (len(s), len(long_string))
    print 'Test passed: send() / recv()'

    ###

    f = sock.makefile()
    s = f.readline()
    assert s == long_string + '\n'
    s = f.readline()
    assert s == 'the end\n', s
    del f
    print 'Test passed: socket.makefile()'

    ###
    
    for i in range(3):
        temp = sock.recv(8192)
        assert temp == '', 'temp = %r' % temp
    print 'Test passed: sock.recv(...) == "" at EOF'
    
#
#
#

def test():
    
    for fam in families:
        print '\tUsing family=%r\n' % fam
        l = Listener(family=fam)        
        p = Process(target=foo, args=[l.address])
        p.start()
        conn = l.accept()
        test_conn(conn)
        p.join()
        print
                
    if hasattr(socket, 'fromfd') and not issubclass(Process, threading.Thread):
        print '\tTesting socket.fromfd()\n'
        l = socket.socket()
        l.bind(('localhost', 0))
        l.listen(1)
        address = l.getsockname()
        p = Process(target=bar, args=[address])
        p.start()
        conn, _ = l.accept()
        test_fromfd(conn.fileno())
        p.join()
        print
        
if __name__ == '__main__':
    test()
