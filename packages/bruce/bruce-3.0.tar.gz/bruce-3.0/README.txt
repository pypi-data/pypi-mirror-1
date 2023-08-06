---------------------------
Bruce the Presentation Tool
---------------------------

Bruce, the Presentation Tool is for people who are tired of
fighting with presentation tools. Presentations are composed
(edited) in plain text files. It allows text, code, image,
interative Python sessions and video. It uses pyglet to render
in OpenGL.

Please REMOVE any previous installation of Bruce!

Changes in this release:

- add rendering of tables
- add "bullet mode" for faster presentation styles
- add support for Pygments code colorisation
- add code block for displaying code blocks
- add blank page marker
- pop up a simple GUI when no command-line args given
- fix page number in window title
- set the clear color to the layout bgcolor
- generate warnings when unhandled docutils features are encountered
- handle doctest


Bruce, the Presentation Tool version 3.0 Features
=================================================

- displays ReStructuredText content with one page per section or transition
- has a "bullet mode" which displays one page per *bullet point*
- handling of *most* of ReStructuredText, including:

  * inline markup for emphasis, strong and literal
  * literal and line blocks
  * tables
  * block quotes
  * definition, bullet and enumerated lists (including nesting)
  * images - inline and stand-alone, including scaling
  * page titles (section headings)

- page layout and decorations
- scrolling of content larger than a screenful
- sensible resource location (images, video, sound from the same directory
  as the presentation file)
- and some extensions of ReST:

  * embedded Python interative interpreter sessions
  * videos (embedded just like images) with optional looping
  * stylesheet and layout changes on the fly (eg. multiple fonts
    per page)
  * transitions between pages

- timer and page count display for practicing
- may specify which screen to open on in multihead
- runs fullscreen at native resolution
- may switch to/from fullscreen quickly



Installation
============

Please REMOVE any previous installation of Bruce!

Bruce REQUIRES:

- Python__ 2.5
- docutils__ 0.4.1 or later
- pyglet__ 1.1 beta 2 or later
- Cocos__ 0.3 rc0 or later

__ http://www.python.org/
__ http://docutils.sf.net/
__ http://pyglet.org/
__ http://cocos2d.org/

And you may also optionally install:

- Pygments__ 0.10 or later
- Tkinter for the GUI interface (Tkinter is usually bundled with Python)

__ http://pygments.org/

To install Bruce, run::

    # python setup.py install


How to use Bruce, the Presentation Tool
=======================================

To invoke bruce, run::

    % bruce [presentation source.txt]

With no command-line arguments Bruce will pop up a simple GUI.

There's a number of command-line controls - use ``bruce -h`` to
learn what they do.


Controls
========

left, right arrows; left, right mouse button; space bar (forward)
  Move back and forward pages.
page up, page down
  Move back and forward 5 pages.
mouse scroll wheel
  Scroll large page content. You may also drag the contents up or down
  by dragging a left mouse button press up and down the screen. If a
  page has an embedded Python Interpreter you may use the scroll-wheel
  to scroll its contents (when the mouse is over the interpreter).
  Clicking and dragging always scrolls the whole page.
control-F
  Switch between fullscreen and windowed mode
escape
  Exit presentation
home, end
  Go to the first or last page


How to write presentations using Bruce, the Presentation Tool
=============================================================

Bruce presentations are written as plain-text files in the
ReStructuredText format with some extensions. See the examples
folder \*.rst files for some samples, the simplest being
"simple.rst" which displays plain text sentences centered
on a white background (using the "big-centered" style)::

    .. load-style:: big-centered

    Text displayed centered on the default white background.

    ----

    A new page, separated from the previous using the four
    dashes.

    Ut enim ad minim veniam.

    A Page Title
    ------------

    Pages may optionally have titles which are displayed
    centered at the top by default.

and so on. For more information see the HOWTO__ at the Bruce
website (or bundled with the source) and the source examples
directory.

__ http://r1chardj0n3s.googlepages.com/howto


License
=======

Copyright (c) 2005-2008 Richard Jones <richard@mechanicalcat.net>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. The name of the author may not be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

