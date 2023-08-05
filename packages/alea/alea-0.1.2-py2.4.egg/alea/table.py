# -*- coding: utf-8 -*-

# table.py
# Part of alea, a library of random generators for games
#
# Copyright © 2007 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Implement tables for random results
"""


class TableResultSetError(AssertionError):
    """ Raised when result set does not match between dice and entries """

    def __init__(self, dice_results, entry_results):
        """ Set up a new instance """
        self.dice_results = dice_results
        self.entry_results = entry_results

    def __str__(self):
        return "Table result set mismatch: " \
            "dice range == %s, entry results == %s" % (
                self.dice_results, self.entry_results
            )


class TableEntry(object):
    """ Single entry on a table """

    def __init__(self, results, data):
        """ Set up a new instance """
        self.results = results
        self.data = data

    def __repr__(self):
        params = []
        params.append("results=%s" % self.results)
        params.append("data=%s" % self.data)
        repr_str = "TableEntry(%s)" % ", ".join(params)
        return repr_str


class Table(object):
    """ Table for determining results randomly """

    def __init__(self, entries, roller):
        """ Set up a new instance """
        self.entries = entries
        self.roller = roller

        entry_results = self._get_entry_result_list()
        dice_results = self.roller.total_range
        if not dice_results == entry_results:
            raise TableResultSetError(dice_results, entry_results)

    def __repr__(self):
        params = []
        params.append("entries=%s" % self.entries)
        params.append("roller=%s" % self.roller)
        repr_str = "Table(%s)" % ", ".join(params)
        return repr_str

    def _get_entry_result_list(self):
        results = []
        for entry in self.entries:
            results.extend(entry.results)
        results.sort()
        return results

    def get_entry(self, number):
        """ Get an entry by the result number """
        candidate_entries = (entry for entry in self.entries
                             if number in entry.results)
        try:
            entry = candidate_entries.next()
        except StopIteration:
            entry = None
        return entry

    def get_random_entry(self, roller=None):
        """ Get an entry by random result of the dice """
        if not roller:
            roller = self.roller
        result = roller.get_result()
        entry = self.get_entry(result.total())
        return result, entry
