import os

path = os.path.abspath(os.path.join(os.getcwd(), __file__))

class Config(object):
    # colour specifications
    page_bgcolour = (0, 0, 0)
    text_fgcolour = (255, 255, 255)
    title_fgcolour = (255, 55, 55)      # kinda red-pink-ish
    code_bgcolour = (20, 20, 20)
    code_fgcolour = (0, 255, 0)
    code_hilitecolour = (255, 255, 255)
    cursor_fgcolour = (200, 200, 255)
    interp_font_size = 24
    codefile_font_size = 24

    # fonts may be a list of system font names or a font file name
    text_font_size = 64
    text_font = 'Vera,Helvetica,Arial'
    title_font = 'Vera,Helvetica,Arial'
    code_font = 'VeraMono,Monaco'       # (Monaco is an Apple font)
    # if not defined, we use the above text_font system font with bold=True
    bold_font = None

    def __init__(self):
        raise RuntimeError("dont instantiate Config, fool!")

    def set(cls, key, val):
        if hasattr(cls, key):
            old = getattr(cls, key)
            if isinstance(old, int):
                val = int(val)
            elif isinstance(old, float):
                val = float(val)
            elif isinstance(old, tuple):
                # a colour
                val = tuple([int(x.strip()) 
                        for x in val.strip('()').split(',')])
            elif isinstance(old, basestring) or old is None:
                pass
            else:
                raise ValueError("dont understand old value type %r"%(old))
        setattr(cls, key, val)
    set = classmethod(set)

    def get(cls, key, dflt=None):
        """ get(key, default)
            key can be a string, or a sequence of strings, in which
            case first one wins. default is returned if none match.
        """
        if isinstance(key, basestring):
            key = [key]
        for k in key:
            if hasattr(cls, k):
                return getattr(cls, k)
            else:
                return dflt
    get = classmethod(get)

    def getfont(cls, key, size, dflt=None):
        """ getfont(key, size, default)
            key can be a string, or a sequence of strings, in which
            case first one wins. default is returned if none match.
            returns a font object or default or None
        """
        from bruce.fonts import get_font
        f = cls.get(key, dflt)
        if f:
            f = get_font(f, size)
        return f
    getfont = classmethod(getfont)
        
