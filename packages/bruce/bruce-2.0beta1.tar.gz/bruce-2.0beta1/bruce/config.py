import os

import pyglet

class _Section(object):
    '''Each page created will grab a _Section for itself which also
    takes a snapshot of the configuration at that point.
    '''
    def __init__(self, config, name):
        self.config = config.copy()
        self.name = name
    def __getitem__(self, label):
        k = '%s.%s'%(self.name, label)
        if k in self.config:
            return self.config[k]
        return self.config[label]

class _Config(dict):
    '''Store a set of defaults (defined here and in various page
    types and then per-presentation overrides.
    '''
    # XXX support custom fonts via pyglet.resource.add_font(filename)

    defaults = dict(
        bgcolor = (0, 0, 0, 255),
        charset = 'ascii',
        logo = None,
    )

    def set(self, key, val):
        if key in self:
            old = self[key]
            if isinstance(old, int):
                val = int(val)
            elif isinstance(old, float):
                val = float(val)
            elif isinstance(old, tuple):
                # a color
                val = tuple([int(x.strip())
                        for x in val.strip('()').split(',')])
                if len(val) < 4:
                    val += (255,)
            elif isinstance(old, basestring) or old is None:
                pass
            else:
                raise ValueError("don't understand old value type %r"%(old))
        self[key] = val

    def __contains__(self, key):
        return super(_Config, self).__contains__(key) or key in self.defaults

    def __getitem__(self, key):
        if super(_Config, self).__contains__(key):
            return super(_Config, self).__getitem__(key)
        return self.defaults[key]

    def get_section(self, name):
        return _Section(self, name)

    def add_section(self, name, options):
        for k in options:
            self.defaults['%s.%s'%(name, k)] = options[k]

    def copy(self):
        c = _Config()
        c.update(self)
        return c

    flags = tuple([(k, str, defaults[k]) for k in defaults])
    def as_page(self, content, **kw):
        for k in kw:
            if k in self.defaults:
                # exact match on the key
                self.set(k, kw[k])
            else:
                # otherwise match all sets with this key
                for d in self.defaults:
                    if '.' in d and d.split('.', 1)[1] == k:
                        self.set(d, kw[k])
        return None

    def as_html(self, content, **kw):
        # apply the config since we will need to know the correct charset
        # (etc?)
        self.as_page(content, **kw)
        return ''
        #l = ['<b>config section</b>']
        #l.extend('%s=%s'%i for i in kw.items())
        #return '<br>'.join(l)

# singleton
config = _Config()

# public API
get = config.get
set = config.set
add_section = config.add_section
get_section = config.get_section
path = os.path.abspath(os.path.join(os.getcwd(), __file__))

