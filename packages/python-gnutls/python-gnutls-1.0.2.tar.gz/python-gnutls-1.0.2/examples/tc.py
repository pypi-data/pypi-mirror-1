#!/usr/bin/python

"""Asynchronous client using Twisted with GNUTLS"""

import sys
import os
from time import time

from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineOnlyReceiver
from twisted.protocols.policies import TimeoutMixin
from twisted.internet import reactor

from gnutls.constants import *
from gnutls.crypto import *
from gnutls.errors import *
from gnutls.interfaces.twisted import X509Credentials

class EchoProtocol(LineOnlyReceiver, TimeoutMixin):

    def connectionMade(self):
        print "connection made. send 'echo' and set timeout to 5 seconds"
        self.start = time()
        self.setTimeout(5)
        self.sendLine('echo')

    def lineReceived(self, line):
        print 'received %s @ %s ' % (line, time() - self.start)
        self.setTimeout(None)
        self.transport.loseConnection()

    def connectionLost(self, reason):
        print "connection lost @ %s" % (time() - self.start,)
        reactor.stop()

    def timeoutConnection(self):
        print "connection did timeout @ %s" % (time() - self.start,)
        self.transport.credentials.session_params.bye_timeout = 5
        self.transport.loseConnection()

class EchoFactory(ClientFactory):
    protocol = EchoProtocol

    def clientConnectionFailed(self, connector, err):
        print err.value
        reactor.stop()


script_path = os.path.realpath(os.path.dirname(sys.argv[0]))
certs_path = os.path.join(script_path, 'certs')

cert = X509Certificate(open(certs_path + '/valid.crt').read())
key = X509PrivateKey(open(certs_path + '/valid.key').read())
ca = X509Certificate(open(certs_path + '/ca.pem').read())
crl = X509CRL(open(certs_path + '/crl.pem').read())
cred = X509Credentials(cert, key, [ca])
cred.verify_peer = True

reactor.connectTLS('localhost', 10000, EchoFactory(), cred)
reactor.run()

