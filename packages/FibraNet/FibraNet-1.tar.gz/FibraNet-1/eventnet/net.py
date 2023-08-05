import struct
import cStringIO
import gherkin as encoder
from twisted.internet import protocol, reactor
import driver

class StringQueue(object):
    def __init__(self):
        self.l_buffer = []
        self.s_buffer = ""

    def write(self, data):
        self.l_buffer.append(data)

    def read(self, count=None):
        if count > len(self.s_buffer) or count==None:
            self.build_s_buffer()
        result = self.s_buffer[:count]
        self.s_buffer = self.s_buffer[count:]
        return result

    def build_s_buffer(self):
        new_string = "".join(self.l_buffer)
        self.s_buffer = "".join((self.s_buffer, new_string))
        self.l_buffer = []

    def __len__(self):
        self.build_s_buffer()
        return len(self.s_buffer)

def message_unpacker(data):
    while True:
        if len(data) >= 4:
            size = struct.unpack("!l", data.read(4))[0]
            while len(data) < size:
                yield None
            message = data.read(size)
            yield message
        else:
            yield None

def pack_message(data):
    size = struct.pack("!l", len(data))
    return "".join((size, data))

class MessageProtocol(protocol.Protocol):
    def __init__(self, *args, **kw):
        self.buffer = StringQueue()
        self.message_unpacker = message_unpacker(self.buffer)

    def connectionMade(self):
        if self.factory.handleNewConnection:
            self.factory.handleNewConnection(self)

    def connectionLost(self, reason):
        if self.factory.handleCloseConnection:
            self.factory.handleCloseConnection(self, reason)

    def post(self, name, **kw):
        data = pack_message(encoder.dumps((name, kw)))
        self.transport.write(data)

    def flush(self):
        reactor.iterate()

    def dataReceived(self, data):
        self.buffer.write(data)
        for message in self.message_unpacker:
            if message is not None:
                name, kw = encoder.loads(message)
                kw['_conn'] = self
                kw['reply'] = self.post
                driver.post(name, **kw)
            else: break


class ClientFactory(protocol.ReconnectingClientFactory):
    def __init__(self, onConnect,onClose):
        self.handleNewConnection = onConnect
        self.handleCloseConnection = onClose
        self.maxDelay = 10

    def buildProtocol(self, addr):
        self.resetDelay()
        p = MessageProtocol()
        p.factory = self
        return p


class ServerFactory(protocol.ServerFactory):
    def __init__(self, onConnect,onClose):
        self.handleNewConnection = onConnect
        self.handleCloseConnection = onClose

    def buildProtocol(self, addr):
        p = MessageProtocol()
        p.factory = self
        return p


def listen(port, onConnect, onClose):
    """
    Listen on a port.
    Calls onConnect (with connection as argument) when a new connection occurs.
    Calls onClose (with connection and reason as arguments) when a connection is closed.
    """
    reactor.listenTCP(port, ServerFactory(onConnect, onClose))

def connect(address, port,onConnect, onClose):
    """
    Connects to an address and port.
    Calls onConnect (with connection as argument) when a new connection occurs.
    Calls onClose (with connection and reason as arguments) when the connection is closed.
    """
    reactor.connectTCP(address, port, ClientFactory(onConnect, onClose))

poll = reactor.iterate

def poll_iterator():
    """
    An iterator which polls the network stuff as it is iterated.
    """
    while True:
        yield poll()

if __name__ == "__main__":
    pass
