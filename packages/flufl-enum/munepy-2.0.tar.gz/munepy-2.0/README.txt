========================================
munepy - Yet another Python enum package
========================================

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

Why another Python enumeration implementation?  'Cause I like mine better. :)


Requirements
============

munepy requires Python 2.6 or newer, and is compatible with Python 3 (when
used with 2to3).


Documentation
=============

All documentation is in the form of doctests.  Because the package is so
simple to use, the doctests should allow you to get started using munepy enums
in about 5 minutes.

See `munepy/docs/README.txt`_ for details.


Project details
===============

The project home page is:

    http://launchpad.net/munepy

You may download and the latest version of the package from the Python
Cheeseshop:

    http://pypi.python.org/pypi/munepy

You can of course just ez_install it::

    % sudo easy_install munepy

You can grab the latest development copy of the code using Bazaar, from the
Launchpad home page above.  See http://bazaar-vcs.org for details on the
Bazaar distributed revision control system.  If you have Bazaar installed, you
can grab your own branch of the code like this::

     bzr branch lp:munepy

You may contact the author via barry@python.org.

All bug reporting should use the Launchpad site mentioned above.


Copyright
=========

Copyright (C) 2004-2010 Barry A. Warsaw

This file is part of munepy.

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 2 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with this program; if not, write to the Free Software Foundation, Inc., 51
Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


.. _`munepy/docs/README.txt`: munepy/docs/README.html


Table of Contents
=================

.. toctree::

    munepy/docs/README.txt
