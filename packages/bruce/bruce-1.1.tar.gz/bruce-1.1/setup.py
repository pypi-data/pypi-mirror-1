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

Changes in 1.1:

- Cleaned up configuration of fonts (now use SystemFont by default, but
  presentations may code in direct paths to fonts if they wish)
- Removed "data" from distribution and installation
- Moved examples into "examples" directory of the source repository
  http://bruce.python-hosting.com/browser/
- Removed "bruce-play" method of invoking presentations
''',
    author = "Richard Jones",
    author_email = "richard@mechanicalcat.net",
    url = "http://bruce.python-hosting.com/",
    packages = ["bruce"],
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
