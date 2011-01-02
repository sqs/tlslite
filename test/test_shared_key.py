import unittest, os, sys

from .clientserver import *
from tlslite.api import *

class TestSharedKey(unittest.TestCase):
    def setUp(self):
        incr_server_port()
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

    def __server_shared_key_fault(self, fault):
        sc = self.server.connect()
        sc.fault = fault
        sc.handshakeServer(sharedKeyDB=self.sharedKeyDB)
        sc.close()
        sc.sock.close()

    def test_good_shared_key(self):
        with ServerThread(self.server, self.__server_shared_key):
            with TestClient() as cc:
                cc.handshakeClientSharedKey("shared", "key")

    def test_shared_key_fault(self):
        for fault in Fault.clientSharedKeyFaults + Fault.genericFaults:
            with ServerThread(self.server, self.__server_shared_key_fault, fault):
                with TestClient() as cc:
                    cc.fault = fault
                    good_fault = False
                    try:
                        cc.handshakeClientSharedKey("shared", "key")
                        good_fault = True
                    except TLSFaultError as e:
                        print "Bad fault: %s %s" % (Fault.faultNames[fault],
                                                str(e))
                        raise e
                    self.assertTrue(good_fault)

