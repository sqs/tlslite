import os, sys
from tlslite.api import *

def get_x509(cert, key):
    testdir = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
    serverX509Cert = X509().parse(open(os.path.join(testdir, cert)).read())
    serverX509Chain = X509CertChain([serverX509Cert])
    s = open(os.path.join(testdir, key)).read()
    serverX509Key = parsePEMKey(s, private=True)
    return (serverX509Cert, serverX509Chain, serverX509Key)

class X509Mixin(object):
    def make_server_x509(self):
        x = get_x509("serverX509Cert.pem", "serverX509Key.pem")
        self.serverX509Cert = x[0]
        self.serverX509Chain = x[1]
        self.serverX509Key = x[2]

    def make_client_x509(self):
        x = get_x509("clientX509Cert.pem", "clientX509Key.pem")
        self.clientX509Cert = x[0]
        self.clientX509Chain = x[1]
        self.clientX509Key = x[2]

