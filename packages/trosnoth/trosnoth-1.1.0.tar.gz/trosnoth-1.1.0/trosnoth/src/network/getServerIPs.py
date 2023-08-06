from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from trosnoth.src.networkDefines import *


class ServerIPGetter(DatagramProtocol):
    def __init__(self, multicastPort=multicastPort):
        self.result = {}
        self.port = reactor.listenUDP(0, self)
        self.port.write('Trosnoth:ServerList?', (multicastGroup, multicastPort))
        
    def datagramReceived(self, datagram, address):
        '''This method is called when a datagram is received. It will interpret
        the message, and instruct the networkClient object'''

        # A server tells us that it exists
        if datagram.startswith('Trosnoth:Server:'):
            tcpPort = ntohl(struct.unpack('I', datagram[16:20])[0])
            name = datagram[20:]
            self.result[name]
            self.serverDetails[name] = (address[0], tcpPort)
            
