from bruce.config import Config
from bruce.fonts import get_font
from bruce.shell import MyInterpreter
from bruce.baseinterp import BaseInterpreterPage

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

class ShellInterpreterPage(BaseInterpreterPage):
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

    def __init__(self, title='', text='', prompt="% ", **kw):
        self.prompt = prompt
        self.prompt2 = '> '
        super(ShellInterpreterPage, self).__init__(title=title, text=text, 
                                                   **kw)

    def preamble(self): 
        pass

    def init(self, screen):
        self.interpreter = MyInterpreter(self.renderOutputLine)
        super(ShellInterpreterPage, self).init(screen)

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



