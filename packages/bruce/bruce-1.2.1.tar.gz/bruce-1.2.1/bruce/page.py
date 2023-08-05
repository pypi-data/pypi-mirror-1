from time import time
from bruce.fonts import get_font
from bruce.config import Config
import pygame.image

fontCode = get_font(Config.code_font, 30)


class Page(object):
    _last_render_time = None
    _last_render_time_font = None
    _last_render_page = None
    _last_render_page_font = None
    _footer_image = None
    _footer = True
    def __init__(self, **kw):
        if kw.get('nofooter'):
            self._footer = False

    def init(self, screen):
        if self._footer and Config.get('footer_image'):
            image = pygame.image.load(Config.get('footer_image')).convert()
            pos = Config.get('footer_align', 'centre')
            sw = screen.get_rect().width
            sh = screen.get_rect().height
            imw, imh = image.get_rect().size
            ypos = sh - 5 - imh
            if pos in ('centre', 'center'):
                xpos = sw/2 - imw/2
            elif pos == 'left':
                xpos = 5
            else:
                xpos = sw - 5 - imw
            self._footer_image = (image, (xpos,ypos))

    def activate(self, screen):
        pass
    def handleEvent(self, event):
        return event
    def render(self, screen, deltat):
        from bruce.main import options, startTime
        if self._footer and self._footer_image:
            image, pos = self._footer_image
            screen.blit(image, pos)

        if options.timer:
            now = int(time() - startTime)
            if self._last_render_time != now:
                tt = "%02d:%02d"%(now/60, now%60)
                colour = Config.get('clock_colour', (255,255,255))
                self._last_render_time_font = fontCode.render(tt, 1, colour)
                self._last_render_time = now
            h = screen.get_rect().height 
            screen.blit(self._last_render_time_font, (20,h-50))
        if options.pageCount:
            from bruce.main import presentation
            c = presentation.currentPage + 1
            if self._last_render_page != c:
                pp = "% 3d"%(c)
                colour = Config.get('clock_colour', (255,255,255))
                self._last_render_page_font = fontCode.render(pp, 1, colour)
                self._last_render_page = c
            w = screen.get_rect().width 
            h = screen.get_rect().height 
            screen.blit(self._last_render_page_font, (w-80,h-50))

