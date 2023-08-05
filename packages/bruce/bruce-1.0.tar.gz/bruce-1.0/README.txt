
Bruce the Presentation Tool is for Python programmers who are tired of
fighting with presentation tools. In its basic form it allows text, code or
image pages and even interactive Python sessions. It uses PyGame and is
easily extensible to add new page types.


Usage
=====

Write your presentation as a Python module or package. Then:

  bruce-play <module name> [-win]

will import the presentation and attempt to access a function called
"pages" which it uses to get a sequence of pages to display. The "-win"
swtich runs the presentation in a window instead of full-screen.


Controls
========

left, right arrows
  Move back and forward pages (and expose/hide "-" marked text lines)
up, down arrows
  Move back and forward 5 pages (ignores expose/hide text lines)
control-I
  Enter / exit auto-type mode in the interactive interpreter
escape
  Exit presentation
home, end
  Go to the first or last page


Sample
======

This is a sample which includes use of all of the default page types::

    from bruce.text import TextPage
    from bruce.interp import InterpreterPage
    from bruce.scratch_interp import ScratchPadInterpreterPage
    from bruce.codefile import CodeFilePage
    from bruce.image import ImagePage

    opening_pages = '''
    =Games In Python

    MPUG, Sept 2005
    ---
    =How do you make a game?

    Control the screen & speakers
    -User interaction
    -World simulation
    '''

    def pages():
        l = []
        # some intro
        for page in opening_pages.split('---'):
            l.append(TextPage(page))

        l.append(InterpreterPage('Zen of Python', 'import this'))

    l.append(ScratchPadInterpreterPage('Draw to the Screen', '''
car = pygame.image.load('car.png')
car
scratch.blit(car, (100, 100))
rotated = pygame.transform.rotate(car, 45)
scratch.blit(rotated, (150, 150))
'''))

        l.append(CodeFilePage("Sample Game", 'car_game.py'))

        # examples
        l.extend([
            ImagePage("POWER CORE from PyWeek 1", 'powercore.png'),
            ImagePage("POWER CORE dev screenshot", 'lotsa_ufos.png'),
            ImagePage("Dynamite from PyWeek 1", 'dynamite.png'),
            ImagePage("Pylonoid from PyWeek 1", 'pylonoid.jpg'),
        ])
        l.append(TextPage('''=Questions?

    www.pygame.org
    pyopengl.sf.net
    home.gna.org/oomadness
    www.imitationpickles.org/pgu
    '''))
        return l

License
=======

Copyright (c) 2005 Richard Jones (richard at mechanicalcat)

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. The name of the author may not be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

