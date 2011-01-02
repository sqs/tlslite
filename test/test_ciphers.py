import unittest

from .clientserver import *
from .helpers import *
from tlslite.api import *

class TestCiphers(unittest.TestCase, SharedKeyMixin):
    def setUp(self):
        incr_server_port()
        self.server = TestServer()
        self.__make_implementations()
        self.make_shared_key_db()
        self.ciphers = ['aes128', 'aes256', 'rc4']
    
    def __make_implementations(self):
        self.impls = []
        if cryptlibpyLoaded:
            self.impls.append("cryptlib")
        if m2cryptoLoaded:
            self.impls.append("openssl")
        if pycryptoLoaded:
            self.impls.append("pycrypto")
        self.impls.append("python")

    def __server_cipher(self, impl, cipher):
        sc = self.server.connect()
        settings = HandshakeSettings()
        settings.cipherNames = [cipher]
        settings.cipherImplementations = [impl, "python"]
        sc.handshakeServer(sharedKeyDB=self.sharedKeyDB, settings=settings)
        print sc.getCipherName(), sc.getCipherImplementation()
        h = sc.read(min=5, max=5)
        assert "hello" == h
        sc.write(h)
        sc.close()
        sc.sock.close()
    
    def test_ciphers(self):
        for impl in self.impls:
            for cipher in self.ciphers:
                with ServerThread(self.server, self.__server_cipher, impl, cipher):
                    with TestClient() as cc:
                        settings = HandshakeSettings()
                        settings.cipherNames = [cipher]
                        settings.cipherImplementations = [impl, "python"]
                        cc.handshakeClientSharedKey("shared", "key", settings=settings)
                        print "%s %s" % (cc.getCipherName(), cc.getCipherImplementation())

                        cc.write("hello")
                        h = cc.read(min=5, max=5)
                        self.assertEquals("hello", h)
