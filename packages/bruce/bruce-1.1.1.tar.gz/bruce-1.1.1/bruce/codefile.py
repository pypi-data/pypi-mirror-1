import pygame, os, string

from bruce.config import Config
from bruce.page import Page
from bruce.fonts import get_font

def fit_text((w, h), text): #, fontsize=64):
    # start off trying for best fit
    fontsize = h / len(text)
    while 1:
        font = get_font(Config.code_font, fontsize)
        tw = th = 0
        for line in text:
            width, height = font.size(line)
            tw = max(width, tw)
            th += height
        if tw < w and th < h:
            return tw, th, fontsize
        fontsize = int(fontsize * .9)

class CodeFilePage(Page):
    def __init__(self, title, file, bgcolour=Config.code_bgcolour,
            fgcolour=Config.code_fgcolour):
        self.pagetext = [line.rstrip() for line in open(file)]
        self.title = title
        self.fgcolour = fgcolour
        self.bgcolour = bgcolour

    def init(self, screen):
        sw = screen.get_rect().width
        fontsize = 64
        while 1:
            font = get_font(Config.title_font, fontsize)
            if font.size(self.title)[0] < sw:
                break
            fontsize = int(fontsize * .75)
        self.title = font.render(self.title, 1, Config.title_fgcolour)
        th = self.title.get_rect().height

        w, h = screen.get_rect().size
        h -= th
        w, h, fontsize = fit_text((w, h), self.pagetext)
        self.pageblock = pygame.Surface((w, h))
        self.pageblock.fill(self.bgcolour)
        font = get_font(Config.code_font, fontsize)
        y = 0
        for line in self.pagetext:
            line = font.render(line, 1, self.fgcolour)
            self.pageblock.blit(line, (0, y))
            y += line.get_rect().height

    def render(self, screen, deltat):
        screen.fill(Config.page_bgcolour)

        sw, sh = screen.get_rect().size

        tw, th = self.title.get_rect().size
        screen.blit(self.title, (sw/2 - tw/2, 0))

        bw, bh = self.pageblock.get_size()
        l = sw/2 - bw/2
        t = th + (sh-th)/2 - bh/2
        screen.blit(self.pageblock, (l, t))

