import pyglet
from bruce import page

class Resource(page.Page):

    @classmethod
    def as_page(cls, content, **kw):
        pyglet.resource.path.append(content.strip())
        pyglet.resource.reindex()
        return None

