from pygame import locals as L

from bruce.config import Config
from bruce.page import Page
from bruce.fonts import get_font

class TextPage(Page):
    '''Displays some text centered on screen.

    The first line is always bolded.

    Obeys newlines.

    Lines starting withj '-' (dash) are initially hidden and are exposed
    or hidden with the left/right arrow keys. Modified arrow keys are
    ignored here, so will change pages.
    '''
    def __init__(self, text, **kw):
        self.width = 0
        self.height = 0
        self.lines = []
        self.hidden_lines = []
        self.text = text

        self.font_size = int(Config.get('text_font_size', 64))
        self.Fonts = { 
            '=': Config.get(('title_font', 'bold_font'), None),
            '*': Config.get(('bold_font', 'text_font'), None),
            ':': Config.get(('code_font', 'text_font'), None),
        }
        self.Colours = { 
            '=': Config.get(('title_fgcolour', 'bold_fgcolour'), None),
            '*': Config.get(('bold_fgcolour', 'text_fgcolour'), None),
            ':': Config.get(('code_fgcolour', 'text_fgcolour'), None),
        }
        self.bgcolour = Config.get('page_bgcolour')
        # default font, colour
        self.dfont = Config.get('text_font')
        self.dcolour = Config.get('text_fgcolour')
        super(TextPage, self).__init__(**kw)

    def init(self, screen):
        lines = []
        for line in self.text.splitlines():
            if line.startswith('#'): continue

            font = self.dfont
            colour = self.dcolour

            hidden = italic = False
            scale = 1
            while line and line[0] in '<>=:*-/\\':
                ch, line = line[0], line[1:]
                if ch == "\\":
                    break
                elif ch == "-":
                    hidden = True
                elif ch == "<":
                    scale *= 0.75
                elif ch == ">":
                    scale *= 1.33
                elif ch == "/":
                    italic = True
                else:
                    font = self.Fonts.get(ch) or font
                    colour = self.Colours.get(ch) or colour
            font_size = int(self.font_size*scale)
            # XXX support crappy bolding if no bold_font set 
            font = get_font(font, font_size, italic=italic)
            f = font.render(line, 1, colour)
            lines.append((f, hidden))

        # total height
        tHeight = (sum([x.get_size()[1] for x,h in lines]))

        sw, sh = screen.get_size()
        curypos = sh/2 - tHeight / 2
        for line, hidden in lines:
            lw, lh = line.get_size()
            xpos = sw/2 - lw/2
            if hidden:
                self.hidden_lines.append((line, (xpos, curypos)))
            else:
                self.lines.append((line, (xpos, curypos)))
            curypos += lh

        # so we can pop() lines off
        self.hidden_lines.reverse()
        self.popped_lines = []
        super(TextPage, self).init(screen)

    def handleEvent(self, event):
        if (event.type == L.KEYDOWN and 
                event.mod & (L.KMOD_SHIFT|L.KMOD_CTRL|L.KMOD_META|L.KMOD_ALT)):
            return event
        elif ((event.type == L.KEYDOWN and event.key == L.K_RIGHT) or
                    (event.type == L.MOUSEBUTTONDOWN and event.button == 1)):
            if not self.hidden_lines:
                return event
            line = self.hidden_lines.pop()
            self.popped_lines.append(line)
            self.lines.append(line)
            return None
        elif ((event.type == L.KEYDOWN and event.key == L.K_LEFT) or
                    (event.type == L.MOUSEBUTTONDOWN and event.button == 3)):
            if not self.popped_lines:
                return event
            line = self.popped_lines.pop()
            self.lines.pop()
            self.hidden_lines.append(line)
            return None
        return event

    def render(self, screen, deltat):
        screen.fill(self.bgcolour)
        for line, pos in self.lines:
            screen.blit(line, pos)
        super(TextPage, self).render(screen, deltat)
