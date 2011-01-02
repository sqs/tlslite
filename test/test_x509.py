import unittest, os, sys

from .clientserver import *
from tlslite.api import *

class TestX509(unittest.TestCase):
    def setUp(self):
        global SERVER_PORT
        SERVER_PORT += 1
        self.server = TestServer('127.0.0.1', SERVER_PORT)
        self.client = TestClient('127.0.0.1', SERVER_PORT)
        self.__make_x509()

    def tearDown(self):
        self.server.close()

    def __make_x509(self):
        mydir = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
        self.x509Cert = X509().parse(open(os.path.join(mydir, "serverX509Cert.pem")).read())
        self.x509Chain = X509CertChain([self.x509Cert])
        s = open(os.path.join(mydir, "serverX509Key.pem")).read()
        self.x509Key = parsePEMKey(s, private=True)

    def __server_x509(self):
        sc = self.server.connect()
        sc.handshakeServer(certChain=self.x509Chain,
                           privateKey=self.x509Key)
        sc.close()
        sc.sock.close()
        
    def test_good_x509(self):
        with ServerThread(self.server, self.__server_x509):
            cc = self.client.connect()
            cc.handshakeClientCert()
            assert(isinstance(cc.session.serverCertChain, X509CertChain))
            cc.close()
            cc.sock.close()
