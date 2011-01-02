import unittest, os, sys

from .clientserver import *
from .helpers import *
from tlslite.api import *

class TestX509(unittest.TestCase, X509Mixin):
    def setUp(self):
        incr_server_port()
        self.server = TestServer()
        self.make_server_x509()
        self.make_client_x509()

    def tearDown(self):
        self.server.close()

    def __server_x509(self):
        sc = self.server.connect()
        sc.handshakeServer(certChain=self.serverX509Chain,
                           privateKey=self.serverX509Key)
        sc.close()
        sc.sock.close()

    def __server_x509_sslv3(self):
        sc = self.server.connect()
        settings = HandshakeSettings()
        settings.minVersion = (3,0)
        settings.maxVersion = (3,0)
        sc.handshakeServer(certChain=self.serverX509Chain,
                           privateKey=self.serverX509Key,
                           settings=settings)
        sc.close()
        sc.sock.close()

    def __server_x509_fault(self, fault):
        sc = self.server.connect()
        sc.fault = fault
        sc.handshakeServer(certChain=self.serverX509Chain,
                           privateKey=self.serverX509Key)
        sc.close()
        sc.sock.close()

    def __server_mutual_x509_fault(self, fault):
        sc = self.server.connect()
        sc.fault = fault
        sc.handshakeServer(certChain=self.serverX509Chain,
                           privateKey=self.serverX509Key,
                           reqCert=True)
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

    def test_x509_fault(self):
        for fault in Fault.clientNoAuthFaults + Fault.genericFaults:
            with ServerThread(self.server, self.__server_x509_fault, fault):
                with TestClient() as cc:
                    cc.fault = fault
                    try:
                        cc.handshakeClientCert()
                    except TLSFaultError as e:
                        print "Bad fault: %s %s" % (Fault.faultNames[fault], str(e))
                        raise e

    def test_mutual_x509(self):
        with ServerThread(self.server, self.__server_x509):
            with TestClient() as cc:
                cc.handshakeClientCert(self.clientX509Chain, self.clientX509Key)
                self.assertTrue(isinstance(cc.session.serverCertChain, X509CertChain))

    def test_mutual_x509_sslv3(self):
        with ServerThread(self.server, self.__server_x509_sslv3):
            with TestClient() as cc:
                settings = HandshakeSettings()
                settings.minVersion = (3,0)
                settings.maxVersion = (3,0)
                cc.handshakeClientCert(self.clientX509Chain, self.clientX509Key, settings=settings)
                self.assertTrue(isinstance(cc.session.serverCertChain, X509CertChain))

    def test_x509_fault(self):
        for fault in Fault.clientCertFaults + Fault.genericFaults:
            with ServerThread(self.server, self.__server_mutual_x509_fault, fault):
                with TestClient() as cc:
                    cc.fault = fault
                    try:
                        cc.handshakeClientCert(self.clientX509Chain, self.clientX509Key)
                    except TLSFaultError as e:
                        print "Bad fault: %s %s" % (Fault.faultNames[fault], str(e))
                        raise e
