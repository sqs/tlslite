import unittest, os, sys

from .clientserver import *
from .helpers import *
from tlslite.api import *

class TestSRP(unittest.TestCase):
    def setUp(self):
        incr_server_port()
        self.server = TestServer()
        self.__make_verifier_db()

    def tearDown(self):
        self.server.close()

    def __make_verifier_db(self):
        self.verifierDB = VerifierDB()
        self.verifierDB.create()
        entry = VerifierDB.makeVerifier("test", "password", 1536)
        self.verifierDB["test"] = entry        

    def __server_srp(self):
        sc = self.server.connect()
        sc.handshakeServer(verifierDB=self.verifierDB)
        sc.close()
        sc.sock.close()

    def __server_srp_x509(self):
        x = get_x509("serverX509Cert.pem", "serverX509Key.pem")
        sc = self.server.connect()
        sc.handshakeServer(verifierDB=self.verifierDB, \
                               certChain=x[1], privateKey=x[2])
        sc.close()
        sc.sock.close()
        
    def test_good_srp(self):
        with ServerThread(self.server, self.__server_srp):
            with TestClient() as cc:
                cc.handshakeClientSRP("test", "password")

    def test_srp_fault(self):
        def server_srp_fault():
            sc = self.server.connect()
            self.assertRaises(sc.handshakeServer(verifierDB=self.verifierDB))
            sc.close()
            sc.sock.close()

        for fault in Fault.clientSrpFaults + Fault.genericFaults:
            with ServerThread(self.server, server_srp_fault):
                with TestClient() as cc:
                    cc.fault = fault
                    cc.handshakeClientSRP("test", "password")

    def test_unknown_psk_identity(self):
        with ServerThread(self.server, self.__server_srp):
            def srpCallback():
                return ("test", "password")
            with TestClient() as cc:
                cc.handshakeClientUnknown(srpCallback=srpCallback)

    def test_srp_x509(self):
        with ServerThread(self.server, self.__server_srp_x509):
            with TestClient() as cc:
                cc.handshakeClientSRP("test", "password")
                assert(isinstance(cc.session.serverCertChain, X509CertChain))

    def test_srp_x509_fault(self):
        for fault in Fault.clientSrpFaults + Fault.genericFaults:
            with ServerThread(self.server, self.__server_srp_x509):
                with TestClient() as cc:
                    cc.fault = fault
                    cc.handshakeClientSRP("test", "password")
