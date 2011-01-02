import unittest

from .clientserver import *
from tlslite.api import *

class TestResume(unittest.TestCase):
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

    def __server_srp_sessioncache(self, session_cache):
        sc = self.server.connect()
        sc.handshakeServer(verifierDB=self.verifierDB, sessionCache=session_cache)
        sc.close()
        sc.sock.close()

    def __server_srp_sessioncache_invalidated_resumption(self, session_cache):
        sc = self.server.connect()
        sc.handshakeServer(verifierDB=self.verifierDB, sessionCache=session_cache)

        try:
            sc.read(min=1, max=1)
            assert() #Client is going to close the socket without a close_notify
        except TLSAbruptCloseError, e:
            pass
        
        sc = self.server.connect()
        try:
            sc.handshakeServer(verifierDB=self.verifierDB, sessionCache=session_cache)
        except TLSLocalAlert, alert:
            if alert.description != AlertDescription.bad_record_mac:
                raise
        sc.close()
        sc.sock.close()

    def test_resume(self):
        session = None
        session_cache = SessionCache()
        with ServerThread(self.server, self.__server_srp_sessioncache, session_cache):
            with TestClient() as cc:
                cc.handshakeClientSRP("test", "password")
                session = cc.session
        self.assertTrue(session)

        with ServerThread(self.server, self.__server_srp_sessioncache, session_cache):
            with TestClient() as cc:
                cc.handshakeClientSRP("test", "garbage", session=session)

    def test_invalidated_resumption(self):
        # set up session as in test_resume
        session = None
        session_cache = SessionCache()
        with ServerThread(self.server, self.__server_srp_sessioncache_invalidated_resumption, session_cache):
            client = TestClient()
            cc = client.connect()
            cc.handshakeClientSRP("test", "password")
            session = cc.session
            self.assertTrue(session)
            cc.sock.close() #Close the socket without a close_notify!

            cc = client.connect()
            try:
                cc.handshakeClientSRP("test", "garbage", session=session)
                assert()
            except TLSRemoteAlert, alert:
                if alert.description != AlertDescription.bad_record_mac:
                    raised
            cc.sock.close()

            

        
