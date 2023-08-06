#! /usr/bin/env python
#
# $Id$

from distutils.core import setup

# perform the setup action
from bruce import __version__
setup(
    name = "bruce",
    version = __version__,
    description = "Bruce the Presentation Tool",
    long_description = '''Bruce the Presentation Tool is for
programmers who are tired of fighting with presentation tools. In its
basic form it allows text, code, image and video. It uses pyglet and
is easily extensible to add new page types.


Bruce 3.0 Features (this being the first 3.0 release)
=====================================================

- displays ReStructuredText content with one page per section or transition
- handling of *most* of ReStructuredText, including:

  * inline markup for emphasis, strong and literal
  * literal and line blocks
  * block quotes
  * definition, bullet and enumerated lists (including nesting)
  * images - inline and stand-alone, including scaling
  * page titles (section headings)

- page decorations
- scrolling of content larger than a screenful
- sensible resource location (images, video, sound from the same directory
  as the presentation file)
- and some extensions of ReST:

  * embedded Python interative interpreter sessions
  * videos (embedded just like images) with optional looping
  * stylsheet and decoration changes on the fly (eg. multiple fonts
    per page)

- timer and page count display for practicing
- may specify which screen to open on in multihead
- runs fullscreen at native resolution
- may switch to/from fullscreen quickly



Installation
============

Bruce REQUIRES Python 2.5 and pyglet Subversion r2093, or 1.1 *later than beta1*
when it's released.

To install Bruce, run::

    # python setup.py install



How to write presentations using Bruce the Presentation Tool
============================================================

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

and so on.
''',
    author = "Richard Jones",
    author_email = "richard@mechanicalcat.net",
    url = "http://r1chardj0n3s.googlepages.com/bruce",
    packages = ["bruce"],
    scripts = ['scripts/bruce'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
    ]
)

# vim: set filetype=python ts=4 sw=4 et si
