# legume. Copyright 2009 Dale Reidy. All rights reserved. See LICENSE for details.

import logging
import netshared
import packets
import serverpeer
import time
from legume.nevent import Event

LOG = logging.getLogger('server')
LOG.setLevel(logging.ERROR)
LOG.addHandler(logging.StreamHandler())

class Server(netshared.NetworkEndpoint):
    '''
    A server. To allow network clients to communicate with this class
    call listen() with a network address then periodically call update()
    to ensure data is kept flowing and connects/disconnects are handled.
    '''

    def __init__(self, packetFactory=packets.packetFactory):
        netshared.NetworkEndpoint.__init__(self, packetFactory)
        self._state = self.DISCONNECTED
        self._peers = {}
        self._dead_peers = [] # List of peers (by address) to be removed

        self.OnConnectRequest = Event()
        self.OnDisconnect = Event()
        self.OnError = Event()
        self.OnMessage = Event()

    def listen(self, address):
        '''
        Begin listening for incoming connections.
        address is a tuple of the format (hostname, port)
        This method change the class state to LISTENING.
        '''
        if self.isActive():
            raise netshared.ServerError(
                'Server cannot listen whilst in a LISTENING state')
        self.createSocket()
        self.bindSocket(address)
        self._address = address
        self._state = self.LISTENING

    def _onSocketData(self, data, addr):
        LOG.debug(
            'Got data %s bytes in length from %s' %
            (str(len(data)), str(addr)))

        if not addr in self._peers:
            new_peer = serverpeer.Peer(self, addr, self.packetFactory)
            self._peers[addr] = new_peer

            new_peer.OnDisconnect += self._Peer_OnDisconnect
            new_peer.OnError += self._Peer_OnError
            new_peer.OnMessage += self._Peer_OnMessage
            new_peer.OnConnectRequest += self._Peer_OnConnectRequest

        self._peers[addr].insertRawUDPPacket(data)

    def _Peer_OnConnectRequest(self, peer, event_args):
        return self.OnConnectRequest(peer, event_args)

    def _Peer_OnError(self, peer, error_string):
        self.OnError(peer, error_string)

    def _Peer_OnMessage(self, peer, message_packet):
        self.OnMessage(peer, message_packet)

    def _Peer_OnDisconnect(self, peer, event_args):
        self.OnDisconnect(peer, None)

    def update(self):
        '''
        Pumps buffers and dispatches events. Call regularly to ensure
        buffers do not overfill or connections time-out.
        '''
        self.doRead(self._onSocketData)

        dead_peers = []

        for peer in self._peers.itervalues():
            peer.update()

            if peer.pendingDisconnect and not peer.hasPacketsToSend():
                dead_peers.append(peer.address)

        for dead_peer in dead_peers:
            self._removePeer(dead_peer)


    def _removePeer(self, peer_address):
        LOG.debug('Peer %s has been removed from peers' % str(peer_address))
        peer = self._peers[peer_address]
        del self._peers[peer_address]


    def getPeerByAddress(self, peer_address):
        return self._peers[peer_address]


    def disconnect(self, peer_address):
        '''
        Disconnect a peer by specifying their address.
        Equivalent to:
        >>> server.getPeerByAddress(peer_address).disconnect()
        '''
        self.getPeerByAddress(peer_address).disconnect()


    def sendPacketToAll(self, packet):
        for peer in self._peers.itervalues():
            peer.sendPacket(packet)


    def sendReliablePacketToAll(self, packet):
        for peer in self._peers.itervalues():
            peer.sendReliablePacket(packet)
