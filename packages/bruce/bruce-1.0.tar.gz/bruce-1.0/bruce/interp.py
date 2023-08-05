import pygame, sys, pprint, sets, code, StringIO, time, os
from pygame.locals import *

from bruce.config import Config
from bruce.page import Page
from bruce.fonts import get_font

FONT_HEIGHT = 24
LINE_HEIGHT = 26
fontBd = get_font(os.path.join(Config.data, 'VeraBd.ttf'), FONT_HEIGHT)
fontmono = get_font(os.path.join(Config.data, 'VeraMono.ttf'),
    FONT_HEIGHT)
em = fontmono.size('M')[0]

class MyInterpreter(code.InteractiveInterpreter):
    error = None
    def write(self, error):
        self.error = error

shift_keys = sets.Set((K_RSHIFT, K_LSHIFT))

class InterpreterPage(Page):
    '''Run a Python interpreter.

    Backspace deletes text.

    The optional "text" may be used to "auto-type" into the interpreter.
    If activated by control-I any further keystrokes will be taken from
    this text until the end of a line. Hitting return will then invoke
    the line as per usual and move the auto-typer on to the next line.
    Backspace is not handled. Shift-return will complete the current line
    and invoke it.

    The up and down keys will search through the input history.
    '''
    def __init__(self, title='', text='', sysver=False):
        cursor = pygame.Surface((10, 2))
        pygame.draw.rect(cursor, Config.cursor_fgcolour, (0, 0, 10, 2))
        self.cursor = cursor
        if title:
            self.title = fontBd.render(title, 1, Config.title_fgcolour)
        else:
            self.title = None

        # figure the text to render and make it poppable
        self.auto_lines = [list(line)
            for line in text.strip().splitlines()]
        self.auto_lines.reverse()
        [line.reverse() for line in self.auto_lines]

        # actual rendered lines to draw to the screen
        self.rendered_lines = []

        # insert system version?
        if sysver:
            for line in sys.version.splitlines():
                self.rendered_lines.append(fontmono.render(line, 1,
                    Config.text_fgcolour))

        # current typed line
        self.current_line = ['>', '>', '>', ' ']
        line = ''.join(self.current_line)
        self.rendered_lines.append(fontmono.render(line, 1,
                    Config.text_fgcolour))

        # input from the user which doesn't quite form complete
        # interpreter input
        self.captured_input = []

        self.history = []
        self.hist_num = 0

        self.auto_mode = False
        self.auto_line = []

        self.blink_time = 0
        self.blink_state = False

    def init(self, screen):
        self.interpreter = MyInterpreter({'pygame': pygame})
        sh = screen.get_rect().height
        if self.title:
            sh -= self.title.get_rect().height
        self.max_rendered_lines = (sh - LINE_HEIGHT) / LINE_HEIGHT
        sw = screen.get_rect().width
        self.columns = sw / em
        if sw % em: self.columns -= 1

    def handleEvent(self, event):
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                if not self.auto_mode and len(self.current_line) > 4:
                    self.current_line.pop()
                    self.render_current_line()
                return None
            if event.key == K_RETURN:
                if event.mod & KMOD_SHIFT and self.auto_mode:
                    while self.auto_line:
                        glyph = self.auto_line.pop()
                        self.current_line.append(glyph)

                if self.auto_mode and self.auto_line:
                    # don't honor the return key yet
                    return None

                # evaluate the input
                input = ''.join(self.current_line[4:])

                # ignore key-up events (typically the next
                # event in the queue)
                if (input.startswith('pygame.event.wait()') or
                        input.startswith('pygame.event.poll()')):
                    pygame.event.set_blocked(KEYUP)

                # run the interpreter
                self.captured_input.append(input)
                old_stdout = sys.stdout
                output = sys.stdout = StringIO.StringIO()
                input = '\n'.join(self.captured_input)
                more = self.interpreter.runsource(input)
                sys.stdout = old_stdout

                if not more:
                    self.captured_input = []

                # handle the output
                output.seek(0)
                out = []
                for line in output.readlines():
                    out.append(line.strip())
                if self.interpreter.error:
                    out.append(self.interpreter.error.strip())
                    self.interpreter.error = None

                display_out = []
                for line in out:
                    for n in range(len(line)/self.columns + 1):
                        text = line[n*self.columns:(n+1)*self.columns]
                        r = fontmono.render(text, 1, Config.text_fgcolour)
                        self.rendered_lines.append(r)

                if (input.startswith('pygame.event.wait()') or
                        input.startswith('pygame.event.poll()')):
                    pygame.event.set_allowed(KEYUP)

                # new line
                if input:
                    self.history.append(self.current_line)
                if more:
                    self.current_line = ['.', '.', '.', ' ']
                else:
                    self.current_line = ['>', '>', '>', ' ']

                # possibly remove an extraneous line?
                if len(self.rendered_lines) > self.max_rendered_lines:
                    diff = len(self.rendered_lines) - self.max_rendered_lines
                    self.rendered_lines = self.rendered_lines[diff:]

                # render the last line
                line = ''.join(self.current_line)
                r = fontmono.render(line, 1, Config.text_fgcolour)
                self.rendered_lines.append(r)

                self.hist_num = 0
                if self.auto_mode:
                    if not self.auto_lines:
                        self.auto_mode = False
                    else:
                        self.auto_line = self.auto_lines.pop()
                return None
            if not event.mod:
                if event.key == K_UP and self.history:
                    if not self.hist_num:
                        self.history.append(list(self.current_line))
                        self.hist_num = -1
                    if abs(self.hist_num) < len(self.history):
                        self.hist_num -= 1
                    self.current_line[:] = self.history[self.hist_num]
                    self.render_current_line()
                    return None
                if event.key == K_DOWN and self.history:
                    if self.hist_num < -1:
                        self.hist_num += 1
                    self.current_line[:] = self.history[self.hist_num]
                    self.render_current_line()
                    return None
            if event.key == K_i and event.mod & KMOD_CTRL:
                self.auto_mode = not self.auto_mode
                if self.auto_mode:
                    if self.auto_lines:
                        self.auto_line = self.auto_lines.pop()
                    else:
                        self.auto_mode = False
                self.current_line[:] = ['>', '>', '>', ' ']
                return None
            if event.key == K_d and event.mod & KMOD_CTRL:
                # control-D quits interpreter
                return event
            if event.key in shift_keys:
                # we use this as a modifier
                return None
            if event.mod & (KMOD_CTRL|KMOD_META|KMOD_ALT):
                return event
            if event.key == K_ESCAPE:
                # for some reason this key has a unicode representation
                return event

            glyph = getattr(event, 'unicode', None)

            # is this a useful interpreter key?
            if not glyph or ord(glyph) > 256:
                return event

            # use auto key or user key?
            if self.auto_mode:
                if self.auto_line:
                    glyph = self.auto_line.pop()
                else:
                    return None

            self.current_line.append(glyph)
            self.render_current_line()
            return None

        return event

    def render_current_line(self):
        line = ''.join(self.current_line)
        self.rendered_lines[-1] = fontmono.render(line, 1, Config.text_fgcolour)

    def render(self, screen, deltat):
        screen.fill(Config.page_bgcolour)

        self.blink_time += deltat
        if self.blink_time > 500:
            self.blink_state = not self.blink_state
            self.blink_time = 0

        toff = 0
        if self.title:
            screen.blit(self.title, (0, 0))
            toff = self.title.get_rect().height

        for n, line in enumerate(self.rendered_lines):
            hoff = toff + n * LINE_HEIGHT
            screen.blit(line, (0, hoff))

        if not self.blink_state:
            x = line.get_rect().width
            pygame.draw.rect(screen, Config.cursor_fgcolour,
                (x, toff + n*LINE_HEIGHT + 32, 10, 2))

