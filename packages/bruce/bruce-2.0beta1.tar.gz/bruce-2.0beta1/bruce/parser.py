class ParseError(Exception):
    def __init__(self, number, error):
        super(ParseError, self).__init__('line %d: %s'%(number, error))

def parse(text, html=False):
    from bruce.presentation import Presentation

    klass = None
    pages = []
    content = []
    notes = []
    all = []
    for n, line in enumerate(text.splitlines()):
        all.append(line)
        if line.startswith('#'):
            notes.append(line[1:].strip())
            continue

        if line.startswith('--- '):
            first = all[-1]
            all[:] = all[:-1]
            if klass is not None:
                try:
                    content = '\n'.join(content).strip()
                    if html:
                        obj = (klass.as_html(content, **flags), notes)
                    else:
                        obj = klass.as_page(content, **flags)
                except ValueError, error:
                    raise ParseError(N, str(error))
                klass = None
                if obj:
                    pages.append(obj)
            N = n
            all = [first]
            flags = dict(source=all)
            content = []
            notes = []

            name = line[4:]
            if ' ' in name:
                name, content = name.split(' ', 1)
                content = [content.strip()]
            if name not in _classes:
                raise ParseError(N, '%s not a registered page type'%name)
            klass = _classes[name]
        elif line.startswith('  '):
            if '=' in line:
                name, value = line.split('=', 1)
                flags[name.strip()] = value.strip()
            else:
                flags[line.strip()] = True
        else:
            content.append(line.strip())

    if klass is not None:
        try:
            content = '\n'.join(content)
            if html:
                obj = (klass.as_html(content, **flags), notes)
            else:
                obj = klass.as_page(content, **flags)
        except ValueError, error:
            raise ParseError(N, str(error))
        if obj:
            pages.append(obj)

    return pages

from bruce import config
from bruce.text import TextPage
from bruce.code import CodePage
from bruce.resource import Resource
from bruce.image import ImagePage
from bruce.video import VideoPage
from bruce.html import HTMLTextPage
from bruce.blank import BlankPage
from bruce.python_interpreter import PythonInterpreterPage
_classes = dict(config=config.config, text=TextPage, html=HTMLTextPage,
    image=ImagePage, resource=Resource, video=VideoPage,
    code=CodePage, py=PythonInterpreterPage, blank=BlankPage)
def register(name, klass):
    if name in _classes:
        raise KeyError('%s already registered!'%name)
    _classes[name] = klass

__all__ = 'parse ParseError register'.split()

