"""

The nanotubes module implements asynchronous socket handling, and provides
protocol classes which simplify event passing over sockets.

"""

__author__ = "simonwittber@gmail.com"

import socket
import select
import struct

import gherkin as encoder

from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, ENOTCONN, ESHUTDOWN, EINTR, EISCONN


#---------------------------------------------------------------------#
#Utility classes

class StringQueue(object):
    """
    A simple character buffer which is used for queing network bytes.
    """
    def __init__(self):
        self.l_buffer = []
        self.s_buffer = ""

    def write(self, data):
        """
        Append's data to the buffer.
        """
        self.l_buffer.append(data)

    def read(self, count=None):
        """
        Returns and removes a number of bytes from the buffer. If count is
        None, all bytes are returned.
        """
        result = self.peek(count)
        self.discard(count)
        return result
    
    def discard(self, count):
        """
        Removes a number of bytes from the buffer.
        """
        self.s_buffer = self.s_buffer[count:]
            
    def peek(self, count=None):
        """
        Returns a number of bytes from the buffer, but does not remove them.
        If count is None, all bytes are returned.
        """
        if count > len(self.s_buffer) or count==None:
            self._build_s_buffer()
        result = self.s_buffer[:count]
        return result

    def _build_s_buffer(self):
        new_string = "".join(self.l_buffer)
        self.s_buffer = "".join((self.s_buffer, new_string))
        self.l_buffer = []

    def __len__(self):
        self._build_s_buffer()
        return len(self.s_buffer)
        

#---------------------------------------------------------------------#
#Base classes

class SocketHandler(object):
    """
    The SocketHandler class registers all socket connections, and uses the
    select function to trigger read, write and close calls on Connection 
    objects.
    """
    sockets = []
    socket_objects = {}
    dead_sockets = []
    
    @classmethod
    def poll(cls):
        """
        The poll method removes dead sockets, and triggers method calls on 
        any Connection objects which are waiting for attention. This method
        needs to be called often.
        """
        for s in cls.dead_sockets:
            cls.sockets.remove(s)
            del cls.socket_objects[s]
        cls.dead_sockets[:] = []
        if cls.sockets:
            readable,writable,exceptional = select.select(cls.sockets,cls.sockets,cls.sockets,0)
            for s in readable:
                cls.socket_objects[s].handle_read()
            for s in writable:
                cls.socket_objects[s].handle_write()
            for s in exceptional:
                cls.socket_objects[s].handle_exception()
            
    @classmethod
    def nanothread(cls):
        """
        The nanothread method returns a generator which can be installed into
        the nanothread scheduler which will iterate the poll method.
        """
        while True:
            cls.poll()
            yield None
    
    @classmethod
    def remove(cls, s):
        """
        Schedules a socket for deletion.
        """
        cls.dead_sockets.append(s)
    
    @classmethod
    def add_socket(cls, s, s_o):
        """
        Adds a socket and socket_object to the handler. The socket_object 
        will have handler methods called when activity occurs on the socket.
        """
        cls.sockets.append(s)
        cls.socket_objects[s] = s_o


class Connection(object):
    """
    The connection object has methods which are called by the socket handler
    which populate protocol buffers, write out data to the socket and calls
    protocol methods to trigger buffer processing.
    """
    def __init__(self, protocol, sock=None):
        self.protocol = protocol
        if sock is None:
            self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.socket.setblocking(0)
        else:
            self.socket = sock
        SocketHandler.add_socket(self.socket, self)
        
        
    def handle_new(self):
        pass
        
    def handle_read(self):
        try:
            data = self.socket.recv(4096)
        except socket.error:
            self.handle_exception()
        else:
            if len(data) == 0:
                self.handle_close()
            self.protocol.input_buffer.write(data)
            self.protocol.handle_read()

    def handle_write(self):
        data = self.protocol.output_buffer.peek(4096)
        if data:
            try:
                count = self.socket.send(data)
            except socket.error:
                self.handle_exception()
            else:
                self.protocol.output_buffer.discard(count)
    
    def handle_exception(self):
        self.protocol.handle_exception()
        
    def handle_close(self):
        self.shutdown()
        self.protocol.handle_close()

    def shutdown(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        SocketHandler.remove(self.socket)


class Protocol(object):
    """
    This abstract base class needs to be subclassed to provide anything
    useful. Its methods are called when data is ready for processing in the
    input and output buffers.
    """
    def __init__(self):
        self.input_buffer = StringQueue()
        self.output_buffer = StringQueue()
        
    def handle_close(self):
        pass
    
    def handle_read(self):
        pass
    
    def handle_exception(self):
        pass

    
#---------------------------------------------------------------------#
#User/Derived classes

class MessageProtocol(Protocol):
    """
    The message protocol fires and forgets events over a connections.
    Events are (name, dict) pairs. Recieved events are queued up in the
    messages attribute.
    """
    def __init__(self):
        Protocol.__init__(self)
        self.unpacker = self._create_unpacker(self.input_buffer)
        self.messages = []
    
    def _create_unpacker(self, buffer):
        """
        This generator yields new messages from the incoming buffer.
        """
        while True:
            if len(buffer) >= 4:
                size = struct.unpack("!l", buffer.read(4))[0]
                while len(buffer) < size:
                    yield None
                message = buffer.read(size)
                yield message
            else:
                yield None

    def pack_message(self, data):
        size = struct.pack("!l", len(data))
        return "".join((size, data))
    
    def post(self, name, **kw):
        """
        Post an event over the connection. The name argument is the event
        name, kw arguments are the event attributes.
        """
        data = self.pack_message(encoder.dumps((name, kw)))
        self.output_buffer.write(data)

    def handle_read(self):
        for message in self.unpacker:
            if message is not None:
                self.messages.append(encoder.loads(message))
            else: 
                break
                        

class Listener(Connection):
    """
    A generic TCP listener which adds new connections to the socket handler.
    Subclass and override handle_new to get the connection object.
    """
    def __init__(self, (host, port), protocol_class):
        Connection.__init__(self, self)
        self.protocol_class = protocol_class
        self.socket.bind((host, port))
        self.socket.listen(5)
        
    def handle_read(self):
        new_socket, address = self.socket.accept()
        protocol = self.protocol_class()
        c = Connection(protocol, sock=new_socket)
        self.handle_new(c)
        return c
    
        
class Connector(Connection):
    """
    A generic connector object, which connects to a listening socket using a 
    protocol. Can reconnect when connections are broken.
    """
    def __init__(self, (host, port), protocol_class, reconnect=False, reconnect_delay=1.0):
        Connection.__init__(self, protocol_class())
        self.reconnect = reconnect
        self.reconnect_delay = reconnect_delay
        self.host = host
        self.port = port
        self.connect()
            
    def connect(self):
        err = self.socket.connect_ex((self.host, self.port))
        if err in (EINPROGRESS, EALREADY, EWOULDBLOCK):
            pass
        else:
            raise socket.error, err
    
    def handle_close(self):
        if self.reconnect:
            self.connect()
                
    def handle_exception(self):        
        if self.reconnect:
            self.connect()
        
        

if __name__ == "__main__":
    class MyListener(Listener):
        def handle_new(self, p):
            print self
            p.protocol.post('OI')
            
            
    l = MyListener(('127.0.0.1',1024), MessageProtocol)
    c = Connector(('127.0.0.1',1024), MessageProtocol())
    nanothreads.install(SocketHandler.nanothread())
    def exit():
        raise SystemExit
    nanothreads.defer_for(5, exit)
    nanothreads.defer_for(1.0, c.protocol.post, 's', a=1)
    nanothreads.defer_for(1.5, c.shutdown)
    nanothreads.loop()














