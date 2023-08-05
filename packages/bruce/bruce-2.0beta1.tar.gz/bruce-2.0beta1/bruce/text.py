import pyglet
from pyglet import graphics
from pyglet.text import document, layout

from bruce import config
from bruce import page

class TextPage(page.Page):
    '''Displays some text centered on screen.

    Lines can start with one or more special characters. These include:

    . # line is ignored
    . - "hidden". Each 'next' will display another hidden line.
    . = display as a title
    . * display in bold
    . < or > smaller or bigger (can have multiple)
    . : display in codefont (fixed width)
    . / display line in italics
    . \ no more special characters will be parsed on this line

    For example::

       ..text
       =The Page Title
       *a bold thing*
       -<<*a smaller bold thing not displayed immediately*
    '''
    name = 'text'

    def on_enter(self, vw, vh):
        content = []
        styles = []
        n = 0
        self.blocks = []
        self.exposed = 0
        for line in self.content.splitlines():
            if line.startswith('#'): continue

            # set up style defaults
            style = dict(font_name=self.cfg['text.font_name'],
                font_size=self.cfg['text.font_size'],
                color=self.cfg['text.color'])

            # handle styling prefix
            hide = False
            while line and line[0] in '<>=:*-/\\':
                ch, line = line[0], line[1:]
                if ch == "\\":
                    break
                elif ch == "-":
                    # XXX start and end for *block* not single line
                    hide = True
                elif ch == "<":
                    style['font_size'] *= 0.75
                elif ch == ">":
                    style['font_size'] *= 1.33
                elif ch == "/":
                    style['italic'] = True
                elif ch == "*":
                    style['bold'] = True
                elif ch == '=':
                    style['font_name'] = self.cfg['title.font_name']
                    style['font_size'] = self.cfg['title.font_size']
                    style['color'] = self.cfg['title.color']
                elif ch == ':':
                    style['font_name'] = self.cfg['code.font_name']
                    style['font_size'] = self.cfg['code.font_size']
                    style['color'] = self.cfg['code.color']
            if hide:
                color = style['color']
                self.blocks.append((n, n+len(line), color))
                style['color'] = color[:3] + (0,)
            styles.append((n, n + len(line), style))
            n += len(line) + 1
            content.append(line)

        content = '\n'.join(content)
        self.document = document.FormattedDocument(content)
        for s, e, attrs in styles:
            self.document.set_style(s, e, attrs)
        self.document.set_style(0, len(content), {'align': 'center'})

        # render the text lines to our batch
        self.batch = graphics.Batch()
        self.layout = layout.IncrementalTextLayout(self.document,
            vw, vh, multiline=True, batch=self.batch)
        self.layout.valign='center'
        self.layout.y = vh//2

    def on_next(self):
        if self.exposed == len(self.blocks):
            return False
        s, e, color = self.blocks[self.exposed]
        self.document.set_style(s, e, {'color': color[:3] + (255,)})
        self.exposed += 1
        return True

    def on_previous(self):
        if self.exposed == 0:
            return False
        self.exposed -= 1
        s, e, color = self.blocks[self.exposed]
        self.document.set_style(s, e, {'color': color[:3] + (0,)})
        return True

    def on_leave(self):
        self.document = None
        self.layout = None
        self.batch = None

    def draw(self):
        self.batch.draw()

config.add_section('text', {
    'text.font_name': 'Arial',
    'text.font_size': 64,
    'text.color': (255, 255, 255, 255),
    'title.font_name': 'Arial',
    'title.font_size': 64,
    'title.color': (200, 255, 255, 255),
    'code.font_name': 'Courier New',
    'code.font_size': 64,
    'code.color': (200, 200, 200, 255),
})

