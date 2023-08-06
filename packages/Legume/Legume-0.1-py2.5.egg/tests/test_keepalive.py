import sys
sys.path.append('..')
import time
import unittest
import legume
from greenbar import GreenBarRunner


def getRandomPort():
    import random
    return random.randint(16000, 50000)


class TestKeepAlive(unittest.TestCase):
    def setUp(self):
        self.port = getRandomPort()
        self.server = legume.udp.Server()
        self.client = legume.udp.Client()

    def initEndpoints(self):
        self.server.listen(('', self.port))
        self.client.connect(('localhost', self.port))

    def performUpdateLoop(self):
        for i in xrange(60):
            self.server.update()
            self.client.update()
            time.sleep(0.01)

    def testKeepAliveClientWillDisconnect(self):
        '''
        Client will connect to Server but connection will timeout
        and Client will go into an errored state.
        '''
        self.initEndpoints()

        # Mismatched timeout causes client to bail on the connection early.
        self.server.timeout = 1.0
        self.client.timeout = 0.25

        self.performUpdateLoop()
        self.assertTrue(self.client.isErrored())

    def testKeepAliveClientWillStayConnected(self):
        '''
        Client will stay connected to the server
        '''
        self.initEndpoints()

        self.server.timeout = 0.25
        self.client.timeout = 0.25

        self.performUpdateLoop()
        self.assertTrue(self.client.isConnected())



if __name__ == '__main__':
    mytests = unittest.TestLoader().loadTestsFromTestCase(TestKeepAlive)
    GreenBarRunner(verbosity=2).run(mytests)