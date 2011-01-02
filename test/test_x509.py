import unittest, os, sys

from .clientserver import *
from tlslite.api import *

class TestX509(unittest.TestCase):
    def setUp(self):
        incr_server_port()
        self.server = TestServer()
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

    def __server_x509_sslv3(self):
        sc = self.server.connect()
        settings = HandshakeSettings()
        settings.minVersion = (3,0)
        settings.maxVersion = (3,0)
        sc.handshakeServer(certChain=self.x509Chain,
                           privateKey=self.x509Key,
                           settings=settings)
        sc.close()
        sc.sock.close()

    def test_good_x509(self):
        with ServerThread(self.server, self.__server_x509):
            with TestClient() as cc:
                cc.handshakeClientCert()
                assert(isinstance(cc.session.serverCertChain, X509CertChain))

    def test_good_x509_sslv3(self):
        with ServerThread(self.server, self.__server_x509_sslv3):
            with TestClient() as cc:
                settings = HandshakeSettings()
                settings.minVersion = (3,0)
                settings.maxVersion = (3,0)
                cc.handshakeClientCert(settings=settings)
                self.assertTrue(isinstance(cc.session.serverCertChain, X509CertChain))
