# -*- coding: utf-8 -*-

import urllib.parse
import xmlrpc.client
import xmlrpc.server
import threading

_stop_server = False
_server = None
_receiver = None
_server_thread = None


def _is_p2p_init():
    return _server is not None

def p2p_init(url):
    from . import mqas
    if _is_p2p_init():
        raise RuntimeError("p2p connection is already initialized")
    global _server
    global _stop_server
    global _receiver
    global _server_thread
    netloc = urllib.parse.urlparse(url)[1]
    host, port = netloc.split(":")
    _server = xmlrpc.server.SimpleXMLRPCServer((host, int(port)))
    _receiver = mqas.MessageQueueReceiver(url)
    _server.register_instance(_receiver)
    _stop_server = False

    def _p2p_main():
        global _stop_server
        while not _stop_server:
            _server.handle_request()

    _server_thread = threading.Thread(target=_p2p_main)
    _server_thread.start()


def p2p_connect(url):
    if not _is_p2p_init():
        raise RuntimeError("p2p connection is not initialized")
    _receiver._add_connection(url)


def p2p_quit():
    if not _is_p2p_init():
        raise RuntimeError("p2p connection is not initialized")
    global _stop_server
    _stop_server = True
    p2p_mainloop()


def p2p_mainloop():
    if not _is_p2p_init():
        raise RuntimeError("p2p connection is not initialized")
    _server_thread.join()
