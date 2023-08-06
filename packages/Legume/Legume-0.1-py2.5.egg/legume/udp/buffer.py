# legume. Copyright 2009 Dale Reidy. All rights reserved.
# See LICENSE for details.

'''
The job of the buffer is to manage the flow of messages in and out through
the socket.

It appends a message number to any packets due to be sent which is read
by the buffer instance at the other end of the connection for the purposes
of managing in-order and reliable packet tranmission and acknowledgement.
'''
import time
import struct
import logging
import random

from legume.udp import packets

# Simulated connection loss (%)
CONNECTION_LOSS = 0


LOG = logging.getLogger('buffer')
LOG.setLevel(logging.ERROR)
LOG.addHandler(logging.StreamHandler())

class BufferError(Exception): pass

class BufferedOutgoingPacket(object):
    def __init__(self, packetId, packetString, requireAck):
        self.packetId = packetId
        self.packetString = packetString
        self.requireAck = requireAck

    def getLength(self):
        return len(self.packetString)
    length = property(getLength)


class ByteBuffer(object):
    '''
    Provides a simplified method of reading struct packed data from
    a string buffer.

    readBytes and readStruct remove the read data from the string buffer.
    '''
    def __init__(self, bytes):
        self.bytes = bytes

    def readBytes(self, numBytes):
        result = self.bytes[:numBytes]
        self.bytes = self.bytes[numBytes:]
        return result

    def peekBytes(self, numBytes):
        return self.bytes[:numBytes]

    def pushBytes(self, bytes):
        self.bytes += bytes

    def readStruct(self, structFormat):
        structSize = struct.calcsize(structFormat)
        structBytes = self.readBytes(structSize)
        return struct.unpack(structFormat, structBytes)

    def peekStruct(self, structFormat):
        structSize = struct.calcsize(structFormat)
        structBytes = self.peekBytes(structSize)
        return struct.unpack(structFormat, structBytes)

    def isEmpty(self):
        return len(self.bytes) == 0


class EndpointBuffer(object):
    '''
    A two-way buffer for reading and writing UDP packets.

    An MTU of 1400 bytes is set for the maximum payload of a UDP packet
    that can be sent by the buffer. Currently a message cannot span over
    multiple UDP packets and a PacketError will be raised.
    '''

    MTU = 1400
    PACKETBUFFER_HEADER = 'IIII'
    MAX_RECENT_PACKET_LIST_SIZE = 1000

    def __init__(self, packetFactory):
        self.packetFactory = packetFactory

        # Packet instances to be processed go in here
        self.incomingPacketList = []

        # Packet strings to be sent go in here
        self.outgoing = []

        # In-order packet instances that have arrived early
        self.inOrderHeldPacketList = []

        self.incomingInOrderSequenceNumber = 0
        self.outgoingInOrderSequenceNumber = 1

        self.outgoingPacketID = 0

        self.recentPacketIDs = []


    def removePacketFromOutgoingList(self, packetId):
        for p in self.outgoing:
            if p.packetId == packetId:
                self.outgoing.remove(p)
                return
        raise BufferError, 'Got ACK for packet that was never sent. packetid=%s' % (
            packetId)


    def truncateRecentPacketList(self):
        '''
        Ensures that the recent_packet_ids list length is kept below
        MAX_RECENT_PACKET_LIST_SIZE. This method is called as part of this class'
        update method.
        '''
        if len(self.recentPacketIDs) > self.MAX_RECENT_PACKET_LIST_SIZE:
            self.recentPacketIDs = \
                self.recentPacketIDs[-self.MAX_RECENT_PACKET_LIST_SIZE:]


    def _insertPacket(self, packet):
        self.incomingPacketList.append(packet)
        self.recentPacketIDs.append(packet.packetId)
        if packet.isInOrder:
            self.incomingInOrderSequenceNumber = packet.seqNum

    def _holdPacket(self, packet):
        self.inOrderHeldPacketList.append(packet)
        self.recentPacketIDs.append(packet.packetId)

    def insertRawUDPPacket(self, udpData):
        '''
        Pass raw udp packet data to this method.
        Returns the number of packets parsed and inserted into
        the .incoming list.
        '''
        packets = self.parseRawUDPPacket(udpData)

        for packet in packets:
            if not packet.packetId in self.recentPacketIDs:
                if packet.isInOrder:
                    if self._canReadInOrderPacket(seqNum):
                        self._insertPacket(packet)
                    else:
                        self._holdPacket(packet)
                else:
                    self._insertPacket(packet)

        return len(packets)

    def _canReadInOrderPacket(self, sequenceNumber):
        '''
        Can the in-order packet with the specified sequence number be
        insert into the .incoming list for processing?
        '''
        return self.incomingInOrderSequenceNumber == (sequenceNumber+1)

    def parseRawUDPPacket(self, udpData):
        '''
        Parse a raw udp packet and return a list of packetStrings
        that were parsed.
        '''

        udpDataBB = ByteBuffer(udpData)
        parsedPackets = []

        # While more udpData to read.
        while not udpDataBB.isEmpty():
            # - Read packet ID bytes.
            # - Read reliable transfer byte.
            # - Read in-order sequence number bytes.
            # - Read packet header bytes.
            packetId, seqNum, inOrderFlag, reliableFlag = \
                udpDataBB.readStruct(self.PACKETBUFFER_HEADER)

            # - Read packet type ID
            packetTypeID = packets.BasePacket.readHeaderFromByteBuffer(
                udpDataBB)[1]

            packetClass = self.packetFactory.getById(packetTypeID)

            packet = packetClass()
            # - Read packet data bytes.
            packet.loadFromByteBuffer(udpDataBB)

            # - These flags are for consumption by .update()
            packet.isReliable = reliableFlag
            packet.isInOrder = inOrderFlag
            packet.seqNum = seqNum
            packet.packetId = packetId

            parsedPackets.append(packet)

        return parsedPackets

    def update(self, sock, address):
        '''
        Update this buffer by sending any packets in the output lists
        and read any packets which have been insert into the inputBuffer
        via the insertRawUDPPacket call.

        Returns a list of packet instances of packets that were read.
        '''
        read_packets = self._doRead()
        self.truncateRecentPacketList()
        self._doWrite(sock, address)

        return read_packets


    def _doRead(self):
        unhold = []
        for heldpacket in self.inOrderHeldPacketList:
            if self._canReadInOrderPacket(heldpacket.seqNum):
                unhold.append(heldpacket)
                self.incomingInOrderSequenceNumber = packet.seqNum
                self.incomingPacketList.append(heldpacket)
        for unheldpacket in unhold:
            self.inOrderHeldPacketList.remove(unheldpacket)

        for packet in self.incomingPacketList:
            if packet.isInOrder or packet.isReliable:
                #sendack()
                ack_packet = packets.PacketAck()
                ack_packet.packetToAck.value = packet.packetId
                self.send(ack_packet)


        readPackets = self.incomingPacketList
        self.incomingPacketList = []

        return readPackets


    def _doWrite(self, sock, address):
        #while len(self.outgoing) != 0:
        udpPacket = self._createOutgoingUDPDatagram()
        if udpPacket != "":
            if random.randint(1, 100) > CONNECTION_LOSS:
                bytes_sent = sock.sendto(udpPacket, 0, address)
            else:
                pass # Simulated lost packet

            LOG.info('Sent UDP packet %d bytes in length' % len(udpPacket))


    def _createOutgoingUDPDatagram(self):
        udpPacketSize = 0
        udpPacketString = ""

        sent_packets = []

        LOG.debug('outgoing contains %d items' % len(self.outgoing))

        for packet in self.outgoing:
            if udpPacketSize + packet.length <= self.MTU:
                LOG.debug('Added data packet into UDP packet')
                udpPacketSize += packet.length
                udpPacketString += packet.packetString
                sent_packets.append(packet)
            else:
                LOG.debug(
                    'Data packet too fat, maybe he\'ll get on the next bus')

        for sent_packet in sent_packets:
            # Packets that require an ack are only removed
            # from the outgoing list if an ack is received.
            if not sent_packet.requireAck:
                LOG.debug('Packet doesnt require ack - removing')
                self.outgoing.remove(sent_packet)
            else:
                LOG.debug('Packet requires ack - waiting for response')

        return udpPacketString


    def _getNewOutgoingPacketNumber(self):
        '''
        Returns a packet ID for the next outgoing packet. The
        outgoing_packet_id attribute contains the ID returned
        by the last call to this method.
        '''
        self.outgoingPacketID += 1
        return self.outgoingPacketID


    def _getNewOutgoingInOrderSequenceNumber(self):
        self.outgoingInOrderSequenceNumber += 1
        return self.outgoingInOrderSequenceNumber


    def _getNewPacketBufferHeader(
        self, packetId, seqNum, inOrderFlag, reliableFlag):
        return struct.pack(
            self.PACKETBUFFER_HEADER,
            packetId, seqNum, inOrderFlag, reliableFlag)


    def _addPacketStringToOutputList(self, packetId, packetString, requireAck=False):
        if len(packetString) > self.MTU:
            raise BufferError, 'Packet is too large. size=%s, mtu=%s' % (
                len(packetString), self.MTU)
        else:
            self.outgoing.append(
                BufferedOutgoingPacket(packetId, packetString, requireAck))


    def send(self, packet, inOrder=False, reliable=False):
        '''
        Send a packet and specify any options for the send method used.
        A packet sent inOrder is implicitly sent as reliable.
        packet is an instance of a subclass of packets.BasePacket.
        '''
        packetId = self._getNewOutgoingPacketNumber()
        if inOrder:
            inOrderSequenceNumber = self._getNewOutgoingInOrderSequenceNumber()
        else:
            inOrderSequenceNumber = 0
        inOrderFlag = int(inOrder)
        reliableFlag = int(reliable)

        packetBufferHeader = self._getNewPacketBufferHeader(
            packetId, inOrderSequenceNumber, inOrderFlag, reliableFlag)

        packetString = packet.getPacketString()

        self._addPacketStringToOutputList(
            packetId,
            packetBufferHeader+packetString,
            inOrder or reliable)

        LOG.info('Added %d byte packet in outgoing buffer' %
            (len(packetBufferHeader)+len(packetString)))


    def sendNormal(self, packet):
        '''
        Send a packet that may arrive out of order or be lost.
        packet is an instance of a subclass of packets.BasePacket
        '''
        self.send(packet)

    def sendReliable(self, packet):
        '''
        Send a packet that is guaranteed to be delivered.
        packet is an instance of a subclass of packets.BasePacket
        '''
        self.send(packet, False, True)

    def sendInOrder(self, packet):
        '''
        Send a packet in the in-order channel. Any packets sent in-order will
        arrive in the order they were sent.
        packet is an instance of a subclass of packets.BasePacket
        '''
        self.send(packet, True)

    def hasOutgoingPackets(self):
        '''
        Returns whether this buffer has any packets waiting to be sent.
        '''
        return len(self.outgoing) > 0
