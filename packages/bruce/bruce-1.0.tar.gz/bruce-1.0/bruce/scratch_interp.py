import pygame

from bruce.interp import InterpreterPage, MyInterpreter, LINE_HEIGHT

class ScratchPadInterpreterPage(InterpreterPage):
    '''Run a Python interpreter with an attached PyGame scratch pad.
    '''
    def init(self, screen):
        InterpreterPage.init(self, screen)

        self.scratch = pygame.Surface((256, 256))
        self.scratch.fill((255, 255, 255))

        self.interpreter = MyInterpreter({'scratch': self.scratch,
            'pygame': pygame})

    def render(self, screen, deltat):
        InterpreterPage.render(self, screen, deltat)

        # blit the scratch pad
        x = screen.get_rect().width - 256
        if len(self.rendered_lines)*LINE_HEIGHT > 300:
            screen.blit(self.scratch, (x -10, LINE_HEIGHT + 10))
        else:
            y = screen.get_rect().height - 256
            screen.blit(self.scratch, (x -10, y-10))

