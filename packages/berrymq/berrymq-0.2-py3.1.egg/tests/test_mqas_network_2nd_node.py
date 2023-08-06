# -*- coding: utf-8 -*-

mqas = None

import time
import xmlrpc.client


def test_twitter_from_client(server):
    mqas.twitter("twitter_test_from_client:call")
    time.sleep(1)
    assert server.check_test1_result()
    print("mqas: test_twitter_from_client() OK!")


def test(mqas_module):
    global mqas
    mqas = mqas_module
    server = xmlrpc.client.ServerProxy("http://localhost:9999")
    mqas.p2p.p2p_init("http://localhost:12346")
    mqas.p2p.p2p_connect("http://localhost:12345")
    test_twitter_from_client(server)
    server.quit()
    mqas.p2p.p2p_quit()


