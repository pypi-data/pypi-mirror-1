from __future__ import absolute_import
import sys
import os
import code

import pyglet
from pyglet import graphics
from pyglet import text
from pyglet.text import caret, document, layout

from bruce import config
from bruce import page

class Output:
    def __init__(self, display, realstdout):
        self.out = display
        self.realstdout = realstdout
        self.data = ''

    def write(self, data):
        self.out(data)

class MyInterpreter(code.InteractiveInterpreter):
    def __init__(self, locals, display):
        self.write = display
        code.InteractiveInterpreter.__init__(self, locals=locals)

    def execute(self, input):
        old_stdout = sys.stdout
        sys.stdout = Output(self.write, old_stdout)
        more = self.runsource(input)
        sys.stdout = old_stdout
        return more

class PythonInterpreterPage(page.ScrollableLayoutPage):
    '''Runs an interactive Python interpreter.
    '''
    flags = (
        ('title', str, ''),
        ('sysver', bool, False),
        ('auto', bool, False),
    )
    name = 'py'

    prompt = ">>> "
    prompt_more = "... "

    def __init__(self, content, **kw):
        super(PythonInterpreterPage, self).__init__(content, **kw)

        self.interpreter = MyInterpreter({}, self._write)

        self.current_input = []

        self.history = ['']
        self.history_pos = 0

        assert self.auto is False, 'not implemented yet'

    @classmethod
    def as_html(cls, content, **flags):
        '''Invoked to generate the HTML version of the presentation.
        '''
        if not content:
            return 'python interpreter'
        content = decode_content(cls, content)
        return '<pre>%s</pre>'%html_quote(content)

    def on_enter(self, vw, vh):
        content = self.prompt

        if self.sysver:
            content = sys.version + '\n' + content

        # format the code
        self.document = document.FormattedDocument(content)
        self.document.set_style(0, len(self.document.text), {
            'font_name': self.cfg['code.font_name'],
            'font_size': self.cfg['code.font_size'],
            'color': self.cfg['code.color'],
        })

        self.batch = graphics.Batch()

        if self.title:
            x = vw//2
            l = self.label = text.Label(self.title,
                font_name=self.cfg['title.font_name'],
                font_size=self.cfg['title.font_size'],
                color=self.cfg['title.color'],
                halign='center', valign='bottom', batch=self.batch, x=x)
            l.y = vh = vh - l.content_height

        # generate the document
        self.layout = layout.IncrementalTextLayout(self.document,
            vw, vh, multiline=True, batch=self.batch)
        self.layout.valign = 'top'
        self.layout.y = vh

        self.caret = caret.Caret(self.layout, color=self.cfg['caret.color'])
        self.caret.position = len(self.document.text)
        self.caret.on_activate()

        self.start_of_line = len(self.document.text)

    def on_resize(self, vw, vh):
        super(PythonInterpreterPage, self).on_resize(vw, vh)
        self.caret.position = len(self.document.text)

    def on_leave(self):
        self.document = None
        self.label = None
        self.layout = None
        self.batch = None
        self.caret = None

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.TAB:
            return self.caret.on_text('\t')
        elif symbol in (pyglet.window.key.ENTER, pyglet.window.key.NUM_ENTER):
            # write the newline
            self._write('\n')

            line = self.document.text[self.start_of_line:]
            if line == 'help()':
                line = 'print "help() not supported, sorry!"'
            self.current_input.append(line)
            self.history_pos = len(self.history)
            self.history[self.history_pos-1] = line.strip()
            self.history.append('')
            more = self.interpreter.execute('\n'.join(self.current_input))
            if not more:
                self.current_input = []
                self._write(self.prompt)
            else:
                self._write(self.prompt_more)
            self.start_of_line = len(self.document.text)
        elif symbol == pyglet.window.key.SPACE:
            pass
        else:
            return pyglet.event.EVENT_UNHANDLED
        return pyglet.event.EVENT_HANDLED

    def on_text(self, symbol):
        # squash carriage return - we already handle them above
        if symbol == '\r':
            return pyglet.event.EVENT_HANDLED

        self._scroll_to_bottom()
        return self.caret.on_text(symbol)

    def on_text_motion(self, motion):
        at_sol = self.caret.position == self.start_of_line

        if motion == pyglet.window.key.MOTION_UP:
            # move backward in history, storing the current line of input
            # if we're at the very end of time
            line = self.document.text[self.start_of_line:]
            if self.history_pos == len(self.history)-1:
                self.history[self.history_pos] = line
            self.history_pos = max(0, self.history_pos-1)
            self.document.delete_text(self.start_of_line,
                len(self.document.text))
            self._write(self.history[self.history_pos])
        elif motion == pyglet.window.key.MOTION_DOWN:
            # move forward in the history
            self.history_pos = min(len(self.history)-1, self.history_pos+1)
            self.document.delete_text(self.start_of_line,
                len(self.document.text))
            self._write(self.history[self.history_pos])
        elif motion == pyglet.window.key.MOTION_BACKSPACE:
            # can't delete the prompt
            if not at_sol:
                return self.caret.on_text_motion(motion)
        elif motion == pyglet.window.key.MOTION_LEFT:
            # can't move back beyond start of line
            if not at_sol:
                return self.caret.on_text_motion(motion)
        elif motion == pyglet.window.key.MOTION_PREVIOUS_WORD:
            # can't move back word beyond start of line
            if not at_sol:
                return self.caret.on_text_motion(motion)
        else:
            return self.caret.on_text_motion(motion)
        return pyglet.event.EVENT_HANDLED

    def _write(self, s):
        self.document.insert_text(len(self.document.text), s, {
            'font_name': self.cfg['code.font_name'],
            'font_size': self.cfg['code.font_size'],
            'color': self.cfg['code.color'],
        })
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        # on key press always move the view to the bottom of the screen
        if self.layout.height < self.layout.content_height:
            self.layout.valign = 'bottom'
            self.layout.y = 0
            self.layout.view_y = 0
        self.caret.position = len(self.document.text)

    def draw(self):
        self.batch.draw()

config.add_section('py', {
    'title.font_name': 'Arial',
    'title.font_size': 64,
    'title.color': (200, 255, 255, 255),
    # fits 80 columns across 1024 pixels
    'code.font_name': 'Courier New',
    'code.font_size': 20,
    'code.color': (200, 200, 200, 255),
    'caret.color': (200, 200, 200),
})

