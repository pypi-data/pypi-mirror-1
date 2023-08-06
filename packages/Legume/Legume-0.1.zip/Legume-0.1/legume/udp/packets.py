# legume. Copyright 2009 Dale Reidy. All rights reserved. See LICENSE for details.

import sys
import struct
import string

class PacketError(Exception): pass


BASE_PACKETID_SYSTEM = 11000
BASE_PACKETID_USER = 14000

def isValidIdentifier(identifier):
    return not (' ' in identifier or identifier[0] not in string.ascii_letters)

class PacketValue(object):
    VALID_TYPE_NAMES = ['int', 'string', 'float', 'bool']

    def __init__(self, name, typename, value=None, maxLength=None):
        '''
        Create a new packet type.

        The name parameter must be a valid python class attribute identifier.
        Typename can be one of 'int', 'string', 'float' or 'bool'.
        Value must be of the specified type.
        maxLength is only required for string values.

        '''

        if not isValidIdentifier(name):
            raise PacketError, '%s is not a valid name' % name

        self.name = name
        self.typename = typename
        self._value = value
        self.maxLength = maxLength # only required for string

        if self.typename == 'string' and self.maxLength is None:
            raise PacketError, 'String value requires a maxLength attribute'
        elif self.maxLength is not None and self.maxLength < 1:
            raise PacketError, 'Max length must be None or > 0'
        elif self.typename not in self.VALID_TYPE_NAMES:
            raise PacketError, '%s is not a valid type name' % self.typename
        elif self.name == '':
            raise PacketError('A value name is required')

    def getValue(self):
        return self._value

    def setValue(self, value):
        if self.typename == 'string':
            if len(value) > self.maxLength:
                raise PacketError, 'String value is too long.'
            self._value = value.replace('\0', '')
        else:
            self._value = value

    value = property(getValue, setValue)

    def getFormatString(self):
        '''
        Returns the string necessary for encoding this value using struct.
        '''

        if self.typename == 'int':
            return 'I'
        elif self.typename == 'string':
            return str(self.maxLength) + 's'
        elif self.typename == 'float':
            return 'd'
        elif self.typename == 'bool':
            return 'b'
        else:
            raise PacketError, 'Cant get format string for type "%s"' % self.typename

class BasePacket(object):
    '''
    Data packets must inherit from this base class. A subclass must have a static
    property called PacketTypeID set to a integer value to uniquely identify the packet
    within a single PacketFactory.
    '''

    VERSION = 42000
    HEADER_FORMAT = 'II'
    PacketTypeID = None
    def __init__(self, *values):
        self._packet_type_id = self.PacketTypeID
        if self.PacketTypeID is None:
            raise PacketError('%s does not have a PacketTypeID' % self.__class__.__name__)

        self.valueNames = []
        for value in values:
            self._addValue(value)

    def _addValue(self, value):
        self.valueNames.append(value.name)
        self.__dict__[value.name] = value

    def getHeaderFormat(self):
        '''
        Returns the header format as a struct compatible string.
        '''
        return self.HEADER_FORMAT

    def getHeaderValues(self):
        '''
        Returns a list containing the values used to construct
        the packet header.
        '''
        return [self.VERSION, self._packet_type_id]

    def getDataFormat(self):
        '''
        Returns a struct compatible format string of the packet data
        '''
        format = []
        for valuename in self.valueNames:
            value = self.__dict__[valuename]
            if not isinstance(value, PacketValue):
                raise PacketError(
                    'Overwritten message value! Use msgval.value = xyz')
            format.append(value.getFormatString())
        return ''.join(format)

    def getPacketValues(self):
        '''
        Returns a list containing the header+packet values used
        to construct the packet
        '''
        values = self.getHeaderValues()
        for name in self.valueNames:
            values.append(self.__dict__[name].value)
        return values

    def getPacketFormat(self):
        '''
        Returns a struct compatible format string of the packet
        header and data
        '''
        return self.getHeaderFormat() + self.getDataFormat()

    def getPacketString(self):
        '''
        Returns a string containing the packet header and data. This
        string can be passed to .loadFromString(...).
        '''
        return struct.pack(
            self.getPacketFormat(),
            *self.getPacketValues())

    @staticmethod
    def readHeaderFromByteBuffer(byteBuffer):
        '''
        Read a packet header from an instance of ByteBuffer. This
        method will return a tuple containing the header
        values.
        '''

        return byteBuffer.peekStruct(BasePacket.HEADER_FORMAT)

    def loadFromString(self, packetString):
        '''
        Reconstitute the packet values from the packetString argument.
        '''
        unpackedValues = struct.unpack(
            self.getPacketFormat(),
            packetString)

        if unpackedValues[0] != self.VERSION:
            raise PacketError, 'Version mismatch. Us=%s, Packet=%s' % (
                str(self.VERSION), str(unpackedValues[0]))

        headerValueCount = len(self.getHeaderValues())

        for i, name in enumerate(self.valueNames):
            self.__dict__[name].value = unpackedValues[i+headerValueCount]

    def loadFromByteBuffer(self, byteBuffer):
        '''
        Reconstitute the packet from a ByteBuffer instance
        '''
        packetString = byteBuffer.readBytes(
            struct.calcsize(self.getPacketFormat()))
        self.loadFromString(packetString)


class ConnectRequest(BasePacket):
    '''
    A connection request packet - sent by a client to the server.
    '''
    PacketTypeID = BASE_PACKETID_SYSTEM+1
    def __init__(self):
        BasePacket.__init__(self)

class ConnectRequestRejected(BasePacket):
    '''
    A connection request rejection packet - sent by the server back to
    a client.
    '''
    PacketTypeID = BASE_PACKETID_SYSTEM+2
    def __init__(self):
        BasePacket.__init__(self)

class ConnectRequestAccepted(BasePacket):
    '''
    A connection request accepted packet - sent by the server back to
    a client.
    '''
    PacketTypeID = BASE_PACKETID_SYSTEM+3
    def __init__(self):
        BasePacket.__init__(self)

class KeepAliveRequest(BasePacket):
    '''
    This is sent by the server to keep the connection alive.
    '''
    PacketTypeID = BASE_PACKETID_SYSTEM+4
    def __init__(self):
        BasePacket.__init__(self)

class KeepAliveResponse(BasePacket):
    '''
    A clients response to the receipt of a KeepAliveRequest packet.
    '''
    PacketTypeID = BASE_PACKETID_SYSTEM+5
    def __init__(self):
        BasePacket.__init__(self)

class Disconnected(BasePacket):
    '''
    This packet is sent by either the client or server to indicate to the
    other end of the connection that the link is closed. In cases where
    the connection is severed due to software crash, this packet will
    not be sent, and the socket will eventually disconnect due to a timeout.
    '''
    PacketTypeID = BASE_PACKETID_SYSTEM+6
    def __init__(self):
        BasePacket.__init__(self)

class PacketAck(BasePacket):
    '''
    Sent by either a client or server to acknowledge receipt of an
    in-order or reliable packet.
    '''
    PacketTypeID = BASE_PACKETID_SYSTEM+7
    def __init__(self):
        BasePacket.__init__(self,
            PacketValue('packetToAck', 'int'))


class PacketFactoryItem(object):
    def __init__(self, packet_name, packet_type_id, packet_factory):
        self.packet_name = packet_name
        self.packet_type_id = packet_type_id
        self.packet_factory = packet_factory

class PacketFactory(object):
    def __init__(self):
        self.factories = []
        self.factoriesByName = {}
        self.factoriesById = {}

        self.add(*packets.values())

    def add(self, *packet_classes):
        '''
        Add packet class(es) to the packet factory.
        The parameters to this method must be subclasses of BasePacket.

        A PacketError will be raised if a packet already exists in
        this factory with an identical name or PacketTypeID.
        '''
        for packet_class in packet_classes:
            if packet_class.__name__ in self.factoriesByName:
                raise PacketError, 'Packet already in factory'
            if packet_class.PacketTypeID in self.factoriesById:
                raise PacketError, 'Packet %s has same Id as Packet %s' % (
                    packet_class.__name__,
                    self.factoriesById[packet_class.PacketTypeID].packet_name)
            newFactory = PacketFactoryItem(
                packet_class.__name__,
                packet_class.PacketTypeID,
                packet_class)
            self.factoriesByName[packet_class.__name__] = newFactory
            self.factoriesById[packet_class.PacketTypeID] = newFactory

    def getById(self, id):
        '''
        Obtain a packet class by specifying the packets PacketTypeID.
        If the packet cannot be found a PacketError exception is raised.
        '''
        try:
            return self.factoriesById[id].packet_factory
        except:
            raise PacketError, 'No packet exists with ID %s' % str(id)

    def getByName(self, name):
        '''
        Obtain a packet class by specifying the packets name.
        If the packet cannot be found a PacketError exception is raised.
        '''
        try:
            return self.factoriesByName[name].packet_factory
        except:
            raise PacketError, 'No packet exists with name %s' % str(name)

    def isA(self, packetInstance, packetName):
        '''
        Determine if packetInstance is an instance of the named packet class.

        Example:
        >>> tp = TestPacket1()
        >>> packetFactory.isA(tp, 'TestPacket1')
        True
        '''
        return isinstance(packetInstance, self.getByName(packetName))


packets = {
    'ConnectRequest':ConnectRequest,
    'ConnectRequestRejected':ConnectRequestRejected,
    'ConnectRequestAccepted':ConnectRequestAccepted,
    'KeepAliveRequest':KeepAliveRequest,
    'KeepAliveResponse':KeepAliveResponse,
    'Disconnected':Disconnected,
    'PacketAck':PacketAck
}

packetFactory = PacketFactory()