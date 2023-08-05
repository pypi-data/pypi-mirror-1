import pygame, sys, code

from bruce.config import Config
from bruce.baseinterp import BaseInterpreterPage
from bruce.fonts import get_font
from pygame.locals import KEYUP

class Output:
    def __init__(self, method, realstdout):
        self.out = method
        self.realstdout = realstdout
        self.data = ''

    def write(self, data):
        self.data += data
        while '\n' in self.data:
            line, self.data = self.data.split('\n', 1)
            self.out(line)
        #print >>self.realstdout, "outputting %r"%(data)

class MyInterpreter(code.InteractiveInterpreter):
    def __init__(self, locals, method):
        self.outmethod = method
        code.InteractiveInterpreter.__init__(self, locals=locals)

    def execute(self, input):
        old_stdout = sys.stdout
        sys.stdout = Output(self.outmethod, old_stdout)
        more = self.runsource(input)
        sys.stdout = old_stdout
        return more

    def write(self, error):
        while '\n' in error:
            line, error = error.split('\n', 1)
            self.outmethod(line)

FONT_HEIGHT = 24
LINE_HEIGHT = FONT_HEIGHT + 2
fontmono = None
def init(force=False):
    global fontmono, fontBd, em
    if fontmono is not None and not force:
        return
    fontBd = get_font(Config.text_font, FONT_HEIGHT, bold=True)
    fontmono = get_font(Config.code_font, FONT_HEIGHT)
    em = fontmono.size('M')[0]
init()

class InterpreterPage(BaseInterpreterPage):
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
    def __init__(self, title='', text='', sysver=False, **kw):
        self.prompt = ">>> "
        self.prompt2 = "... "
        self.sysver = sysver
        super(InterpreterPage, self).__init__(title=title, text=text, **kw)

    def preamble(self):
        if self.sysver:
            for line in sys.version.splitlines():
                self.rendered_lines.append(fontmono.render(line, 1,
                    Config.text_fgcolour))

    def init(self, screen):
        self.interpreter = MyInterpreter({'pygame': pygame}, 
                                         self.renderOutputLine)
        super(InterpreterPage, self).init(screen)

    def processLine(self, input):
        # ignore key-up events (typically the next
        # event in the queue)
        if (input.startswith('pygame.event.wait()') or
                input.startswith('pygame.event.poll()')):
            pygame.event.set_blocked(KEYUP)

        if input == 'help()':
            input = 'print "help() not supported, sorry!"'

        # run the interpreter
        self.captured_input.append(input)
        input = '\n'.join(self.captured_input)
        more = self.interpreter.execute(input)

        if not more:
            self.captured_input = []

        if (input.startswith('pygame.event.wait()') or
                input.startswith('pygame.event.poll()')):
            pygame.event.set_allowed(KEYUP)
        return more

