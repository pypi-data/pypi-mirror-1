import berrymq.jsonrpc.server as server
import threading

_server = None

def stop_thread():
  import time
  time.sleep(1)
  _server.shutdown()
  

def stop():
 thread = threading.Thread(target=stop_thread)
 thread.start()


def main():
  global _server
  _server = server.SimpleJSONRPCServer(("localhost", 8000))
  _server.register_function(stop)
  _server.serve_forever()

if __name__ == "__main__":
  main()
