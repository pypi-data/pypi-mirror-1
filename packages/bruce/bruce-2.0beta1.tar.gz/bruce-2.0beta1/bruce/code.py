import os

import pyglet
from pyglet import graphics
from pyglet import text
from pyglet.text import document, layout

from bruce import config
from bruce import page

class CodePage(page.ScrollableLayoutPage):
    '''Displays some code from a file.
    '''
    flags = (
        ('title', str, ''),
    )
    name = 'code'

    def __init__(self, content, **kw):
        super(CodePage, self).__init__(content, **kw)
        self.cfg = config.get_section('code')

        # load the file content
        f = pyglet.resource.file(self.content.strip())
        try:
            self.file_content = f.read().decode(self.cfg['charset'])
        finally:
            f.close()

        # XXX put up a background too

    label = None
    def on_enter(self, vw, vh):
        # format the code
        self.document = document.FormattedDocument(self.file_content)
        self.document.set_style(0, len(self.file_content), {
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
        self.layout.y = vh
        self.layout.valign = 'top'

    def on_leave(self):
        self.document = None
        self.label = None
        self.layout = None
        self.batch = None

    def draw(self):
        self.batch.draw()

config.add_section('code', {
    'title.font_name': 'Arial',
    'title.font_size': 64,
    'title.color': (200, 255, 255, 255),
    # fits 80 columns across 1024 pixels
    'code.font_name': 'Courier New',
    'code.font_size': 20,
    'code.color': (200, 255, 200, 255),
})

