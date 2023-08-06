The Title, Centered
-------------------

.. style::
   :layout.background_color: silver
   :layout.viewport: 0,64,w,h-(64+48)

.. layout::
   :image: pyglet-trans-64.png;halign=right;valign=bottom
   :quad: C#ffc0a0;V0,h;V0,h-48;Vw,h-48;Vw,h
   :quad: C#ffc0a0;V0,0;V0,64;Cblack;Vw,64;Vw,0

.. footer::
   a footer

Salmony bar at top behind title.

Silver background.

Salmony bar fading to black across the bottom, with logo on the right.

Also with a viewport to make sure we don't cover the bars.

(Try scrolling the text to make sure the viewport works)

Lorem ipsum dolor sit amet.

Consectetur adipisicing elit.

Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

Nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

Lorem ipsum dolor sit amet.

Consectetur adipisicing elit.

Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

Nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.


Title right-aligned
-------------------

.. style::
   :title.position: w,h
   :title.hanchor: right
   :title.vanchor: top
   :footer.position: w,0
   :footer.hanchor: right
   :footer.vanchor: bottom
   :footer.color: white

Title right-aligned, footer right-aligned


Title left-aligned
-------------------

.. style::
   :title.position: 0,h
   :title.hanchor: left
   :title.vanchor: top
   :footer.position: 0,0
   :footer.hanchor: left
   :footer.vanchor: bottom
   :footer.color: black

Title left-aligned, footer left-aligned


red to blue down
----------------

.. layout::
   :vgradient: red;blue

Content

red to blue across
------------------

.. layout::
   :hgradient: red;blue

Content

