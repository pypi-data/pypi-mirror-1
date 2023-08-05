import pygame
import pygame.locals
import driver

def pump_events():
    event_name = pygame.event.event_name
    while True:
        for event in pygame.event.get():
            driver.post(event_name(event.type), **event.dict)
        yield None
