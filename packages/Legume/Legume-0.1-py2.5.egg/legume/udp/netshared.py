# legume. Copyright 2009 Dale Reidy. All rights reserved. See LICENSE for details.

import logging
import socket

import errno

LOG = logging.getLogger('netshared')
LOG.setLevel(logging.ERROR)
LOG.addHandler(logging.StreamHandler())

DEFAULT_TIMEOUT = float(10) # default timeout in seconds

class NetworkEndpointError(Exception): pass
class ServerError(Exception): pass

def isValidPort(port):
    '''
    Returns True if the port parameter is within the
    range 1...65535.
    '''
    return port in xrange(1, 65535)

class NetworkEndpoint(object):
    DISCONNECTED = 100
    ERRORED = 101
    LISTENING = 102
    CONNECTING = 103
    CONNECTED = 104

    MTU = 1400

    def __init__(self, packetFactory):
        self._state = self.DISCONNECTED
        self._socket = None
        self.packetFactory = packetFactory
        self.timeout = DEFAULT_TIMEOUT

    def getSocket(self):
        return self._socket
    socket = property(getSocket)

    def createSocket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setblocking(0)
        return self.socket

    def _shutdownSocket(self):
        LOG.info('_shutdownSocket called for %s' % str(self))
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

    def connectSocket(self, addr):
        self._socket.connect(addr)

    def bindSocket(self, addr):
        self._socket.bind(addr)

    def isActive(self):
        return self._state in [
            self.LISTENING, self.CONNECTING, self.CONNECTED]

    def doRead(self, callback):
        if self._state in [self.LISTENING, self.CONNECTED, self.CONNECTING]:
            if self.socket:
                try:
                    while True:
                        data, addr = self.socket.recvfrom(self.MTU, 0)
                        callback(data, addr)
                except socket.error, e:
                    try:
                        errornum = e[0]

                        if errornum not in [errno.EWOULDBLOCK, errno.ECONNRESET]:
                            LOG.debug('Socket error: %s' % str(e))
                            raise
                    except:
                        # Pish.
                        LOG.debug('Socket error: %s' % str(e))
                        raise
            else:
                raise NetworkEndpointError, 'Endpoint is not active'

    def getState(self):
        return self._state
    state = property(getState)
