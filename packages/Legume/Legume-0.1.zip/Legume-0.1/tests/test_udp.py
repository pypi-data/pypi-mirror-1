# legume. Copyright 2009 Dale Reidy. All rights reserved. See LICENSE for details.

import sys
sys.path.append('..')
import unittest
import legume
import random

def getRandomPort():
    return random.randint(16000, 50000)

PORT = random.randint(16000, 26000)

# ========

class TestInstantiation(unittest.TestCase):
    def testClientCtor(self):
        c = legume.udp.Client()

    def testServerCtor(self):
        s = legume.udp.Server()

class TestConnectionSetup(unittest.TestCase):
    def testClientConnect(self):
        c = legume.udp.Client()
        c.connect(('localhost', getRandomPort()))

    def testServerListen(self):
        s = legume.udp.Server()
        s.listen(('', getRandomPort()))

class TestUpdate(unittest.TestCase):
    def testClientUpdate(Self):
        c = legume.udp.Client()
        c.update()

    def testServerUpdate(self):
        s = legume.udp.Server()
        s.update()

# ========

class TestClientState(unittest.TestCase):

    def setUp(self):
        self.client = legume.udp.Client()

    def testClientClosedStated(self):
        self.assertEquals(self.client.state, self.client.DISCONNECTED)

    def testClientBadPortException(self):
        def willfail():
            self.client.connect(('localhost', 'notaservice')) # Errored port number
        self.assertRaises(legume.udp.client.ClientError, willfail)

    def testClientConnectingState(self):
        self.client.connect(('localhost', getRandomPort()))
        self.assertEquals(self.client.state, self.client.CONNECTING)

    def testConnectReAttemptFails(self):
        def willfail():
            self.client.connect(('localhost', getRandomPort()))
            self.client.connect(('localhost', getRandomPort()))
        self.assertRaises(legume.udp.client.ClientError, willfail)

# ========

class TestServerState(unittest.TestCase):

    def setUp(self):
        self.server = legume.udp.Server()

    def testServerClosedState(self):
        self.assertEquals(self.server.state, self.server.DISCONNECTED)

    def testServerBadPortException(self):
        def willfail():
            self.server.listen(('', 'notaservice')) # Errored port number
        self.assertRaises(TypeError, willfail)

    def testServerListeningState(self):
        self.server.listen(('', getRandomPort()))
        self.assertEquals(self.server.state, self.server.LISTENING)

# ========

PACKET_HEADER_FORMAT = legume.udp.packets.BasePacket.HEADER_FORMAT

class TestPacket(unittest.TestCase):

    def testConnectRequestPacketFormat(self):
        self.assertEquals(
            legume.udp.packets.ConnectRequest().getHeaderFormat(),
            PACKET_HEADER_FORMAT)

    def testConnectRequestPacketValues(self):
        values = legume.udp.packets.ConnectRequest().getPacketValues()
        self.assertEquals(
            values,
            [legume.udp.packets.BasePacket.VERSION,
            legume.udp.packets.ConnectRequest.PacketTypeID])


class TestPacket1(legume.udp.packets.BasePacket):
    PacketTypeID = legume.udp.packets.BASE_PACKETID_USER+1
    def __init__(self):
        legume.udp.packets.BasePacket.__init__(self,
            legume.udp.packets.PacketValue(
                'message', 'string', 'Hello World!', maxLength=32))

class TestTestPacket1NormalUsage(unittest.TestCase):

    def setUp(self):
        self.tp = TestPacket1()

    def testTestPacket1_1(self):
        self.assertEquals(
            self.tp.getPacketValues(),
            [legume.udp.packets.BasePacket.VERSION,
            TestPacket1.PacketTypeID, 'Hello World!'])

    def testTestPacket1Value(self):
        self.assertEquals(
            self.tp.message.value, 'Hello World!')

    def testTestPacket1ValueType(self):
        self.assertEquals(
            self.tp.message.typename, 'string')

    def testTestPacket1ValueFormatString(self):
        self.assertEquals(
            self.tp.message.getFormatString(), '32s')

    def testTestPacket1PacketFormat(self):
        self.assertEquals(
            self.tp.getPacketFormat(),
            PACKET_HEADER_FORMAT + '32s')

    def testGetPacketString(self):
        self.tp.getPacketString()

    def testLongNameRaisesException(self):
        def setLongName():
            self.tp.message.value = "ThisMessageIsLongerThan32Characters."

        self.assertRaises(
            legume.udp.packets.PacketError,
            setLongName)

    def testLoadString(self):
        st = self.tp.getPacketString()
        tp2 = TestPacket1()
        tp2.message.value = "blahblahblah" # Scrub the default packet content
        tp2.loadFromString(st)
        self.assertEquals(tp2.message.value, self.tp.message.value)

# ========

# Tests connection of clients to server

class TestClientConnectionToServer(unittest.TestCase):
    def testRunSingleClient(self):
        PORT = getRandomPort()
        c = legume.udp.Client()
        s = legume.udp.Server()

        s.listen(('', PORT))
        c.connect(('localhost', PORT))

        for i in xrange(100):
            c.update()
            s.update()

        self.assertTrue(c.isConnected())

    def testRunTwoClients(self):
        PORT = getRandomPort()
        c1 = legume.udp.Client()
        c2 = legume.udp.Client()
        s = legume.udp.Server()

        s.listen(('', PORT))
        c1.connect(('localhost', PORT))
        c2.connect(('localhost', PORT))

        for i in xrange(100):
            c1.update()
            c2.update()
            s.update()

        self.assertTrue(c1.isConnected())
        self.assertTrue(c2.isConnected())


# ========

# Test connection request accept/reject mechanism

class TestConnectRequest(unittest.TestCase):
    def setUp(self):
        self.serverPort = getRandomPort()
        self.server = legume.udp.Server()
        self.client = legume.udp.Client()

    def connectEndpoints(self):
        self.server.listen(('', self.serverPort))
        self.client.connect(('localhost', self.serverPort))

    def performUpdateLoop(self):
        self.connectEndpoints()

        i = 0
        while i < 100:
            self.server.update()
            self.client.update()
            i += 1

    def testServerDoesNotAcceptConnection(self):
        '''
        The server should not accept the connection and the clients
        state at the end of the update loop should be ERRORED.
        '''
        def rejectConnection(endpoint, packet):
            print('Rejecting connection.')
            return False

        self.server.OnConnectRequest = rejectConnection
        self.performUpdateLoop()
        self.assertTrue(self.client.isErrored())

    def testServerShouldAcceptConnection(self):
        '''
        The server should accept the clients connection request.
        At the end of this update loop the clients status should be
        CONNECTED.
        '''
        def acceptConnection(endpoint, packet):
            print('Accepting connection.')
            return True

        self.server.OnConnectRequest = acceptConnection
        self.performUpdateLoop()
        self.assertTrue(self.client.isConnected())


class TestGracefulDisconnect(unittest.TestCase):
    '''
    Server should issue a disconnect packet to the client causing
    both ends of the connection to close gracefully.
    '''
    def setUp(self):
        self.serverPort = getRandomPort()
        self.server = legume.udp.Server()
        self.client = legume.udp.Client()
        self.got_disconnect_message = False

    def connectEndpoints(self):
        self.server.listen(('', self.serverPort))
        self.client.connect(('localhost', self.serverPort))

    def performUpdateLoop(self):
        self.peer_address = None

        def Server_OnConnectRequest(endpoint, packet):
            self.peer_address = endpoint.address
            return True

        def Client_OnDisconnect(sender, event_args):
            self.got_disconnect_message = True

        self.server.OnConnectRequest += Server_OnConnectRequest
        self.client.OnDisconnect += Client_OnDisconnect

        i = 0
        while i < 200:
            self.server.update()
            self.client.update()
            i += 1

            if i == 50:
                self.server.disconnect(self.peer_address)

    def testServerDisconnectsClient(self):
        self.connectEndpoints()
        self.performUpdateLoop()
        self.assertTrue(self.client.isDisconnected())
        self.assertTrue(self.got_disconnect_message)


# ========

class MessagePacket(legume.udp.packets.BasePacket):
    PacketTypeID = legume.udp.packets.BASE_PACKETID_USER+3
    def __init__(self):
        legume.udp.packets.BasePacket.__init__(self,
            legume.udp.packets.PacketValue(
                'message', 'string', 'Hello World!', maxLength=32))

class TestServerToClientMessage(unittest.TestCase):
    def setUp(self):
        self.pf = legume.udp.packets.PacketFactory()
        self.pf.add(MessagePacket)
        self.serverPort = getRandomPort()
        self.server = legume.udp.Server(self.pf)
        self.client = legume.udp.Client(self.pf)
        self.peer_address = None
        self.message_to_send = "WHY HELLO THERE!"
        self.received_message = None

    def Server_OnConnectRequest(self, peer, packet):
        print('Got connection request')
        self.peer_address = peer.address
        return True

    def Client_OnMessage(self, sender, message):
        if self.received_message is not None:
            raise Exception, 'Tear in the fabric of space and time!'
        self.received_message = message.message.value
        print('Got message: %s' % self.received_message)


    def connectEndpoints(self):
        self.server.listen(('', self.serverPort))
        self.client.connect(('localhost', self.serverPort))

        self.server.OnConnectRequest = self.Server_OnConnectRequest
        self.client.OnMessage = self.Client_OnMessage

    def performUpdateLoop(self):

        sent_packet = False

        i = 0
        while i < 200:

            if (not sent_packet) and (self.peer_address is not None):
                p = MessagePacket()
                p.message.value = self.message_to_send
                self.server.getPeerByAddress(self.peer_address).sendPacket(p)
                sent_packet = True
                print('Sent message from Server to Client')

            self.server.update()
            self.client.update()

            i += 1

    def testMessagePass(self):
        print('Start of testMessagePass')
        self.connectEndpoints()
        self.performUpdateLoop()
        self.assertEquals(self.message_to_send, self.received_message)

# ========

# Test transmission of non-reliable messages from Client to Server
class TestClientToServerMessage(unittest.TestCase):
    pass

# ========

# TODO: Test transmission of in-order messages

# ========

# TODO: Test transmission of reliable messages

# ========

class TestPacket2(legume.udp.packets.BasePacket):
    PacketTypeID = legume.udp.packets.BASE_PACKETID_USER+2
    def __init__(self):
        legume.udp.packets.BasePacket.__init__(self)
        self.addValue('message', 'string', 'Hello World!', maxLength=32)

class TestPacket2SameID(legume.udp.packets.BasePacket):
    PacketTypeID = legume.udp.packets.BASE_PACKETID_USER+2
    def __init__(self):
        legume.udp.packets.BasePacket.__init__(self)
        self.addValue('message', 'string', 'Hello World!', maxLength=32)

class TestPacketFactory(unittest.TestCase):
    def setUp(self):
        self.pf = legume.udp.packets.PacketFactory()

    def testPacketFactoryHasBasePacketsByDefault(self):
        for pname, pclass in legume.udp.packets.packets.iteritems():
            self.assertEquals(self.pf.getByName(pname), pclass)

    def testPacketFactoryAddTestPacket2(self):
        self.pf.add(TestPacket2)
        self.assertEquals(self.pf.getByName('TestPacket2'), TestPacket2)

    def testPacketFactoryCantShareIDs(self):
        def willfail():
            self.pf.add(TestPacket2)
            self.pf.add(TestPacket2SameID)
        self.assertRaises(legume.udp.packets.PacketError, willfail)

    def testPacketFactoryCanAddMultiplePackets(self):
        self.pf.add(TestPacket1)
        self.pf.add(TestPacket2)

    def testPacketFactoryCantAddPacketTwice(self):
        def willfail():
            self.pf.add(TestPacket2)
            self.pf.add(TestPacket2)
        self.assertRaises(legume.udp.packets.PacketError, willfail)

    def testPacketFactoryNotJustReturningRubbish(self):
        self.pf.add(TestPacket2)
        def willfail():
            self.pf.getByName('ThisPacketIsMakeBelieve')
        self.assertRaises(legume.udp.packets.PacketError, willfail)

    def testPacketFactoryGetById(self):
        self.pf.add(TestPacket2)
        self.assertEquals(
            self.pf.getById(TestPacket2.PacketTypeID).PacketTypeID,
            TestPacket2.PacketTypeID)

    def testPacketFactoryGetByIdBadId(self):
        def willfail():
            self.pf.getById(423984723)
        self.assertRaises(legume.udp.packets.PacketError, willfail)

    def testGetBuiltinPacketById(self):
        self.assertEquals(
            legume.udp.packets.ConnectRequest,
            self.pf.getById(legume.udp.packets.ConnectRequest.PacketTypeID))

# ========

if __name__ == '__main__':
    from greenbar import GreenBarRunner
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    GreenBarRunner(verbosity=2).run(suite)