import unittest
import sys, os, SimpleHTTPServer, socket, time

from .clientserver import *
from tlslite.api import *


class TestHTTPS(unittest.TestCase):
    def setUp(self):
        incr_server_port()
        self.server_addr = ('127.0.0.1', config['server_port'])
        print self.server_addr
        self.httpd = MyHTTPServer(self.server_addr, SimpleHTTPServer.SimpleHTTPRequestHandler)
        self.__cd_to_test_dir()

    def __cd_to_test_dir(self):
        self.testdir = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
        self.saved_cwd = os.getcwd()
        os.chdir(self.testdir)

    def tearDown(self):
        self.httpd.server_close()
        os.chdir(self.saved_cwd)

    def test_https_x509(self):
        def handle_requests():
            for x in range(6):
                self.httpd.handle_request()
        with ServerThread(self.httpd, handle_requests):
            timeoutEx = socket.timeout
            while 1:
                try:
                    time.sleep(1)
                    htmlBody = open(os.path.join(self.testdir, "index.html")).read()
                    fingerprint = None
                    for y in range(2):
                        h = HTTPTLSConnection(self.server_addr[0], self.server_addr[1], x509Fingerprint=fingerprint)
                        for x in range(3):
                            h.request("GET", "/index.html")
                            r = h.getresponse()
                            assert(r.status == 200)
                            s = r.read()
                            assert(s == htmlBody)
                        fingerprint = h.tlsSession.serverCertChain.getFingerprint()
                        self.assertTrue(fingerprint)
                    time.sleep(1)
                    break
                except timeoutEx:
                    print "timeout, retrying..."
                    pass

