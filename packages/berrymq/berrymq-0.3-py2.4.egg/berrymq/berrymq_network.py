# -*- coding: utf-8 -*-

import urlparse
import xmlrpclib
import threading
from SimpleXMLRPCServer import SimpleXMLRPCServer


_stop_server = False
_server = None
_receiver = None
_server_thread = None


def _is_network_init():
    return _server is not None


def network_init(url):
    if _is_network_init():
        raise RuntimeError("network connection is already initialized")
    global _server
    global _stop_server
    global _receiver
    global _server_thread
    netloc = urlparse.urlparse(url)[1]
    host, port = netloc.split(":")
    _server = SimpleXMLRPCServer((host, int(port)))
    _receiver = mqas.MessageQueueReceiver(url)
    _server.register_instance(_receiver)
    _stop_server = False

    def _network_main():
        global _stop_server
        while not _stop_server:
            _server.handle_request()

    _server_thread = threading.Thread(target=_network_main)
    _server_thread.start()


def network_connect(url):
    if not _is_network_init():
        raise RuntimeError("network connection is not initialized")
    _receiver._add_connection(url)


def network_quit():
    if not _is_network_init():
        raise RuntimeError("network connection is not initialized")
    global _stop_server
    _stop_server = True
    network_mainloop()


def network_mainloop():
    if not _is_network_init():
        raise RuntimeError("network connection is not initialized")
    _server_thread.join()
