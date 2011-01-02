import unittest, os, sys

from .clientserver import *
from tlslite.api import *

class TestSharedKey(unittest.TestCase):
    def setUp(self):
        global SERVER_PORT
        SERVER_PORT += 1
        self.server = TestServer('127.0.0.1', SERVER_PORT)
        self.client = TestClient('127.0.0.1', SERVER_PORT)
        self.__make_shared_key_db()

    def tearDown(self):
        self.server.close()

    def __make_shared_key_db(self):
        self.sharedKeyDB = SharedKeyDB()
        self.sharedKeyDB["shared"] = "key"
        self.sharedKeyDB["shared2"] = "key2"

    def __server_shared_key(self):
        sc = self.server.connect()
        sc.handshakeServer(sharedKeyDB=self.sharedKeyDB)
        sc.close()
        sc.sock.close()

    def test_good_shared_key(self):
        with ServerThread(self.server, self.__server_shared_key):
            cc = self.client.connect()
            cc.handshakeClientSharedKey("shared", "key")
            cc.close()
            cc.sock.close()

