import os

from bruce import config
from bruce import page

class BlankPage(page.Page):
    flags = ()
    name = 'blank'

    @classmethod
    def as_html(cls, content, **flags):
        return ''

    def draw(self):
        pass

#config.add_section('blank', {})
