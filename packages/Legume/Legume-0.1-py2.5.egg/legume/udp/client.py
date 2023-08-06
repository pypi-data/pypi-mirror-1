# legume. Copyright 2009 Dale Reidy. All rights reserved.
# See LICENSE for details.

import packets
import netshared
import connection
import logging
from legume.nevent import Event

LOG = logging.getLogger('client')
LOG.setLevel(logging.ERROR)
LOG.addHandler(logging.StreamHandler())

class ClientError(Exception): pass

class Client(netshared.NetworkEndpoint):

    def __init__(self, packetFactory=packets.packetFactory):
        netshared.NetworkEndpoint.__init__(self, packetFactory)
        self.isserver = False
        self._address = None
        self._connection = None
        self._disconnecting = False

        self.OnConnectRequestAccepted = Event()
        self.OnConnectRequestRejected = Event()
        self.OnError = Event()
        self.OnDisconnect = Event()
        self.OnMessage = Event()

    def _Connection_OnMessage(self, sender, message):
        '''Received message'''
        self.OnMessage(self, message)

    def _Connection_OnConnectRequestAccepted(self, sender, event_args):
        '''Connection request was accepted'''
        self._state = self.CONNECTED
        self.OnConnectRequestAccepted(self, event_args)

    def _Connection_OnConnectRequestRejected(self, sender, event_args):
        '''Connection request was rejected'''
        self._state = self.ERRORED
        self._shutdownSocket()
        self.OnConnectRequestRejected(self, event_args)

    def _Connection_OnError(self, sender, error_string):
        self._state = self.ERRORED
        self._shutdownSocket()
        self.OnError(self, error_string)

    def _Connection_OnDisconnect(self, sender, event_args):
        self.disconnect()
        self.OnDisconnect(self, event_args)

    def connect(self, address):
        '''
        Initiate a connection to the server at the specified address.
        address is of the format (host, port) eg:
            ('localhost', 1337)
        Calling this method will put the socket into the CONNECTING state.
        '''
        if self.isActive():
            raise ClientError(
                'Client cannot reconnect in a CONNECTING or CONNECTED state')
        if not netshared.isValidPort(address[1]):
            raise ClientError(
                '%s is not a valid port' % str(address[1]))
        self._socket = self.createSocket()
        self.connectSocket(address)
        self._address = address

        self._connection = connection.Connection(self)

        self._connection.OnConnectRequestAccepted += \
            self._Connection_OnConnectRequestAccepted
        self._connection.OnConnectRequestRejected += \
            self._Connection_OnConnectRequestRejected
        self._connection.OnError += self._Connection_OnError
        self._connection.OnDisconnect += self._Connection_OnDisconnect
        self._connection.OnMessage += self._Connection_OnMessage

        request_packet = packets.packets['ConnectRequest']()
        self._sendReliablePacket(request_packet)
        self._state = self.CONNECTING

    def disconnect(self):
        self._connection.sendPacket(
            self.packetFactory.getByName('Disconnected')())
        self._disconnecting = True

    def isConnected(self):
        return self._state == self.CONNECTED

    def isErrored(self):
        return self._state == self.ERRORED

    def isDisconnected(self):
        return self._state == self.DISCONNECTED

    def _sendPacket(self, packet):
        self._connection.sendPacket(packet)

    def _sendReliablePacket(self, packet):
        self._connection.sendReliablePacket(packet)

    def sendReliablePacket(self, packet):
        if self._state == self.CONNECTED:
            self._sendReliablePacket(packet)
        else:
            raise ClientError, 'Cannot send packet - not connected'

    def sendPacket(self, packet):
        '''
        Send a packet to the server. The packet is added to the output buffer.
        To flush the output buffer call the .update() method.
        packet is an instance of a subclass of packet.BasePacket
        '''
        if self._state == self.CONNECTED:
            self._sendPacket(packet)
        else:
            raise ClientError, 'Cannot send packet - not connected'

    def _disconnect(self):
        '''
        Disconnect this client
        '''
        self._state = self.DISCONNECTED
        self.OnDisconnect(self, None)

    def update(self):
        if self._state in [self.CONNECTING, self.CONNECTED]:
            self._connection.update()

        if self._disconnecting and not self._connection.hasOutgoingPackets():
            self._state = self.DISCONNECTED
            self._shutdownSocket()
            self._disconnecting = False
