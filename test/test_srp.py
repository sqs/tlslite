import unittest, os, sys

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

    def __server_srp(self):
        sc = self.server.connect()
        sc.handshakeServer(verifierDB=self.verifierDB)
        sc.close()
        sc.sock.close()
        
    def test_good_srp(self):
        with ServerThread(self.server, self.__server_srp):
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

    def test_unknown_srp_username(self):
        with ServerThread(self.server, self.__server_srp):
            def srpCallback():
                return ("test", "password")
            cc = self.client.connect()
            cc.handshakeClientUnknown(srpCallback=srpCallback)
            cc.close()
            cc.sock.close()

    def test_srp_x509(self):
        def server_srp_x509():
            mydir = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
            x509Cert = X509().parse(open(os.path.join(mydir, "serverX509Cert.pem")).read())
            x509Chain = X509CertChain([x509Cert])
            s = open(os.path.join(mydir, "serverX509Key.pem")).read()
            x509Key = parsePEMKey(s, private=True)

            sc = self.server.connect()
            sc.handshakeServer(verifierDB=self.verifierDB, \
                               certChain=x509Chain, privateKey=x509Key)
            sc.close()
            sc.sock.close()

        with ServerThread(self.server, server_srp_x509):
            cc = self.client.connect()
            cc.handshakeClientSRP("test", "password")
            assert(isinstance(cc.session.serverCertChain, X509CertChain))
            cc.close()
            cc.sock.close()


