# -*- coding: utf-8 -*-

mqas = None


from xmlrpc.server import SimpleXMLRPCServer


running = True


def quit():
    global running
    running = False
    return True


def run_server(server):
    print("start running 1st test node")
    global running
    while running:
        server.handle_request()
    mqas.p2p.p2p_quit()

test1_result = False


def check_test1_result():
    return test1_result


def test(mqas_module):
    global mqas
    mqas = mqas_module
    server = SimpleXMLRPCServer(("localhost", 9999))
    server.register_function(quit)
    server.register_function(check_test1_result)
    mqas.p2p.p2p_init("http://localhost:12345")

    # test1

    @mqas.following_function("twitter_test_from_client:call")
    def test_receiver(message):
        print("twitter_test_from_client:call called")
        global test1_result
        test1_result = True

    print(mqas.show_followers())

    run_server(server)
