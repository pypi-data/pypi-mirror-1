import pygame
from pygame import locals as L
from bruce.shell import spawner
from time import time

# Don't init sound!
pygame.display.init()
pygame.font.init()

#from bruce.config import Config

class _options:
    fullscreen = False
    startpage = 1
    timer = False
    pageCount = False

options = _options()

startTime = None
screen = None

def main(pages, fullscreen=False, startpage=1):
    global presentation
    presentation = Presentation(pages)
    presentation.initdisplay(fullscreen)
    try:
        presentation.startdisplay(startpage)
    finally:
        spawner.kill()

class Presentation(object):
    def __init__(self, pages):
        self.pages = pages
        self.currentPage = 0

    def initdisplay(self, fullscreen=False):
        global screen
        # init screen
        viewport = (1024, 768)
        if fullscreen:
            screen_flags = L.HWSURFACE | L.FULLSCREEN | L.DOUBLEBUF
        else:
            screen_flags = L.HWSURFACE | L.DOUBLEBUF
        screen = pygame.display.set_mode(viewport, screen_flags)
        pygame.mouse.set_visible(False)

    def _get_page_position(self):
        return self.currentPage
        
    def _set_page_position(self, new):
        self.currentPage = new
        if self.currentPage >= len(self.pages):
            self.currentPage = len(self.pages)-1
        if self.currentPage < 0:
            self.currentPage = 0

    page_position = property(_get_page_position, _set_page_position)

    def startdisplay(self, startpage):
        global screen, startTime
        if options.timer:
            startTime = time()
        # init the pages
        for page in self.pages:
            page.init(screen)
        # startpage starts at 1.
        self.page_position = int(startpage) - 1
        oldpos = None

        clock = pygame.time.Clock()
        while 1:
            deltat = clock.tick(30)

            # handle events -- NOTE THAT THE PAGE CHANGES AFTER WE
            # HANDLE ALL EVENTS
            for event in pygame.event.get():
                if event.type == L.NOEVENT:
                    continue
                if event.type == L.QUIT:
                    return

                # see if the page will handle the event
                event = page.handleEvent(event)
                if event is None: continue

                if event.type == L.KEYDOWN:
                    if event.key == L.K_ESCAPE:
                        return
                    elif event.key == L.K_f and event.mod & L.KMOD_CTRL:
                        pygame.display.toggle_fullscreen()
                    elif event.key == L.K_p and event.mod & L.KMOD_CTRL:
                        pygame.image.save(screen, '/tmp/screenshot.bmp')
                    elif event.key == L.K_d and event.mod & L.KMOD_CTRL:
                        # == "next page" when in an interpreter
                        self.page_position += 1
                    elif event.key == L.K_c and event.mod & L.KMOD_CTRL:
                        spawner.kill()
                    elif event.key == L.K_RIGHT or event.key == L.K_SPACE:
                        self.page_position += 1
                    elif event.key == L.K_LEFT:
                        self.page_position -= 1
                    elif event.key == L.K_DOWN:
                        self.page_position += 5
                    elif event.key == L.K_UP:
                        self.page_position -= 5
                    elif event.key == L.K_END:
                        self.page_position = len(self.pages)-1
                    elif event.key == L.K_HOME:
                        self.page_position = 0
                elif event.type == L.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.page_position += 1
                    elif event.button == 3:
                        self.page_position -= 1

            while True:
                page = self.pages[self.page_position]
                if oldpos != self.page_position:
                    page.activate(screen)
                    oldpos = self.page_position
                # render the current page
                if not page.render(screen, deltat):
                    break
                # render returns 'True' to mean 'autoadvance to next page'
                self.page_position += 1
                pygame.display.flip()
            pygame.display.flip()

