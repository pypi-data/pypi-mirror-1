#!/usr/bin/python
from bruce.config import Config

import bruce.main
from bruce.pages import *

def highlightCodePage(pages, title, filename, **kw):
    titles = [ line for line in open(filename, 'r')
        if line.strip().startswith('#=') ]
    tokens = [ l.split(' ', 1)[0][2:].strip() for l in titles]
    tokens.sort()
    if not tokens:
        tokens = ['00']
    for t in tokens:
        pages.append(CodeFilePage(title, filename, highlight=t, **kw))

class Directive:
    def __init__(self, directive, dirname, Max):
        if len(directive) > len(dirname):
            S = directive[len(dirname)]
            self.items = [x for x in directive.strip().split(S)[:Max]]
        else:
            self.items = []
        if len(self.items) < Max:
            self.items += [''] * (Max-len(self.items))
    def __iter__(self):
        return iter(self.items)

def parseFlags(flags):
    """ Takes a string of form 'FOO BAR=BAZ BOO' and 
        returns { 'FOO': True, 'BAR': 'BAZ', 'BOO': True }
    """
    # Woo one-liners FTW
    return dict([(f.split('=', 1) + [True])[:2] for f in flags.split()])
    
def genPages(filename):
    pages = []
    P = pages.append

    pagedata = ''.join(open(filename).readlines())
    for pagenum, page in enumerate(pagedata.split('---\n')):
        #print pagenum
        kw = {}
        if page[-1] == '\n': page = page[:-1]
        if page.startswith('!'): # Non TextPage
            page = page[1:]
            if page.startswith('IMG'):
                typ, imgfile, imgtitle, flags = Directive(page, 'IMG', 4)
                flags = parseFlags(flags)
                kw = { 'nofooter': 'NOFOOTER' in flags, }
                if 'AUTO' in flags:
                    timer = float(flags.get('AUTO', 0))
                    P(AutoImagePage(imgtitle.strip(), imgfile.strip(), 
                                                        timer=timer, **kw),)
                else:
                    P(ImagePage(imgtitle.strip(), imgfile.strip(), **kw))
            elif page.startswith('CODE'):
                typ, codefile, codetitle, flags = Directive(page, 'CODE', 4) 
                flags = parseFlags(flags)
                kw= {
                        'skiphashbang': 'SKIPHASHBANG' in flags,
                        'nofooter': 'NOFOOTER' in flags,
                    }
                if 'HILITE' in flags:
                    highlightCodePage(pages, codetitle, codefile, **kw)
                elif 'AUTO' in flags:
                    timer = float(flags.get('AUTO', 0))
                    P(AutoCodeFilePage(codetitle, codefile, timer=timer, **kw))
                else:
                    P(CodeFilePage(codetitle, codefile, **kw))
            elif page.startswith('PY'):
                dirline, commands = page.split('\n', 1)
                typ, title, flags = Directive(dirline, 'PY', 3)
                flags = parseFlags(flags)
                P(InterpreterPage(title=title, text=commands, 
                                    sysver=flags.get('SYSVER', False), 
                                    auto_mode=('AUTO' in flags)))
            elif page.startswith('SPAWN'):
                typ, command, flags = Directive(page, 'SPAWN', 3)
                P(SpawnPage(command, 
                                pause=('PAUSE' in flags), 
                                repeat=('REPEAT' in flags)))
            elif page.startswith('SHELL'):
                dirline, commands = page.split('\n', 1)
                typ, title, prompt, flags = Directive(dirline, 'SHELL', 4)
                P(ShellInterpreterPage(title=title, text=commands, 
                    prompt=prompt, auto_mode=('AUTO' in flags)))
            elif page.startswith('TEXT'):
                dirline, page = page.split('\n', 1)
                typ, flags = Directive(dirline, 'TEXT', 2)
                flags = parseFlags(flags)
                kw = { 
                        'nofooter': 'NOFOOTER' in flags,
                     }
                if 'UNICODE' in flags:
                    page = page.decode('utf-8')
                if 'AUTO' in flags:
                    timer = float(flags.get('AUTO', 0))
                    P(AutoTextPage(page, timer=timer, **kw),)
                else:
                    P(TextPage(page, **kw))
            elif page.startswith('CONFIG'):
                dirline, conf = page.split('\n', 1)
                parseConfig(conf)
                reinitPageConfig()
            elif page.startswith('IGNORE') or page.startswith('COMMENT'):
                continue
            elif page.startswith('STOP'):
                break
            else: 
                raise ValueError("unknown directive in line: %r"%(page))
        else:
            # no leading directive, defaults to !TEXT (no flags)
            P(TextPage(page))
    return pages

def parseConfig(text):
    for n, v in [item.strip().split('=', 1) 
                for item in text.split('\n') 
                if not item.startswith('#')]:
        Config.set(n.strip(), v.strip())
        #print "setting", n, "to", v, "result", Config.get(n)


def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--fullscreen", dest="fullscreen",
                      action="store_true", default=False,
                      help="run in fullscreen mode")
    parser.add_option("-t", "--timer", dest="timer",
                      action="store_true", default=False,
                      help="display a timer")
    parser.add_option("-p", "--pagecount", dest="pageCount",
                      action="store_true", default=False,
                      help="display page numbers")
    parser.add_option("-s", "--startpage", dest="startpage",
                      default="1",
                      help="start at page N (default 1)")

    (options, args) = parser.parse_args()
    pages = genPages(args[0])
    bruce.main.options = options
    bruce.main.main(pages, fullscreen=options.fullscreen, 
                            startpage=options.startpage)
    

if __name__ == "__main__":
    main()
