import unittest, os, sys

from .clientserver import *
from tlslite.api import *

class TestSRP(unittest.TestCase):
    def setUp(self):
        self.client = TestClient()
        self.server = TestServer()
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

