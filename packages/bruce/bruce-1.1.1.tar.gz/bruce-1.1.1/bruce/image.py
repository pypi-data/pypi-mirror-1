import pygame, os

from bruce.config import Config
from bruce.page import Page
from bruce.fonts import get_font

font = get_font(Config.title_font, 64)

BORDER = 64

# TODO use PIL for scaling down - it's so much better at it

class ImagePage(Page):
    def __init__(self, title, image):
        self.title = title
        self.image = image

    def init(self, screen):
        # init title
        self.title = font.render(self.title, 1, Config.title_fgcolour)

        # load image and resize
        image = pygame.image.load(self.image).convert()
        w = screen.get_rect().width - BORDER*2
        h = screen.get_rect().height - BORDER*2
        imw, imh = image.get_rect().size
        if imw > w or imh > h:
            if imw > imh:
                ratio = float(w) / imw
                imw = w
                imh *= ratio
            else:
                ratio = float(h) / imh
                imh = h
                imw *= ratio
        self.image = pygame.transform.scale(image, (int(imw), int(imh)))

    def render(self, screen, deltat):
        screen.fill(Config.page_bgcolour)

        w = screen.get_rect().width
        tw = self.title.get_rect().width
        screen.blit(self.title, (w/2-tw/2, 0))

        # border
        w -= BORDER*2
        h = screen.get_rect().height

        imw, imh = self.image.get_rect().size
        screen.blit(self.image, (BORDER + w/2 - imw/2, BORDER + h/2 - imh/2))

