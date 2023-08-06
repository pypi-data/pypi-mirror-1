# legume. Copyright 2009 Dale Reidy. All rights reserved. See LICENSE for details.

'''
A pretty basic test of a single client connecting to the server.
'''

import legume.udp as legume
import time

PORT = 8011
c = legume.Client()
s = legume.Server()

c.connect(('localhost', PORT))
s.listen(('', PORT))

class ExampleMessage1(legume.packets.BasePacket):
    PacketTypeID = 30001
    def __init__(self):
        legume.packets.BasePacket.__init__(self,
            legume.packets.PacketValue(
                'message', 'string', value=None, maxLength=64))

legume.packets.packetFactory.add(ExampleMessage1)

def gotMessage1(peer_endpoint, packet):
    print 'Message="%s"' % packet.message.value

    response = ExampleMessage1()
    response.message.value = "Server says hello!"
    peer_endpoint.sendPacket(response)

s.OnRecv_ExampleMessage1 = gotMessage1

i = 0
j = 0

while True:
    c.update()
    s.update()
    i += 1
    time.sleep(0.01)

    em1 = ExampleMessage1()
    em1.message.value = 'Hello this is a test message'

    j += 1
    if j == 4:
        j = 0
        if c.isConnected():
            c.sendPacket(em1)
            print 'Sent packet'