import time
import buffer
import logging
import netshared
from legume.nevent import Event
import random

LOG = logging.getLogger('connection')
LOG.setLevel(logging.ERROR)
LOG.addHandler(logging.StreamHandler())

class Connection(object):
    def __init__(self, parent):
        self.parent = parent
        self._buffer = buffer.EndpointBuffer(parent.packetFactory)
        self.lastDataRecvdAt = time.time()
        self.lastPacketSentAt = time.time()

        self.OnConnectRequestAccepted = Event()
        self.OnConnectRequestRejected = Event()
        self.OnConnectRequest = Event()
        self.OnError = Event()
        self.OnMessage = Event()
        self.OnDisconnect = Event()

    def sendPacket(self, packet):
        self._buffer.send(packet)
        self.lastPacketSentAt = time.time()

    def sendReliablePacket(self, packet):
        self._buffer.sendReliable(packet)
        self.lastPacketSentAt = time.time()

    def insertRawUDPPacket(self, data):
        self._buffer.insertRawUDPPacket(data)

    def hasOutgoingPackets(self):
        return self._buffer.hasOutgoingPackets()

    def _onSocketData(self, data, addr):
        self.insertRawUDPPacket(data)

    def update(self):
        '''
        This method sends any packets that are in the output buffer and
        reads any packets that have been recieved.
        '''
        try:
            self.parent.doRead(self._onSocketData)
        except netshared.NetworkEndpointError, e:
            self.raiseOnError('Connection reset by peer')
            return

        read_packets = self._buffer.update(
                        self.parent._socket, self.parent._address)

        if len(read_packets) != 0:
            self.lastDataRecvdAt = time.time()

        for packet in read_packets:

            if self.parent.packetFactory.isA(packet, 'ConnectRequestAccepted'):
                self.OnConnectRequestAccepted(self, None)

            elif self.parent.packetFactory.isA(packet, 'ConnectRequestRejected'):
                self.OnConnectRequestRejected(self, None)

            elif self.parent.packetFactory.isA(packet, 'KeepAliveRequest'):
                self.sendPacket(
                    self.parent.packetFactory.getByName('KeepAliveResponse')())

            elif self.parent.packetFactory.isA(packet, 'Disconnected'):
                self.OnDisconnect(self, None)

            elif self.parent.packetFactory.isA(packet, 'PacketAck'):
                self._buffer.removePacketFromOutgoingList(packet.packetToAck.value)

            elif self.parent.packetFactory.isA(packet, 'ConnectRequest'):
                # Unless the connection request is explicitly denied then
                # a connection is made - OnConnectRequest may return None
                # if no event handlers are bound.
                if self.OnConnectRequest(self.parent, packet) is False:
                    response = self.parent.packetFactory.getByName(
                                'ConnectRequestRejected')
                    self.sendReliablePacket(response())
                    self.pendingDisconnect = True
                else:
                    response = self.parent.packetFactory.getByName(
                                'ConnectRequestAccepted')
                    self.sendReliablePacket(response())
            else:
                self.OnMessage(self, packet)

        # KeepAlive stuff:
        if self.parent.isserver:
            # Server sends keep alive requests...
            if (time.time()-self.lastPacketSentAt)>(self.parent.timeout/2):
                self.sendPacket(
                    self.parent.packetFactory.getByName('KeepAliveRequest')())
            # though it will eventually give up...
            if (time.time()-self.lastDataRecvdAt)>(self.parent.timeout):
                self.OnError(self, 'Connection timed out')

        else:
            # ...Client just waits for the connection to timeout
            if (time.time()-self.lastDataRecvdAt)>(self.parent.timeout):
                LOG.info('Connection has timed out')
                self.OnError(self, 'Connection timed out')
