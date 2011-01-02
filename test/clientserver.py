import socket, threading, random

from tlslite.api import *

TIMEOUT = 1 # secs
config = dict(server_port=random.randint(10000, 15000))

def incr_server_port():
    config['server_port'] += 1

class TestEndpoint(object):
    def __init__(self, addr='127.0.0.1', port=None):
        global SERVER_PORT
        self.addr = addr
        self.port = port if port else config['server_port']

        
class TestServer(TestEndpoint):
    def __init__(self, *args):
        TestEndpoint.__init__(self, *args)
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.lsock.bind((self.addr, self.port))
        except:
            print "Couldn't bind TestServer to %s:%d" % (self.addr, self.port)
            raise
        self.lsock.listen(TIMEOUT)

    def connect(self):
        return TLSConnection(self.lsock.accept()[0])

    def close(self):
        self.lsock.close()


class TestClient(TestEndpoint):
    def __init__(self, *args):
        TestEndpoint.__init__(self, *args)

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        sock.connect((self.addr, self.port))
        return TLSConnection(sock)

    def __enter__(self):
        self.cc = self.connect()
        return self.cc

    def __exit__(self, *args):
        self.cc.close()
        self.cc.sock.close()

class ServerThread(threading.Thread):
    def __init__(self, server, f, *args):
        threading.Thread.__init__(self)
        self.server = server
        self.run = lambda: f(*args)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.join()
