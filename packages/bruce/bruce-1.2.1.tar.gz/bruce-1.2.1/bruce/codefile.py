import pygame

from bruce.config import Config
from bruce.page import Page
from bruce.fonts import get_font

def fit_text((w, h), text):
    # start off trying for best fit
    fontsize = min(Config.codefile_font_size, h / len(text))
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
    def __init__(self, title, file, bgcolour=None, fgcolour=None, 
                    highlight='', skiphashbang=False, **kw):
        self.pagetext = [line.rstrip() for line in open(file)]
        self.title = title
        lines = [line.rstrip() for line in open(file)]

        # handle hidden lines       (end comment #--)
        m = []
        skip = False
        for line in lines:
            if skiphashbang and line.startswith("#!"): continue
            if line.endswith('#--'):
                if not skip:
                    m.append('...')
                    skip = True
                else:
                    continue
            else:
                m.append(line)
                skip = False
        lines = m

        if highlight:
            # handle title
            self.pagetext = []
            for l in lines:
                if not l.startswith('#='):
                    self.pagetext.append(l)
                if l.startswith('#='+highlight):
                    els = l.split(' ', 1)
                    if len(els) == 2:
                        self.title = l[len(highlight)+2:].strip()
        else:
            self.pagetext = [line.rstrip() for line in open(file)]
        self.fgcolour = None
        self.bgcolour = None
        self.highlight = highlight
        super(CodeFilePage, self).__init__(**kw)

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
        self.pageblock = pygame.Surface((w + 20, h + 20))
        self.pageblock.fill(self.bgcolour or Config.code_bgcolour)
        font = get_font(Config.code_font, fontsize)
        y = 0
        for line in self.pagetext:
            HL = len(self.highlight)
            colour = self.fgcolour or Config.code_fgcolour
            if self.highlight:
                if line.startswith('#='): continue
                if line.endswith('#'+self.highlight):
                    colour = Config.code_hilitecolour
                if line.endswith('//'+self.highlight):
                    colour = Config.code_hilitecolour
                if len(line) > HL and line[-(HL+1)] == '#':
                    line = line[:-(HL+1)].rstrip()
                if len(line) > HL and line[-(HL+2):-(HL)] == '//':
                    line = line[:-(HL+2)].rstrip()
            line = font.render(line, 1, colour)
            self.pageblock.blit(line, (10, 10+y))
            y += line.get_rect().height
        super(CodeFilePage, self).init(screen)

    def render(self, screen, deltat):
        screen.fill(Config.page_bgcolour)

        sw, sh = screen.get_rect().size

        tw, th = self.title.get_rect().size
        screen.blit(self.title, (sw/2 - tw/2, 0))

        bw, bh = self.pageblock.get_size()
        l = sw/2 - bw/2
        t = th + (sh-th)/2 - bh/2
        screen.blit(self.pageblock, (l, t))
        super(CodeFilePage, self).render(screen, deltat)


