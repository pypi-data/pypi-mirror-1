#!/usr/bin/python

"""Asynchronous client using Twisted with GNUTLS"""

import sys
import os

from zope.interface import implements

from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet import reactor, interfaces

from gnutls.constants import *
from gnutls.crypto import *
from gnutls.errors import *
from gnutls.interfaces.twisted import X509Credentials

class EchoProtocol(LineOnlyReceiver):

    implements(interfaces.IHalfCloseableProtocol)

    def connectionMade(self):
        self.sendLine('echo')
        reactor.callLater(2, self.sendLine, 'echo')
        reactor.callLater(7, self.sendLine, 'echo')

    def lineReceived(self, line):
        print 'received: ', line
        self.transport.loseConnection()

    def connectionLost(self, reason):
        print "connection was lost:", str(reason.value)
        #reactor.stop()

    def readConnectionLost(self):
        print "read connection was lost"

    def writeConnectionLost(self):
        print "write connection was lost"


class EchoFactory(ClientFactory):
    protocol = EchoProtocol

    def clientConnectionFailed(self, connector, err):
        print "failed:", err.value
        reactor.stop()

    def clientConnectionLost(self, connector, err):
        print "lost:", err.value
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

