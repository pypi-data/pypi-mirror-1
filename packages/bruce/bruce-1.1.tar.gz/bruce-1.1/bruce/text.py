import pygame, os
from pygame.locals import *

from bruce.config import Config
from bruce.page import Page
from bruce.fonts import get_font

FONT_SIZE = 64

font = get_font(Config.text_font, FONT_SIZE)
if Config.bold_font:
    fontBd = get_font(Config.bold_font, FONT_SIZE)
else:
    fontBd = get_font(Config.text_font, FONT_SIZE, bold=True)

LINE_SPACE = FONT_SIZE/2

class BlankLine:
    pass

class TextPage(Page):
    '''Displays some text centered on screen.

    The first line is always bolded.

    Obeys newlines.

    Lines starting withj '-' (dash) are initially hidden and are exposed
    or hidden with the left/right arrow keys. Modified arrow keys are
    ignored here, so will change pages.
    '''
    def __init__(self, text):
        self.width = 0
        self.height = 0
        self.lines = []
        self.hidden_lines = []
        for line in text.strip().splitlines():
            if line.startswith('-'):
                line = line[1:]
                hidden = True
            else:
                hidden = False

            if not line:
                # blank line, don't bother rendering
                self.lines.append(BlankLine)
                self.height += FONT_SIZE + LINE_SPACE
                continue

            if line.startswith('='):
                line = fontBd.render(line[1:], 1, Config.title_fgcolour)
            else:
                line = font.render(line, 1, Config.text_fgcolour)
            if hidden:
                self.hidden_lines.append(line)
            else:
                self.lines.append(line)
            self.width = max(self.width, line.get_rect().width)
            self.height += FONT_SIZE + LINE_SPACE

        # so we can pop() lines off
        self.hidden_lines.reverse()
        self.popped_lines = []
        self.need_render = True

    def handleEvent(self, event):
        if event.type == KEYDOWN:
            if event.mod & (KMOD_SHIFT|KMOD_CTRL|KMOD_META|KMOD_ALT):
                return event
            if event.key == K_RIGHT:
                if not self.hidden_lines:
                    return event
                line = self.hidden_lines.pop()
                self.popped_lines.append(line)
                self.lines.append(line)
                self.need_render = True
                return None
            elif event.key == K_LEFT:
                if not self.popped_lines:
                    return event
                line = self.popped_lines.pop()
                self.lines.pop()
                self.hidden_lines.append(line)
                self.need_render = True
                return None
        return event

    def render(self, screen, deltat):
        screen.fill(Config.page_bgcolour)
        w = screen.get_rect().width / 2
        h = screen.get_rect().height / 2
        hoffs = h - self.height/2
        for n, line in enumerate(self.lines):
            if line is BlankLine:
                continue
            r = line.get_rect()
            lw = r.w/2
            screen.blit(line, (w-lw, hoffs + n * FONT_SIZE * 1.5))
        self.need_render = False

