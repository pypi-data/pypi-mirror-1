#! /usr/bin/env python
#
# $Id$

import os
from distutils.core import setup

# perform the setup action
from bruce import __version__
setup(
    name = "bruce",
    version = __version__,
    description = "Bruce the Presentation Tool",
    long_description = '''Bruce the Presentation Tool is for Python
programmers who are tired of fighting with presentation tools. In its
basic form it allows text, code or image pages and even interactive
Python sessions. It uses PyGame and is easily extensible to add new
page types.


1.2.1 - 2007-01-04

- moved some of the smaller examples into doc/examples
- fix ScratchPad page (thanks Dave Cole)


1.2 - 2007-01-02

- added control-F to switch between fullscreen and windowed mode (X11 only)
- added ShellInterpreterPage and SpawnPage (thanks Anthony Baxter)
- added socrates.py driver script - see doc/socrates.txt for more
- many, many new features added - highlighting of code pages, timed 
  auto-advancing of pages, simple syntax for text page effects, autotyping
  enhancements... much more. See doc/socrates.txt for more.

''',
    author = "Richard Jones",
    author_email = "richard@mechanicalcat.net",
    url = "http://bruce.python-hosting.com/",
    packages = ["bruce"],
    scripts = ["socrates.py"],
    requires = ["pygame (>1.6)"],
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
