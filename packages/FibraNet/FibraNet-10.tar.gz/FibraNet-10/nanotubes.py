#Copyright (c) 2006 Simon Wittber
#
#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation files
#(the "Software"), to deal in the Software without restriction,
#including without limitation the rights to use, copy, modify, merge,
#publish, distribute, sublicense, and/or sell copies of the Software,
#and to permit persons to whom the Software is furnished to do so,
#subject to the following conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
#BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

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
    def handle_close(self):
        pass
        
    def handle_read(self):
        pass

    def handle_write(self):
        pass
    
    def handle_exception(self):
        pass
        
    
class TCPConnection(Connection):
    def __init__(self, tcp_socket, protocol):
        self.protocol = protocol
        self.tcp_socket = tcp_socket
        self.tcp_socket.setblocking(0)
        SocketHandler.add_socket(self.tcp_socket, self)
        
    def channel(self, port):
        """
        Opens a UDP channel on a port.
        """
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return UDPConnection(udp_socket, (self.host, port))
        
    def handle_read(self):
        try:
            data = self.tcp_socket.recv(4096)
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
                count = self.tcp_socket.send(data)
            except socket.error:
                self.handle_exception()
            else:
                self.protocol.output_buffer.discard(count)
    
    def handle_exception(self):
        self.protocol.handle_exception()
        

class UDPConnection(Connection):
    def __init__(self, udp_socket, (host, port)):
        self.udp_socket = udp_socket
        self.udp_socket.setblocking(0)
        self.host = host
        self.port = port
        self.transmissions = []
        SocketHandler.add_socket(self.udp_socket, self)
        
    def listen(self, receiver):
        """
        Listen on this channel for incoming traffic.
        receiver is a callback function which takes (address, data) as args.
        """
        self.receiver = receiver
        self.udp_socket.bind((self.host, self.port))
        self.handle_read = self._handle_read
    
    def handle_read(self):
        #Do nothing by default.
        pass
        
    def _handle_read(self):
        try:
            data, address = self.udp_socket.recvfrom(4096)
        except socket.error, e:
            self.handle_exception()
        else:
            self.receiver(address, data)
            
    def transmit(self, address, data):
        """
        Transmit data to address on this channel's port.
        """
        self.transmissions.append((address, data))
    
    def handle_write(self):
        try:
            address, data = self.transmissions.pop(-1)
        except IndexError:
            pass
        else:
            try:
                count = self.udp_socket.sendto(data, (address, self.port))
            except socket.error, e:
                self.handle_exception()
            
    def handle_exception(self):
        print 'UDP Exception.'
        pass


class Protocol(object):
    def __init__(self):
        self.input_buffer = StringQueue()
        self.output_buffer = StringQueue()
        
    def handle_close(self):
        pass
    
    def handle_read(self):
        pass
    
    def handle_exception(self):
        pass


class Listener(TCPConnection):
    """
    Opens a socket and starts listening for connections.
    """
    def __init__(self, (host, port), protocol_factory):
        TCPConnection.__init__(self, socket.socket(socket.AF_INET, socket.SOCK_STREAM), self)
        self.host = host
        self.port = port
        self.protocol_factory = protocol_factory
        self.tcp_socket.bind((host, port))
        self.tcp_socket.listen(5)
        
    def handle_new(self, tcp_connection):
        pass
        
    def handle_read(self):
        new_socket, address = self.tcp_socket.accept()
        c = TCPConnection(new_socket, self.protocol_factory())
        self.handle_new(c)


class Connector(TCPConnection):
    """
    Connects to a socket on a remote host.
    """
    def __init__(self, (host, port), protocol_factory):
        TCPConnection.__init__(self, socket.socket(socket.AF_INET, socket.SOCK_STREAM), protocol_factory())
        self.host = host
        self.port = port
        self.connect()
        
    def connect(self):
        err = self.tcp_socket.connect_ex((self.host, self.port))
        if err in (EINPROGRESS, EALREADY, EWOULDBLOCK):
            pass
        else:
            raise socket.error, err
    
#---------------------------------------------------------------------#

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

    def pack_message(self, name, kw):
        data = encoder.dumps((name, kw))
        size = struct.pack("!l", len(data))
        return "".join((size, data))
    
    def post(self, name, **kw):
        """
        Post an event over the connection. The name argument is the event
        name, kw arguments are the event attributes.
        """
        data = self.pack_message(name, kw)
        self.output_buffer.write(data)

    def handle_read(self):
        for message in self.unpacker:
            if message is not None:
                self.messages.append(encoder.loads(message))
            else: 
                break

