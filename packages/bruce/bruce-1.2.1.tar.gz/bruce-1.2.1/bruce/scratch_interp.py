import pygame

from bruce.interp import InterpreterPage, MyInterpreter
from bruce.config import Config

class ScratchPadInterpreterPage(InterpreterPage):
    '''Run a Python interpreter with an attached PyGame scratch pad.
    '''
    def __init__(self, title='', text='', sysver=False, start_top=True):
        InterpreterPage.__init__(self, title, text, sysver)
        self.start_top = start_top

    def init(self, screen, start_top=True):
        InterpreterPage.init(self, screen)

        self.scratch = pygame.Surface((256, 256))
        self.scratch.fill((255, 255, 255))

        self.interpreter = MyInterpreter({'scratch': self.scratch,
            'pygame': pygame}, self.renderOutputLine)

    def render(self, screen, deltat):
        InterpreterPage.render(self, screen, deltat)

        # blit the scratch pad
        x = screen.get_rect().width - 256
        lh = Config.interp_font_size + 2
        if self.start_top or len(self.rendered_lines)*lh > 300:
            screen.blit(self.scratch, (x -10, lh + 10))
        else:
            y = screen.get_rect().height - 256
            screen.blit(self.scratch, (x -10, y-10))

