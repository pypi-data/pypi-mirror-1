
Bruce the Presentation Tool is for Python programmers who are tired of
fighting with presentation tools. In its basic form it allows text, code or
image pages and even interactive Python sessions. It uses PyGame and is
easily extensible to add new page types.


Installation
============

To install Bruce, run::

    python setup.py install

if you're running Python < 2.5 then you will receive a message like::

    UserWarning: Unknown distribution option: 'requires'

which you may ignore.


Usage
=====

Write your presentation as a Python script which imports "bruce.main" and
calls "bruce.main.main(pages)" where "pages" is a sequence of
bruce.page.Page objects. Then::

  python <presentation file> [-fs]

will run the presentation.

The "-fs" swtich runs the presentation full-screen instead of in a window.


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


Samples
=======

See the examples in the Subversion repository at:

  http://bruce.python-hosting.com/browser/

in particular the simple:

  http://bruce.python-hosting.com/file/trunk/examples/example.py

Note that both examples specify explicit fonts from the Vera family. I
recommend you do the same as pygame's SystemFont can produce unpredictable
and sometimes ugly results.


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

