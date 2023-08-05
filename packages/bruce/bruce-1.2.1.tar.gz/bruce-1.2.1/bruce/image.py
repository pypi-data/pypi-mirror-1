import pygame

from bruce.config import Config
from bruce.page import Page
from bruce.fonts import get_font

# TODO use PIL for scaling down - it's so much better at it

class ImagePage(Page):
    def __init__(self, title, image, **kw):
        self.title = title
        self.image = image
        self.border = 0
        super(ImagePage, self).__init__(**kw)


    def init(self, screen):
        # init title

        if self.title:
            FONT_SIZE = int(Config.get(['title_font_size',
                'text_font_size'], 64))
            font = get_font(Config.title_font, FONT_SIZE)
            self.title = font.render(self.title, 1, Config.title_fgcolour)
            self.border = FONT_SIZE

        # load image and resize
        image = pygame.image.load(self.image).convert()
        w = screen.get_rect().width - self.border*2
        h = screen.get_rect().height - self.border*2
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
        super(ImagePage, self).init(screen)

    def render(self, screen, deltat):
        screen.fill(Config.page_bgcolour)

        w = screen.get_rect().width
        if self.title:
            tw = self.title.get_rect().width
            screen.blit(self.title, (w/2-tw/2, 0))

        # border
        w -= self.border*2
        h = screen.get_rect().height

        imw, imh = self.image.get_rect().size
        screen.blit(self.image, (self.border + w/2 - imw/2,
            self.border + h/2 - imh/2))
        super(ImagePage, self).render(screen, deltat)


