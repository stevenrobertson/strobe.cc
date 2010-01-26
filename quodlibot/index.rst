Quodlibot, a Google Code IRC bot
================================

:Author: Steven Robertson
:Contact: steven@strobe.cc
:Published: 2009-12-26
:Tags: Web

I was looking for a simple IRC bot which would announce changes to the `Quod
Libet`_ project, like what CIA_ does for version control. Finding none, I
hacked one together in about an hour, using Twisted_ and `Feed Parser`_. It's
trivial, but code that isn't shared is lost, and it may save a few others some
time in the future. If you maintain a GC project and want me to host an
instance of the bot, send me an email.

.. _Quod Libet: http://code.google.com/p/quodlibet/
.. _CIA: http://cia.vc/
.. _Twisted: http://twistedmatrix.com/trac/
.. _Feed Parser: http://www.feedparser.org/

.. raw:: html

    quodlibot.py
    <a class="smallcaps" style="color: black;" href="quodlibot.py">(download)</a>

.. codefile:: quodlibot.py
    python

