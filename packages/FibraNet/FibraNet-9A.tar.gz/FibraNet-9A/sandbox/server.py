import pygame
import nanothreads
import nanotubes
import time
import weakref
import random


class PygameListener(nanotubes.Listener):
    """
    A custom listener which tracks connections in a list. Connected sockets
    are available via the connections attribute, and use the MessageProtocol
    to communicate.
    """
    def __init__(self, (host, port)):
        nanotubes.Listener.__init__(self, (host, port), nanotubes.MessageProtocol)
        self.connections = []
        
    def broadcast(self, name, **kw):
        """
        Broadcast a message to all connected sockets.
        """
        for conn_ref in self.connections:
            conn_ref().protocol.post(name, **kw)
    
    def cleanup(self):
        """
        Remove dead connections.
        """
        connections = []
        for conn_ref in self.connections:
            if conn_ref() is not None:
                connections.append(conn_ref)
        self.connections[:] = connections
        
    def handle_new(self, conn):
        self.connections.append(weakref.ref(conn))
        

def main():
    pygame.init()
    #start a server listening for connections on port 1984
    server = PygameListener(('10.1.1.55',1984))
    screen = pygame.display.set_mode((320,200))

    while True:
        time.sleep(0.01)
        #the SocketHandler must be polled regularly.
        nanotubes.SocketHandler.poll()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
            elif event.type == pygame.MOUSEMOTION:
                #broadcast MOUSEMOTION events to all connected clients.
                server.broadcast(event.type, **event.dict)
        
        for conn_ref in server.connections:
            #get a reference to the connection
            conn = conn_ref()
            #if the reference is dead, ignore it
            if conn is None: continue
            #recieved events are stored in .protocol.messages
            for event_type, args in conn.protocol.messages:
                #if recieved event is pygame.MOUSEMOTION, draw a pixel
                if event_type == pygame.MOUSEMOTION:
                    screen.set_at(args['pos'], (255,255,255))
                #remove messages from the connections queue.
                conn.protocol.messages[:] = []
        pygame.display.flip()
        #cleanup and remove dead connections.
        server.cleanup()
        yield None
        

nanothreads.install(main())
nanothreads.loop()
