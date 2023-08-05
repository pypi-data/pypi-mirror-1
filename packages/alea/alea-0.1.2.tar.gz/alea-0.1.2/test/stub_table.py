# -*- coding: utf-8 -*-

# stub_table.py
# Part of alea, a library of random generators for games
#
# Copyright © 2007 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Stub objects for table classes
"""


class Stub_TableEntry(object):
    """ Stub object for TableEntry """

    def __init__(self, results, data):
        """ Set up a new instance """
        self.results = results
        self.data = data

class Stub_Table(object):
    """ Stub object for Table """

    def __init__(self, entries):
        """ Set up a new instance """
        self.entries = entries
        result_range = []
        for entry in self.entries:
            result_range.extend(entry.results)
        self.result_range = result_range

    def get_entry(self, result):
        """ Get an entry by result number """
        result_entry = None
        for entry in self.entries:
            if result in entry.results:
                result_entry = entry
        return result_entry
