import time
import sys
sys.path.append('..')
import legume

PORT = 14822

client = legume.udp.Client()
client.connect(('localhost', PORT))

while True:
    client.update()
    time.sleep(0.001)