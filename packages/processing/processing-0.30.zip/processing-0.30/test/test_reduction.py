#
# We test the sharing of connection objects and sockets between processes
#
# Will if `processing._processing` is available.
#

manager_type = globals().get('manager_type', 'normal')

if manager_type == 'normal':
    from processing import *
    from processing.connection import Listener, Client, families, \
         connections_are_picklable
    import socket
elif manager_type == 'dummy':
    from processing.dummy import *
    from processing.dummy.connection import *
    from processing.dummy.connection import Listener, Client, families, \
         connections_are_picklable
else:
    raise ValueError

#
# Test functions
#

def child_client(address):
    conn_to_parent = Client(address)
    conn = conn_to_parent.recv()
    print 'child received %s' % conn
    if hasattr(conn, 'poll'):
        print 'child receiving message over connection: %r' % conn.recv()
    else:
        print 'child receiving message over socket: %r' % conn.recv(100)


def remote_conn_client(address):
    c = Client(address)
    c.send('hello world')

def remote_socket_client(address):
    s = socket.socket()
    s.connect(address)
    s.send('hello world')

def _test(family, use_socket=False):
    # start child process and set up a connection with it
    child_listener = Listener()
    child_process = Process(target=child_client,
                            args=[child_listener.address])
    
    child_process.start()
    child_conn = child_listener.accept()
    child_listener.close()

    if use_socket:
        listener = socket.socket()
        listener.bind(('localhost', 0))
        listener.listen(1)
        address = listener.getsockname()
    else:
        listener = Listener(family=family)
        address = listener.address

    # start a pretend remote client
    if use_socket:
        remote_process = Process(target=remote_socket_client, args=[address])
    else:
        remote_process = Process(target=remote_conn_client, args=[address])
    remote_process.start()

    # accept a connection from remote client
    if use_socket:
        conn = listener.accept()[0]
    else:
        conn = listener.accept()

    # send connection object to child process
    print 'parent sending %r' % conn
    child_conn.send(conn)

    # join processes
    remote_process.join()
    child_process.join()

    
def test():

    if not connections_are_picklable:
        import sys
        
        print >>sys.stderr, '''
        Cannot run `test_reduction.test()`.
        
        You need to have compiled the C extension
        `processing._processing` to transfer file descriptors/handles
        between processes.
        '''
        return

    for fam in families:
        print '\n    #### Using family=%s\n' % fam
        _test(fam)

    if 'AF_INET' in families:
        print '\n    #### Using real sockets\n'
        _test(None, use_socket=True)
    
if __name__ == '__main__':
    test()
