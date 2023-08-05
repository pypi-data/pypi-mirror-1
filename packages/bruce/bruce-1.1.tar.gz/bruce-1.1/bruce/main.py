import sys, os

import pygame
from pygame.locals import *

pygame.init()
pygame.font.init()

from bruce.config import Config

def main(pages, fullscreen=False):
    # init screen
    fullscreen = '-fs' in sys.argv
    viewport = (1024, 768)
    if fullscreen:
        screen_flags = HWSURFACE | FULLSCREEN | DOUBLEBUF
    else:
        screen_flags = HWSURFACE | DOUBLEBUF
    screen = pygame.display.set_mode(viewport, screen_flags)
    pygame.mouse.set_visible(False)

    # init the pages
    for page in pages:
        page.init(screen)
    page_position = 0
    oldpos = None

    clock = pygame.time.Clock()
    while 1:
        deltat = clock.tick(30)

        # handle events -- NOTE THAT THE PAGE CHANGES AFTER WE
        # HANDLE ALL EVENTS
        for event in pygame.event.get():
            if event.type == NOEVENT:
                continue
            if event.type == QUIT:
                return

            # see if the page will handle the event
            event = page.handleEvent(event)
            if event is None: continue

            if event.type == KEYDOWN:
                if event.key == K_PRINT:
                    pygame.image.save(self.screen, '/tmp/screenshot.bmp')
                elif event.key == K_ESCAPE:
                    return
                elif event.key == K_d and event.mod & KMOD_CTRL:
                    # == "next page" when in an interpreter
                    page_position += 1
                    if page_position >= len(pages):
                        page_position = len(pages)-1
                elif event.key == K_RIGHT:
                    page_position += 1
                    if page_position >= len(pages):
                        page_position = len(pages)-1
                elif event.key == K_LEFT:
                    page_position -= 1
                    if page_position < 0: page_position = 0
                elif event.key == K_DOWN:
                    page_position += 5
                    if page_position >= len(pages):
                        page_position = len(pages)-1
                elif event.key == K_UP:
                    page_position -= 5
                    if page_position < 0: page_position = 0
                elif event.key == K_END:
                    page_position = len(pages)-1
                elif event.key == K_HOME:
                    page_position = 0


        page = pages[page_position]

        if oldpos != page_position:
            page.activate(screen)
            oldpos = page_position

        # render
        page.render(screen, deltat)
        pygame.display.flip()

