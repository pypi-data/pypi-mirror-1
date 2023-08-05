munepy - Yet another Python enum package
Copyright (C) 2004-2007 Barry A. Warsaw
Licensed under the GNU Public License (see gnu-COPYING_GPL)

Introduction
============

This package is called `munepy`.  It is yet another Python enum package, but
with a slightly different take on syntax and semantics than earlier such
packages.

The goals of munepy were to produce simple, specific, concise semantics in an
easy to read and write syntax.  munepy has just enough of the features needed
to make Enums useful, but without a lot of extra baggage to weigh them down.
This work grew out of the Mailman 3.0 project and it is the enum package used
there.

The name `munepy` is a play on words.  *mune* is *enum* backwards, and *py* is
a common suffix for Python code.  *munepy* is pronounced exactly the same as
the delicious round chocolaty (if appearance indicates) pastry Moon Pie, which
is best when consumed with an RC cola.

Why another Python enum implementation?  'Cause I like mine better. :)


Requirements
============

munepy requires Python 2.4 or newer.  It might even work with Python 2.3 but I
don't regularly test it.  Optionally, the nose package is used if you want to
run the package's test suite.  You do not need nose to use munepy -- in fact
you need nothing other than Python.


Documentation
=============

All documentation is in the form of doctests.  Because the package is so
simple to use, the doctests should allow you to get started using munepy enums
in about 5 minutes.

See munepy/tests/test_enum.txt for details.


Project details
===============

The project home page is:

    http://launchpad.net/munepy

You may download and the latest version of the package from the Python
Cheeseshop.  See http://cheeseshop.python.org for details.

Or, if you have ez_install installed, you can just do the following:

    % sudo easy_install munepy

You can grab the latest development copy of the code using Bazaar, from the
Launchpad home page above.  See http://bazaar-vcs.org for details on the
Bazaar distributed revision control system.  If you have Bazaar installed, you
can grab your own branch of the code like this:

     bzr branch sftp://bazaar.launchpad.net/~barry/munepy/trunk munepy

You may contact the author via barry@python.org.  You may get an automatic
response if this is the first time you have emailed me.  Don't worry, I
will have received your email regardless.

All bug reporting should use the Launchpad site mentioned above.
