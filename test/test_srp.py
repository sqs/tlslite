import unittest

from .clientserver import *
from tlslite.api import *

class TestSRP(unittest.TestCase):
    def setUp(self):
        self.client = TestClient()
        self.server = TestServer()
    
    def test_good_srp(self):
        def server_good_srp():
            verifierDB = VerifierDB()
            verifierDB.create()
            entry = VerifierDB.makeVerifier("test", "password", 1536)
            verifierDB["test"] = entry        
            sc = self.server.connect()
            sc.handshakeServer(verifierDB=verifierDB)
            sc.close()
            sc.sock.close()

        with ServerThread(self.server, server_good_srp):
            cc = self.client.connect()
            cc.handshakeClientSRP("test", "password")
            cc.close()
            cc.sock.close()


