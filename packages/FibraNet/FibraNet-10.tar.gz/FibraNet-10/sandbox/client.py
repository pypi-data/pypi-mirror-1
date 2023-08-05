import pygame
import nanothreads
import nanotubes
import time


def main():
    pygame.init()
    #create a client connection to the server on port 1984 using the MessageProtocol
    client = nanotubes.Connector(('10.1.1.55',1984), nanotubes.MessageProtocol)
    screen = pygame.display.set_mode((320,200))

    while True:
        time.sleep(0.01)
        #itereate the network queue
        nanotubes.SocketHandler.poll()
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit
                elif event.type == pygame.MOUSEMOTION:
                    #send all MOUSEMOTION events to the server
                    client.protocol.post(event.type, **event.dict)
        
        #any events recieved from the server are stored in client.protocol.messages
        for event_type, args in client.protocol.messages:
            if event_type == pygame.MOUSEMOTION:
                #draw all MOUSEMOTION events as pixels to the screen
                screen.set_at(args['pos'], (255,255,255))
        
        #clear the incoming network event queue
        client.protocol.messages[:] = []
        pygame.display.flip()
        yield None
        

nanothreads.install(main())
nanothreads.loop()