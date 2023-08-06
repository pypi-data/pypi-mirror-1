from client import *
from server import *

def test():
    if not len(sys.argv) > 1:
        import socket
        print 'Running JSON-RPC server on port 8000'
        server = SimpleJSONRPCServer(("localhost", 8000))
        server.register_function(pow)
        server.register_function(lambda x,y: x+y, 'add')
        server.serve_forever()
    else:
        remote = ServerProxy(sys.argv[1])
        print 'Using connection', remote

        print repr(remote.add(1, 2))
        aaa = remote.add
        print repr(remote.pow(2, 4))
        print aaa(5, 6)

        try:
            # Invalid parameters
            aaa(5, "toto")
            print "Successful execution of invalid code"
        except Fault:
            pass

        try:
            # Invalid parameters
            aaa(5, 6, 7)
            print "Successful execution of invalid code"
        except Fault:
            pass

        try:
            # Invalid method name
            print repr(remote.powx(2, 4))
            print "Successful execution of invalid code"
        except Fault:
            pass


if __name__ == '__main__':
	test()
