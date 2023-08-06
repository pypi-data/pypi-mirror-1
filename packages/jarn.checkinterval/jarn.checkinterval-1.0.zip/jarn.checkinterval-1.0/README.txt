==================
jarn.checkinterval
==================
---------------------------------------------------
Compute optimal interpreter check interval for Zope
---------------------------------------------------

Computes the optimal interpreter check interval for the machine it is run on.
The formula is as follows::

    <result of pystone benchmark> / 50

Installation and use
====================

The checkinterval script must be installed into the Python interpreter used to
run Zope. This is most easily achieved by adding a part to your buildout.cfg::

    [buildout]
    parts = checkinterval

    [checkinterval]
    recipe = zc.recipe.egg
    eggs = jarn.checkinterval

After re-running buildout, type::

    $ ./bin/checkinterval
    1305

The number you see is the recommended check interval for this machine; put it
into your zope.conf file::

    python-check-interval 1305

Now restart Zope and bask in the glow.

Why care?
=========

The Python Library Reference on the topic of `check interval`_:
`"This integer value determines how often the interpreter checks for periodic
things such as thread switches and signal handlers. The default is 100,
meaning the check is performed every 100 Python virtual instructions.
Setting it to a larger value may increase performance for programs using
threads."`

Now, the Zope application server is such a program, and it benefits **greatly**
from setting the right check interval. If the value is too low, Zope
threads are interrupted unnecessarily, causing a noticable performance hit on
today's multi-cpu hardware.

Where's the 50 coming from?
===========================

The constant 50 in the formula was determined by benchmarks performed at Zope
Corporation and has become part of the "Zope lore" (See e.g.  this post by
`Matt Kromer`_). Going beyond pystone/50 produced no further benefits.

The value may well be meaningless for applications other than Zope and
platforms other than Intel.

Background
==========

More on check intervals and the GIL from `David Beazly`_.

For those back from the Beazly talk: Zope uses long running threads and
`asyncore`_, making it (more) independent from OS scheduling issues. Still,
the interruption argument holds.

.. _`check interval`: http://docs.python.org/library/sys.html#sys.setcheckinterval
.. _`Matt Kromer`: http://mail.zope.org/pipermail/zope/2002-June/116598.html
.. _`David Beazly`: http://www.dabeaz.com/python/GIL.pdf
.. _`asyncore`: http://docs.python.org/library/asyncore.html

