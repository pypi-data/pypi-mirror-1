#!/usr/bin/python

"""Asynchronous server using Twisted with GNUTLS"""

import sys
import os

from zope.interface import implements

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.error import CannotListenError, ConnectionDone
from twisted.internet import reactor, interfaces

from gnutls.constants import *
from gnutls.crypto import *
from gnutls.errors import *
from gnutls.interfaces.twisted import X509Credentials

class EchoProtocol(LineOnlyReceiver):

    implements(interfaces.IHalfCloseableProtocol)

    def connectionMade(self):
        session = self.transport.socket
        try:
            peer_name = session.peer_certificate.subject
        except AttributeError:
            peer_name = 'Unknown'
        print '\nNew connection from:', peer_name
        print 'Protocol:     ', session.protocol
        print 'KX algorithm: ', session.kx_algorithm
        print 'Cipher:       ', session.cipher
        print 'MAC algorithm:', session.mac_algorithm
        print 'Compression:  ', session.compression
        self.transport.loseWriteConnection()
        reactor.callLater(5, self.transport.loseConnection)

    def lineReceived(self, line):
        if line == 'quit':
            self.transport.loseConnection()
            return
        print "received:", line
        #self.sendLine(line)

    def connectionLost(self, reason):
        #if reason.type != ConnectionDone:
            print "Connection was lost:", str(reason.value)

    def readConnectionLost(self):
        print "read connection was lost"

    def writeConnectionLost(self):
        print "write connection was lost"


class EchoFactory(Factory):
    protocol = EchoProtocol

script_path = os.path.realpath(os.path.dirname(sys.argv[0]))
certs_path = os.path.join(script_path, 'certs')

cert = X509Certificate(open(certs_path + '/valid.crt').read())
key = X509PrivateKey(open(certs_path + '/valid.key').read())
ca = X509Certificate(open(certs_path + '/ca.pem').read())
crl = X509CRL(open(certs_path + '/crl.pem').read())
cred = X509Credentials(cert, key, [ca], [crl])
cred.verify_peer = True
cred.session_params.compressions = (COMP_LZO, COMP_DEFLATE, COMP_NULL)

reactor.listenTLS(10000, EchoFactory(), cred)
reactor.run()

