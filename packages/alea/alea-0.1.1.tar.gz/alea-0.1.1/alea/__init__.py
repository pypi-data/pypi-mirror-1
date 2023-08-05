# -*- coding: utf-8 -*-

# __init__.py
# Part of alea, a library of random generators for games
#
# Copyright © 2007 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Random generators for games

This library provides implementations for random generators as found
in non-computer games.

Currently implemented:

* ``alea.die`` implements polyhedral dice with any set of faces, and
  allows rolling arbitrary sets of dice and optionally totalling
  numeric results

* ``alea.table`` implements look-up tables that can be associated with
  random generators to have random table entries generated directly.
"""

__version__ = "0.1.1"
__date__ = "2007-07-12"
__author_name__ = "Ben Finney"
__author_email__ = "ben+python@benfinney.id.au"
__author__ = "%s <%s>" % (__author_name__, __author_email__)
__copyright__ = "Copyright © %s %s" % (
    __date__.split('-')[0], __author_name__
)
__license__ = "GPL"
__url__ = "http://cheeseshop.python.org/pypi/alea/"
