import unittest

from .clientserver import *
from tlslite.api import *

class TestSRP(unittest.TestCase):
    def setUp(self):
        self.client = TestClient()
        self.server = TestServer()
        self.__make_verifier_db()

    def tearDown(self):
        self.server.close()

    def __make_verifier_db(self):
        self.verifierDB = VerifierDB()
        self.verifierDB.create()
        entry = VerifierDB.makeVerifier("test", "password", 1536)
        self.verifierDB["test"] = entry        
    
    def test_good_srp(self):
        def server_good_srp():
            sc = self.server.connect()
            sc.handshakeServer(verifierDB=self.verifierDB)
            sc.close()
            sc.sock.close()

        with ServerThread(self.server, server_good_srp):
            cc = self.client.connect()
            cc.handshakeClientSRP("test", "password")
            cc.close()
            cc.sock.close()

    def test_srp_fault(self):
        def server_srp_fault():
            sc = self.server.connect()
            self.assertRaises(sc.handshakeServer(verifierDB=self.verifierDB))
            sc.close()
            sc.sock.close()

        for fault in Fault.clientSrpFaults + Fault.genericFaults:
            with ServerThread(self.server, server_srp_fault):
                cc = self.client.connect()
                cc.fault = fault
                cc.handshakeClientSRP("test", "password")
                cc.close()
                cc.sock.close()
