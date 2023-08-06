import time
import random
import unittest
import legume
from greenbar import GreenBarRunner

# Events to test:

#   - EventName [#times covered]

# Client:
#   - OnConnectRequestAccepted  [#]
#   - OnConnectRequestRejected  [#]
#   - OnError                   [#]
#   - OnDisconnect              [#]
#   - OnMessage                 [#]

# Server:
#   - OnConnectRequest  [####]
#   - OnError           [#]
#   - OnDisconnect      [#]
#   - OnMessage         [#]

HOST = 'localhost'
ITERATIONS = 100

def getRandomPort():
    return random.randint(16000, 50000)


class ExamplePacket(legume.udp.packets.BasePacket):
    PacketTypeID = legume.udp.packets.BASE_PACKETID_USER+1400
    def __init__(self):
        legume.udp.packets.BasePacket.__init__(self,
            legume.udp.packets.PacketValue(
                'message', 'string', 'Hello World!', maxLength=32))


class TestEvents(unittest.TestCase):
    def setUp(self):
        self.packet_factory = legume.udp.packets.PacketFactory()

        self.server = legume.udp.Server(self.packet_factory)
        self.client = legume.udp.Client(self.packet_factory)
        port = getRandomPort()
        self.server.listen((HOST, port))
        self.client.connect((HOST, port))

        self.test_passed = False
        self.peer_address = None


    def update(self):
        if self.server is not None:
            self.server.update()
        if self.client is not None:
            self.client.update()


    def testConnectRequestIsAccepted(self):
        def Server_OnConnectRequest(sender, event_args):
            return True

        def Client_OnConnectRequestAccepted(sender, event_args):
            self.test_passed = True

        self.client.OnConnectRequestAccepted += Client_OnConnectRequestAccepted
        self.server.OnConnectRequest += Server_OnConnectRequest

        for x in xrange(ITERATIONS):
            self.update()

        self.assertTrue(self.test_passed)
        self.assertTrue(self.client.isConnected())


    def testConnectRequestIsRejected(self):
        def Server_OnConnectRequest(sender, event_args):
            return False

        def Client_OnConnectRequestRejected(sender, event_args):
            self.test_passed = True

        self.client.OnConnectRequestRejected += Client_OnConnectRequestRejected
        self.server.OnConnectRequest += Server_OnConnectRequest

        for x in xrange(ITERATIONS):
            self.update()

        self.assertTrue(self.test_passed)
        self.assertFalse(self.client.isConnected())


    def testServerDisconnectsClient(self):
        def Client_OnDisconnect(sender, event_args):
            self.test_passed = True

        def Server_OnConnectRequest(sender, event_args):
            self.peer_address = sender.address

        self.server.OnConnectRequest += Server_OnConnectRequest
        self.client.OnDisconnect += Client_OnDisconnect

        for x in xrange(ITERATIONS):
            self.update()

        self.server.disconnect(self.peer_address)

        for x in xrange(ITERATIONS):
            self.update()

        self.assertTrue(self.test_passed)


    def testClientDisconnectsServer(self):
        def Server_OnConnectRequest(sender, event_args):
            self.peer_address = sender.address
            return True

        def Server_OnDisconnect(sender, event_args):
            self.assertEquals(self.peer_address, sender.address)
            self.test_passed = True

        self.server.OnDisconnect += Server_OnDisconnect
        self.server.OnConnectRequest += Server_OnConnectRequest

        for x in xrange(ITERATIONS):
            self.update()

        self.client.disconnect()

        for x in xrange(ITERATIONS):
            self.update()

        self.assertTrue(self.test_passed)


    def testClientDropsCausingErrorOnServer(self):
        def Server_OnError(sender, event_args):
            self.test_passed = True

        self.client.timeout = 0.25
        self.server.timeout = 0.25

        self.server.OnError += Server_OnError

        for x in xrange(ITERATIONS):
            self.update()

        self.client = None

        for x in xrange(ITERATIONS):
            time.sleep(0.001)
            self.update()

        self.assertTrue(self.test_passed)


    def testServerDropsCausingErrorOnClient(self):
        def Client_OnError(sender, event_args):
            self.test_passed = True

        self.client.timeout = 0.25
        self.server.timeout = 0.25

        self.client.OnError += Client_OnError

        for x in xrange(ITERATIONS):
            self.update()

        self.server = None

        for x in xrange(ITERATIONS):
            time.sleep(0.001)
            self.update()

        self.assertTrue(self.test_passed)


    def testSendMessageToServer(self):
        def Server_OnMessage(sender, packet):
            self.test_passed = True
            self.assertEquals(packet.message.value, "HITHERE")
        self.packet_factory.add(ExamplePacket)

        self.server.OnMessage += Server_OnMessage

        for x in xrange(ITERATIONS):
            self.update()

        example_packet = ExamplePacket()
        example_packet.message.value = "HITHERE"

        self.client.sendReliablePacket(example_packet)

        for x in xrange(ITERATIONS):
            self.update()


    def testSendMessageToClient(self):
        def Client_OnMessage(sender, packet):
            self.test_passed = True
            self.assertEquals(packet.message.value, "HITHERE")
        self.packet_factory.add(ExamplePacket)

        self.client.OnMessage += Client_OnMessage

        for x in xrange(ITERATIONS):
            self.update()

        example_packet = ExamplePacket()
        example_packet.message.value = "HITHERE"

        self.server.sendReliablePacketToAll(example_packet)

        for x in xrange(ITERATIONS):
            self.update()

        self.assertTrue(self.test_passed)

if __name__ == '__main__':
    mytests = unittest.TestLoader().loadTestsFromTestCase(TestEvents)
    GreenBarRunner(verbosity=2).run(mytests)
