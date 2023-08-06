import os

import pyglet
from pyglet import graphics
from pyglet import text
from pyglet import media
from pyglet import gl

from bruce import config
from bruce import page
from bruce import resource

class VideoPage(page.Page):
    config = (
        #('zoom', bool, False),
        ('title', str, ''),
        ('caption', str, ''),
        # only the following are configurable
        ('text.font_name', str, 'Arial'),
        ('text.font_size', float, 64),
        ('text.color', tuple, (255, 255, 255, 255)),
        ('title.font_name', str, 'Arial'),
        ('title.font_size', float, 64),
        ('title.color', tuple, (200, 255, 255, 255)),
    )
    name = 'video'

    @classmethod
    def as_html(cls, content, **flags):
        l = []
        if 'title' in flags:
            l.append('<b>%s</b>'%flags['title'])
        l.append('Video: %s'%page.decode_content(cls, content))
        if 'caption' in flags:
            l.append(flags['caption'])
        return '<br>'.join(l)

    title_label = caption_label = None
    def on_enter(self, vw, vh):
        super(VideoPage, self).on_enter(vw, vh)

        self.batch = graphics.Batch()

        # load the video source
        path = self.content.strip()
        if os.path.exists(path):
            source = pyglet.media.load(path)
        else:
            source = resource.loader.media(path)
        assert source.video_format
        video_format = source.video_format
        self.video_width = video_format.width
        self.video_height = video_format.height
        if video_format.sample_aspect > 1:
            self.video_width *= video_format.sample_aspect
        elif video_format.sample_aspect < 1:
            self.video_height /= video_format.sample_aspect

        # if we have a title then generate it
        if self.title:
            self.title_label = text.Label(self.title,
                font_name=self.cfg['title.font_name'],
                font_size=self.cfg['title.font_size'],
                color=self.cfg['title.color'],
                halign='center', valign='bottom', batch=self.batch)

        # if we have a captio then generate it
        if self.caption:
            self.caption_label = text.Label(self.caption,
                font_name=self.cfg['text.font_name'],
                font_size=self.cfg['text.font_size'],
                color=self.cfg['text.color'],
                halign='center', valign='bottom', batch=self.batch)

        # position all the elements
        self.on_resize(vw, vh)

        # create the player
        self.player = media.Player()
        self.player.queue(source)
        self.player.eos_action = self.player.EOS_PAUSE
        self.player.play()

    def on_resize(self, vw, vh):
        self.viewport_width, self.viewport_height = vw, vh

        # position the labels and adjust the available viewport height
        if self.title_label:
            self.title_label.x = vw//2
            self.title_label.y = vh = vh - self.title_label.content_height
        yoffset = 0
        if self.caption_label:
            self.caption_label.x = vw//2
            self.caption_label.y = 0
            vh -= self.caption_label.content_height
            # shift up to avoid the caption
            yoffset += self.caption_label.content_height

        w, h = self.video_width, self.video_height
        self.video_x, self.video_y = vw//2 - w//2, yoffset + (vh//2 - h//2)

        # determine whether we're scaling
        #if self.zoom or w > vw or h > vh:
        #    self.image.scale = min(vw / float(w), vh / float(h))

    def on_leave(self):
        self.image = None
        self.batch = None
        self.title_label = None
        self.caption_label = None

    def draw(self):
        self.batch.draw()

        # Video
        if self.player.source and self.player.source.video_format:
            self.player.texture.blit(self.video_x,
                                     self.video_y,
                                     width=self.video_width,
                                     height=self.video_height)

config.add_section('video', dict((k, v) for k, t, v in VideoPage.config[1:]))
