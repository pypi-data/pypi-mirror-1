#! /usr/bin/python
# -*- coding: utf-8 -*-

# test_table.py
# Part of alea, a library of random generators for games
#
# Copyright © 2007 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Unit test for table module
"""

import unittest

import scaffold
from stub_die import Stub_Die, Stub_Roller
from stub_table import Stub_TableEntry, Stub_Table

import alea.table


class TableEntryFixture(object):
    """ Mix-in class for table entry fixtures """

    def setUp(self):
        """ Set up test fixtures """

        self.valid_entries = {
            'fine': dict(
                args = dict(
                    results = [1, 2],
                    data = {'description': "Clear skies"},
                ),
            ),
            'cloud': dict(
                args = dict(
                    results = [3, 4],
                    data = {'description': "Cloudy skies"},
                ),
            ),
            'rain': dict(
                args = dict(
                    results = [5, 6],
                    data = {'description': "Rain at times"},
                ),
            ),
        }

        for key, params in self.valid_entries.items():
            args = params['args']
            instance = alea.table.TableEntry(**args)
            params['instance'] = instance

class TableFixture(TableEntryFixture):
    """ Mix-in class for table fixtures """

    def setUp(self):
        """ Set up test fixtures """
        self.table_factory = alea.table.Table
        TableEntryFixture.setUp(self)

        d6 = Stub_Die(faces=range(1, 6+1))
        d10 = Stub_Die(faces=range(1, 10+1))

        self.rollers = {
            'd6': Stub_Roller(dice=[d6]),
            'd10': Stub_Roller(dice=[d10]),
        }

        self.valid_tables = {
            'weather': dict(
                args = dict(
                    roller = self.rollers['d6'],
                    entries = [e['instance']
                               for e in self.valid_entries.values()
                    ],
                ),
            ),
        }

        for key, params in self.valid_tables.items():
            args = params['args']
            instance = alea.table.Table(**args)
            params['instance'] = instance

        self.bad_range_tables = {
            'gaps': dict(
                args = dict(
                    roller = self.rollers['d10'],
                    entries = [],
                ),
                entry_params = [[1,2], [4,5], [9,10]],
            ),
            'short_low': dict(
                args = dict(
                    roller = self.rollers['d10'],
                    entries = [],
                ),
                entry_params = [[1,2,3], [4,5,6], [7,8,9]],
            ),
            'short_high': dict(
                args = dict(
                    roller = self.rollers['d10'],
                    entries = [],
                ),
                entry_params = [[2,3,4], [5,6,7], [8,9,10]],
            ),
            'long_low': dict(
                args = dict(
                    roller = self.rollers['d10'],
                    entries = [],
                ),
                entry_params = [[0,1,2,3,4], [5,6,7], [8,9,10]],
            ),
            'long_high': dict(
                args = dict(
                    roller = self.rollers['d10'],
                    entries = [],
                ),
                entry_params = [[1,2,3], [4,5,6,7], [8,9,10,11]],
            ),
            'overlap': dict(
                args = dict(
                    roller = self.rollers['d10'],
                    entries = [],
                ),
                entry_params = [[1,2,3,4], [4,5,6,7], [7,8,9,10]],
            ),
        }

        for key, params in self.bad_range_tables.items():
            args = params['args']
            entry_params = params['entry_params']
            entries = [Stub_TableEntry(results=r, data=None)
                       for r in entry_params]
            args['entries'] = entries


class Test_Exception(scaffold.Test_Exception):
    """ Test cases for module exception classes """

    def setUp(self):
        """ Set up test fixtures """
        self.valid_exceptions = {
            alea.table.TableResultSetError: dict(
                min_args = 2,
                types = [AssertionError],
            ),
        }

        scaffold.Test_Exception.setUp(self)


class Test_TableEntry(unittest.TestCase, TableEntryFixture):
    """ Test case for the TableEntry class """

    def setUp(self):
        """ Set up test fixtures """
        self.table_factory = Stub_Table
        TableEntryFixture.setUp(self)

        self.iterate_params = scaffold.make_params_iterator(
            default_params_dict = self.valid_entries
        )

    def test_repr(self):
        """ TableEntry should have useful string representation """
        for key, params in self.iterate_params():
            args = params['args']
            instance = params['instance']
            repr_str = repr(instance)
            self.failUnless(repr_str.startswith("TableEntry("))
            self.failUnless(repr_str.count(str(args['results'])))
            self.failUnless(repr_str.count(str(args['data'])))
            self.failUnless(repr_str.endswith(")"))

    def test_instance(self):
        """ TableEntry instance should be created """
        for key, params in self.iterate_params():
            instance = params['instance']
            self.failUnless(instance)

    def test_entry_data(self):
        """ TestEntry should have specified data object """
        for key, params in self.iterate_params():
            args = params['args']
            instance = params['instance']
            self.failUnlessEqual(args['data'], instance.data)


class Test_Table(unittest.TestCase, TableFixture):
    """ Test case for the Table class """

    def setUp(self):
        """ Set up test fixtures """
        TableFixture.setUp(self)

        self.iterate_params = scaffold.make_params_iterator(
            default_params_dict = self.valid_tables
        )

    def test_instance(self):
        """ Table instance should be created """
        for key, params in self.iterate_params():
            instance = params['instance']
            self.failUnless(instance)

    def test_repr(self):
        """ Table should have useful string representation """
        for key, params in self.iterate_params():
            args = params['args']
            instance = params['instance']
            repr_str = repr(instance)
            self.failUnless(repr_str.startswith("Table("))
            self.failUnless(repr_str.count("entries=%s" % args['entries']))
            self.failUnless(repr_str.count("roller=%s" % args['roller']))
            self.failUnless(repr_str.endswith(")"))

    def test_entries_equal(self):
        """ Table should have specified sequence of entries """
        for key, params in self.iterate_params():
            args = params['args']
            instance = params['instance']
            self.failUnlessEqual(args['entries'], instance.entries)

    def test_roller_equal(self):
        """ Table should have specified roll parameters """
        for key, params in self.iterate_params():
            args = params['args']
            roller = args['roller']
            instance = params['instance']
            self.failUnlessEqual(roller, instance.roller)

    def test_result_entry(self):
        """ Table should have an entry for each result in range """
        for key, params in self.iterate_params():
            args = params['args']
            roller = args['roller']
            total_range = roller.total_range
            instance = params['instance']
            for result in total_range:
                instance_entry = instance.get_entry(result)
                self.failUnless(instance_entry)

    def test_random_entry(self):
        """ Table should return a random entry """
        for key, params in self.iterate_params():
            args = params['args']
            entries = args['entries']
            roller = args['roller']
            instance = params['instance']
            loop_range = len(instance.roller.total_range) * 10
            for i in range(loop_range):
                result, entry = instance.get_random_entry()
                self.failUnless(
                    result.total() in roller.total_range,
                    msg = "%s not in %s" % (
                        result.total(), roller.total_range
                    )
                )
                self.failUnless(entry in entries,
                    msg = "%s not in %s" % (entry, entries)
                )

    def test_modified_random_entry(self):
        """ Table should return a modified random entry """
        for key, params in self.iterate_params():
            args = params['args']
            entries = args['entries']
            roller = args['roller']
            instance = params['instance']
            loop_range = range(
                len(roller.total_range) * 10
            )
            modifier_range = range(-20, +20)
            for modifier in modifier_range:
                modified_roller = roller
                modified_roller.modifier = modifier
                instance.roller = modified_roller
                for i in loop_range:
                    result, entry = instance.get_random_entry()
                    self.failUnless(
                        result.total() in modified_roller.total_range,
                        msg = "%s not in %s" % (
                            result.total(), modified_roller.total_range
                        )
                    )
                    self.failUnless(entry in entries,
                        msg = "%s not in %s" % (entry, entries)
                    )

    def test_restricted_random_entry(self):
        """ Table should return a random entry from restricted range """
        for key, params in self.iterate_params():
            args = params['args']
            entries = args['entries']
            roller = args['roller']
            instance = params['instance']
            instance_total_range = instance.roller.total_range
            loop_range = range(
                len(roller.total_range) * 10
            )
            limit_range = range(
                -(len(roller.total_range)-1),
                +(len(roller.total_range))
            )
            for limiter in limit_range:
                restricted_range = list(roller.total_range)
                if limiter < 0:
                    restricted_range = restricted_range[:limiter]
                else:
                    restricted_range = restricted_range[limiter:]
                restricted_entries = [e for e in entries
                    if set(restricted_range) & set(e.results)]
                limited_roller = Stub_Roller(
                    dice = roller.dice,
                    modifier = roller.modifier,
                    total_range = restricted_range,
                )
                for i in loop_range:
                    result, entry = instance.get_random_entry(
                        roller = limited_roller
                    )
                    self.failUnless(
                        result.total() in limited_roller.total_range,
                        msg = "%s not in %s" % (
                            result.total(), limited_roller.total_range
                        )
                    )
                    self.failUnless(entry in restricted_entries,
                        msg = "%s not in %s" % (
                            entry, restricted_entries
                        )
                    )


suite = scaffold.suite(__name__)

__main__ = scaffold.unittest_main

if __name__ == '__main__':
    import sys
    exitcode = __main__(sys.argv)
    sys.exit(exitcode)
