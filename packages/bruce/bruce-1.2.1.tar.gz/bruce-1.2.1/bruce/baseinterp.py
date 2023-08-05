import pygame, sets
from pygame import locals as L

from bruce.config import Config
from bruce.page import Page
from bruce.fonts import get_font

FONT_HEIGHT = 24
LINE_HEIGHT = FONT_HEIGHT + 2

fontmono = fontBd = None
def init(force=False):
    global fontmono, fontBd, em
    if fontmono is not None and not force:
        return
    fontBd = get_font(Config.text_font, FONT_HEIGHT, bold=True)
    fontmono = get_font(Config.code_font, FONT_HEIGHT)
    em = fontmono.size('M')[0]
init()


shift_keys = sets.Set((L.K_RSHIFT, L.K_LSHIFT))

class BaseInterpreterPage(Page, object):
    '''Run a "shell" interpreter.

    Backspace deletes text.

    The optional "text" may be used to "auto-type" into the interpreter.
    If activated by control-I any further keystrokes will be taken from
    this text until the end of a line. Hitting return will then invoke
    the line as per usual and move the auto-typer on to the next line.
    Backspace is not handled. Shift-return will complete the current line
    and invoke it.

    The up and down keys will search through the input history.
    '''

    def preamble(self): 
        pass

    def __init__(self, title='', text='', auto_mode=False, **kw):
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

        # Insert text at the start (optional)
        self.preamble()

        # current typed line
        self.current_line = list(self.prompt)
        line = ''.join(self.current_line)
        self.rendered_lines.append(fontmono.render(line, 1,
                    Config.text_fgcolour))

        # input from the user which doesn't quite form complete
        # interpreter input
        self.captured_input = []

        self.history = []
        self.hist_num = 0

        self.auto_mode = auto_mode
        self.auto_line = []

        self.blink_time = 0
        self.blink_state = False
        super(BaseInterpreterPage, self).__init__(**kw)

    def init(self, screen):
        sh = screen.get_rect().height
        if self.title:
            sh -= self.title.get_rect().height
        self.max_rendered_lines = (sh - LINE_HEIGHT) / LINE_HEIGHT
        sw = screen.get_rect().width
        em = fontmono.size('M')[0]
        self.columns = sw / em
        if sw % em: self.columns -= 1
        if self.auto_mode:
            if self.auto_lines:
                self.auto_line = self.auto_lines.pop()
            else:
                self.auto_mode = False
        super(BaseInterpreterPage, self).init(screen)

    def renderOutputLine(self, line):
        from bruce.main import screen
        for n in range(len(line)/self.columns + 1):
            text = line[n*self.columns:(n+1)*self.columns]
            r = fontmono.render(text, 1, Config.text_fgcolour)
            self.rendered_lines.append(r)
        # possibly remove an extraneous line?
        if len(self.rendered_lines) > self.max_rendered_lines:
            diff = len(self.rendered_lines) - self.max_rendered_lines
            self.rendered_lines = self.rendered_lines[diff:]
        self.render(screen, 1)
        pygame.display.flip()

    def _current_prompt(self):
        if self.captured_input:
            return self.prompt2
        else:
            return self.prompt
    curprompt = property(_current_prompt)

    def handleEvent(self, event):
        turbo_mode = False
        mouse = event.type == L.MOUSEBUTTONDOWN
        key = event.type == L.KEYDOWN
        if mouse or key:
            if key and event.key == L.K_BACKSPACE:
                if not self.auto_mode and (len(self.current_line) > 
                                                    len(self.curprompt)):
                    self.current_line.pop()
                    self.render_current_line()
                return None
            if key and event.key == L.K_u and event.mod & L.KMOD_CTRL:
                self.current_line[:] = list(self.curprompt)
                self.render_current_line()
            if ((key and event.key == L.K_RETURN) or 
                            (mouse and event.button == 2)):
                if key and event.mod & L.KMOD_SHIFT and self.auto_mode:
                    while self.auto_line:
                        glyph = self.auto_line.pop()
                        self.current_line.append(glyph)

                if self.auto_mode and self.auto_line:
                    # don't honor the return key yet
                    return None

                # evaluate the input
                if self.captured_input:
                    # on a second line
                    offset = len(self.prompt2)
                else:
                    offset = len(self.prompt)
                input = ''.join(self.current_line[offset:])

                more = self.processLine(input)

                if not more:
                    self.captured_input = []

                # new line
                if input:
                    self.history.append(self.current_line)
                if more:
                    self.current_line[:] = list(self.prompt2)
                else:
                    self.current_line[:] = list(self.prompt)

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
            if key and not event.mod:
                if event.key == L.K_UP and self.history:
                    if not self.hist_num:
                        self.history.append(list(self.current_line))
                        self.hist_num = -1
                    if abs(self.hist_num) < len(self.history):
                        self.hist_num -= 1
                    self.current_line[:] = self.history[self.hist_num]
                    self.render_current_line()
                    return None
                if event.key == L.K_DOWN and self.history:
                    if self.hist_num < -1:
                        self.hist_num += 1
                    self.current_line[:] = self.history[self.hist_num]
                    self.render_current_line()
                    return None
            if key and event.key == L.K_i and event.mod & L.KMOD_CTRL:
                self.auto_mode = not self.auto_mode
                if self.auto_mode:
                    if self.auto_lines:
                        self.auto_line = self.auto_lines.pop()
                    else:
                        self.auto_mode = False
                self.current_line[:] = list(self.prompt)
                return None
            if key and event.key == L.K_d and event.mod & L.KMOD_CTRL:
                # control-D quits interpreter
                return event
            if key and event.key in shift_keys:
                # we use this as a modifier
                return None
            if key and event.mod & (L.KMOD_CTRL|L.KMOD_META|L.KMOD_ALT):
                return event
            if key and event.key == L.K_ESCAPE:
                # for some reason this key has a unicode representation
                return event
            if key and event.key == L.K_TAB:
                turbo_mode = True

            if key:
                glyph = getattr(event, 'unicode', None)

                # is this a useful interpreter key?
                if not glyph or ord(glyph) > 256:
                    return event
            elif mouse:
                if event.button not in (4, 5):
                    return event
                glyph = None

            if turbo_mode:
                while self.auto_line:
                    self.current_line.append(self.auto_line.pop())
                turbo_mode = False
            # use auto key or user key?
            else:
                if self.auto_mode:
                    if self.auto_line:
                        glyph = self.auto_line.pop()
                        if glyph == '':
                            self.current_line.pop()
                            self.render_current_line()
                            return None
                    else:
                        return None
                if glyph:
                    self.current_line.append(glyph)
            self.render_current_line()
            return None

        return event

    def processLine(self, input):
        more = input.endswith('\\')
        if more:
            self.captured_input.append(input)
        else:
            # run the interpreter
            self.captured_input.append(input)
            input = '\n'.join(self.captured_input)
            # The interpreter does it's own output
            self.interpreter.runsource(input)
        return more

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
        super(BaseInterpreterPage, self).render(screen, deltat)


