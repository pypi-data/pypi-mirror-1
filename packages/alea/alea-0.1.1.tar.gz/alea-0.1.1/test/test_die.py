#! /usr/bin/python
# -*- coding: utf-8 -*-

# test_die.py
# Part of alea, a library of random generators for games
#
# Copyright © 2007 Ben Finney <ben@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Unit test for die module
"""

import unittest

import scaffold
from stub_die import Stub_Die, Stub_Roller, Stub_RollResult

import alea.die


class DieFixture(object):
    """ Mix-in class for Die instance fixtures """

    def setUp(self):
        """ Set up test fixtures """
        self.valid_dice = {
            'd6': dict(
                args = dict(
                    faces = range(1, 7),
                ),
            ),
            'd20': dict(
                args = dict(
                    faces = range(1, 21),
                ),
            ),
            'odd_d6': dict(
                args = dict(
                    faces = range(1, (2*6)+1, 2),
                ),
            ),
            'colour_d6': dict(
                args = dict(
                    faces = ['red', 'orange', 'yellow',
                             'green', 'blue', 'violet',
                            ],
                ),
                is_numeric = False,
            ),
            'mixed_d6': dict(
                args = dict(
                    faces = [1, True, 'green', 4, -27, 15.3],
                ),
                is_numeric = False,
            ),
            'coin': dict(
                args = dict(
                    faces = ['head', 'tail'],
                ),
                is_numeric = False,
            ),
        }

        for key, params in self.valid_dice.items():
            args = params['args']
            instance = self.die_factory(**args)
            params['instance'] = instance

class RollerFixture(DieFixture):
    """ Mix-in class for Roller instance fixtures """

    def setUp(self):
        """ Set up test fixtures """
        DieFixture.setUp(self)

        d6 = self.valid_dice['d6']['instance']
        colour_d6 = self.valid_dice['colour_d6']['instance']

        self.valid_rollers = {
            'colour': dict(
                args = dict(
                    dice = [colour_d6],
                ),
                is_numeric = False,
            ),
            '1d6': dict(
                args = dict(dice = [d6],),
                modified_dice_range = range(1, 6+1),
            ),
            '1d6-7': dict(
                args = dict(dice = [d6], modifier = -7,),
                modified_dice_range = range(-6, -1+1),
            ),
            '1d6-2': dict(
                args = dict(dice = [d6], modifier = -2,),
                modified_dice_range = range(-1, 4+1),
            ),
            '1d6+2': dict(
                args = dict(dice = [d6], modifier = +2,),
                modified_dice_range = range(3, 8+1),
            ),
            '1d6+7': dict(
                args = dict(dice = [d6], modifier = +7,),
                modified_dice_range = range(8, 13+1),
            ),
            '3d6': dict(
                args = dict(dice = [d6]*3,),
                modified_dice_range = range(3, 18+1),
            ),
            '3d6+2': dict(
                args = dict(dice = [d6]*3, modifier = +2,),
                modified_dice_range = range(5, 20+1),
            ),
            '3d6-1': dict(
                args = dict(dice = [d6]*3, modifier = -1,),
                modified_dice_range = range(2, 17+1),
            ),
            'weather': dict(
                args = dict(dice = [d6]*3,),
                modified_dice_range = range(3, 18+1),
            ),
            'bad-weather': dict(
                args = dict(dice = [d6]*3, modifier = -2,),
                modified_dice_range = range(1, 16+1),
            ),
            'good-weather': dict(
                args = dict(dice = [d6]*3, modifier = +2,),
                modified_dice_range = range(5, 20+1),
            ),
            'weather-no-rain': dict(
                args = dict(
                    dice = [d6]*3,
                    total_range = range(9, 18+1),
                ),
                modified_dice_range = range(3, 18+1),
            ),
            'weather-no-fine': dict(
                args = dict(
                    dice = [d6]*3,
                    total_range = range(3, 12+1),
                ),
                modified_dice_range = range(3, 18+1),
            ),
            'bad-weather-no-fine': dict(
                args = dict(
                    dice = [d6]*3, modifier = -2,
                    total_range = range(3, 12+1),
                ),
                modified_dice_range = range(1, 16+1),
            ),
            'good-weather-no-rain': dict(
                args = dict(
                    dice = [d6]*3, modifier = +2,
                    total_range = range(9, 18+1),
                ),
                modified_dice_range = range(5, 20+1),
            ),
        }

        for key, params in self.valid_rollers.items():
            args = params['args']
            instance = self.roller_factory(**args)
            params['instance'] = instance

class RollResultFixture(RollerFixture):
    """ Mix-in class for RollResult instance fixtures """

    def setUp(self):
        """ Set up test fixtures """
        RollerFixture.setUp(self)

        self.valid_results = {
            'green': dict(
                args = dict(
                    roller = self.valid_rollers['colour']['instance'],
                    faces = ['green'],
                ),
            ),
            '1d6 4': dict(
                args = dict(
                    roller = self.valid_rollers['1d6']['instance'],
                    faces = [4],
                ),
                total = 4,
            ),
            '1d6-7 4': dict(
                args = dict(
                    roller = self.valid_rollers['1d6-7']['instance'],
                    faces = [4],
                ),
                total = -3,
            ),
            '1d6-2 4': dict(
                args = dict(
                    roller = self.valid_rollers['1d6-2']['instance'],
                    faces = [4],
                ),
                total = 2,
            ),
            '1d6+2 4': dict(
                args = dict(
                    roller = self.valid_rollers['1d6+2']['instance'],
                    faces = [4],
                ),
                total = 6,
            ),
            '1d6+7 4': dict(
                args = dict(
                    roller = self.valid_rollers['1d6+7']['instance'],
                    faces = [4],
                ),
                total = 11,
            ),
            '3d6 1+2+3': dict(
                args = dict(
                    roller = self.valid_rollers['3d6']['instance'],
                    faces = [1,2,3],
                ),
                total = 6,
            ),
            '3d6 4+5+6': dict(
                args = dict(
                    roller = self.valid_rollers['3d6']['instance'],
                    faces = [4,5,6],
                ),
                total = 15,
            ),
            '3d6 1+1+1': dict(
                args = dict(
                    roller = self.valid_rollers['3d6']['instance'],
                    faces = [1,1,1],
                ),
                total = 3,
            ),
            '3d6 6+6+6': dict(
                args = dict(
                    roller = self.valid_rollers['3d6']['instance'],
                    faces = [6,6,6],
                ),
                total = 36,
            ),
        }

        for key, params in self.valid_results.items():
            args = params['args']
            instance = self.result_factory(**args)
            params['instance'] = instance


class Test_Die(unittest.TestCase, DieFixture):
    """ Test case for a Die object """

    def setUp(self):
        """ Set up test fixtures """
        self.die_factory = alea.die.Die
        DieFixture.setUp(self)

        self.iterate_params = scaffold.make_params_iterator(
            self.valid_dice
        )

    def test_instance(self):
        """ Die instances should be initialised """
        for key, params in self.iterate_params():
            instance = params['instance']
            self.failUnless(instance)

    def test_repr(self):
        """ Die should have useful representation """
        for key, params in self.iterate_params():
            args = params['args']
            instance = params['instance']
            repr_str = repr(instance)
            self.failUnless(repr_str.startswith("Die("))
            self.failUnless(repr_str.count("faces=%s" % args['faces']))
            self.failUnless(repr_str.endswith(")"))

    def test_num_faces(self):
        """ Die should have specified number of faces """
        for key, params in self.iterate_params():
            args = params['args']
            instance = params['instance']
            self.failUnlessEqual(
                len(args['faces']), len(instance.faces),
                msg = "len(%s) != len(%s)" % (
                    args['faces'], instance.faces
                )
            )

    def test_face_values(self):
        """ Die faces should match specified face values """
        for key, params in self.iterate_params():
            args = params['args']
            args_faces = args['faces']
            instance = params['instance']
            instance_faces = instance.faces
            self.failUnlessEqual(args_faces.sort(),
                                 list(instance_faces).sort())

    def test_is_numeric(self):
        """ Die should determine whether its faces are all numeric """
        for key, params in self.iterate_params():
            is_numeric = params.get('is_numeric', True)
            instance = params['instance']
            self.failUnlessEqual(is_numeric, instance.is_numeric())

    def test_roll(self):
        """ Die result should be one of the specified faces """
        for key, params in self.iterate_params():
            args = params['args']
            instance = params['instance']
            for i in range(1000):
                result = instance.roll()
                self.failUnless(result in args['faces'],
                    msg = "%s not in %s" % (result, args['faces'])
                )


class Test_Roller(unittest.TestCase, RollerFixture):
    """ Test case for a Roller object """

    def setUp(self):
        """ Set up test fixtures """
        self.die_factory = Stub_Die
        self.roller_factory = alea.die.Roller
        self.result_factory = Stub_RollResult
        RollerFixture.setUp(self)

        self.iterate_params = scaffold.make_params_iterator(
            self.valid_rollers
        )

    def test_instance(self):
        """ Roller instances should be initialised """
        for key, params in self.iterate_params():
            instance = params['instance']
            self.failUnless(instance)

    def test_repr(self):
        """ Roller should have useful representation """
        for key, params in self.iterate_params():
            args = params['args']
            instance = params['instance']
            repr_str = repr(instance)
            self.failUnless(repr_str.startswith("Roller("))
            self.failUnless(repr_str.count("dice=%s" % args['dice']))
            if args.get('modifier', 0):
                self.failUnless(repr_str.count(
                    "modifier=%s" % args['modifier']
                ))
            if args.get('total_range', None):
                self.failUnless(repr_str.count(
                    "total_range=%s" % args['total_range']
                ))
            self.failUnless(repr_str.endswith(")"))

    def test_dice_equal(self):
        """ Roller should have specified dice """
        for key, params in self.iterate_params():
            args = params['args']
            dice = args['dice']
            instance = params['instance']
            self.failUnlessEqual(dice, instance.dice)

    def test_modifier_equal(self):
        """ Roller should have specified modifier """
        for key, params in self.iterate_params():
            args = params['args']
            modifier = args.get('modifier', 0)
            instance = params['instance']
            self.failUnlessEqual(modifier, instance.modifier)

    def test_is_numeric(self):
        """ Roller should determine whether its dice are all numeric """
        for key, params in self.iterate_params():
            is_numeric = params.get('is_numeric', True)
            instance = params['instance']
            self.failUnlessEqual(is_numeric, instance.is_numeric(),
                msg = "%s.is_numeric() != %s" % (
                    instance, is_numeric
                )
            )

    def test_total_range(self):
        """ Roller should export its numeric total range """
        for key, params in self.iterate_params():
            args = params['args']
            if 'total_range' not in args:
                continue
            instance = params['instance']
            self.failUnlessEqual(
                args['total_range'], instance.total_range
            )

    def test_modified_dice_range(self):
        """ Roller should export its numeric modified dice range """
        for key, params in self.iterate_params():
            is_numeric = params.get('is_numeric', True)
            if not is_numeric:
                continue
            modified_dice_range = params['modified_dice_range']
            instance = params['instance']
            self.failUnlessEqual(
                modified_dice_range, instance.modified_dice_range
            )

    def test_get_result_num_modified_dice_range(self):
        """ Roller should get a result sequence in modified dice range """
        for key, params in self.iterate_params():
            args = params['args']
            if 'total_range' in args:
                continue
            is_numeric = params.get('is_numeric', True)
            if not is_numeric:
                continue
            dice = args['dice']
            dice_range_min = sum([min(d.faces) for d in dice])
            dice_range_max = sum([max(d.faces) for d in dice])
            modifier = args.get('modifier', 0)
            modified_dice_range = range(
                dice_range_min + modifier,
                dice_range_max + modifier + 1
            )
            total_range = modified_dice_range
            instance = params['instance']
            for i in range(len(instance.total_range) * 10):
                result = instance.get_result()
                self.failUnless(result.total() in total_range,
                    msg = "%d not in %s" % (
                        result.total(), total_range
                    )
                )

    def test_get_result_num_specified_range(self):
        """ Roller should get a result number in specified range """
        for key, params in self.iterate_params():
            args = params['args']
            if 'total_range' not in args:
                continue
            total_range = args['total_range']
            instance = params['instance']
            for i in range(len(instance.total_range) * 10):
                result = instance.get_result()
                self.failUnless(result.total() in total_range,
                    msg = "%s not in %s" % (
                        result.total(), total_range
                    )
                )


class Test_RollResult(unittest.TestCase, RollResultFixture):
    """ Test case for RollResult class """

    def setUp(self):
        """ Set up test fixtures """
        self.die_factory = Stub_Die
        self.roller_factory = Stub_Roller
        self.result_factory = alea.die.RollResult

        RollResultFixture.setUp(self)

        self.iterate_params = scaffold.make_params_iterator(
            default_params_dict = self.valid_results
        )

    def test_instance(self):
        """ RollResult instance should be created """
        for key, params in self.iterate_params():
            instance = params['instance']
            self.failUnless(instance)

    def test_repr(self):
        """ RollResult should have useful representation """
        for key, params in self.iterate_params():
            args = params['args']
            instance = params['instance']
            repr_str = repr(instance)
            self.failUnless(repr_str.startswith("RollResult("))
            self.failUnless(repr_str.count(
                "roller=%s" % args['roller']
            ))
            self.failUnless(repr_str.count(
                "faces=%s" % args['faces']
            ))
            self.failUnless(repr_str.endswith(")"))

    def test_roller_equal(self):
        """ RollResult should have specified roll parameters """
        for key, params in self.iterate_params():
            args = params['args']
            instance = params['instance']
            self.failUnlessEqual(
                args['roller'], instance.roller
            )

    def test_faces_equal(self):
        """ RollResult should have specified die faces """
        for key, params in self.iterate_params():
            args = params['args']
            instance = params['instance']
            self.failUnlessEqual(args['faces'], instance.faces)

    def test_total(self):
        """ RollResult should determine its numeric total """
        for key, params in self.iterate_params():
            args = params['args']
            roller = args['roller']
            if not roller.is_numeric():
                continue
            total = sum(args['faces']) + roller.modifier
            total = min(total, min(roller.total_range))
            total = max(total, max(roller.total_range))
            instance = params['instance']
            self.failUnlessEqual(total, instance.total())


suite = scaffold.suite(__name__)

__main__ = scaffold.unittest_main

if __name__ == '__main__':
    import sys
    exitcode = __main__(sys.argv)
    sys.exit(exitcode)
