# -*- coding: utf-8 -*-

# stub_dice.py
# Part of alea, a library of random generators for games
#
# Copyright © 2007 Ben Finney <ben@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Stub objects for dice
"""

import random


class Stub_Die(object):
    """ Stub object for Die behaviour """

    def __init__(self, faces):
        """ Set up a new instance """
        self.faces = faces
        self._roller = self._sequential_roller()

    def __repr__(self):
        params = "faces=%s" % self.faces
        result = "Stub_Die(%s)" % params
        return result

    def is_numeric(self):
        result = True
        try:
            for f in self.faces:
                int(f)
        except ValueError:
            result = False
        return result

    def _sequential_roller(self):
        """ Generate sequential faces from the die """
        i = 0
        while True:
            yield self.faces[i]
            i += 1
            if i >= len(self.faces):
                i = 0

    def _random_roller(self):
        """ Generate random faces from the die """
        while True:
            yield random.choice(self.faces)

    def roll(self):
        """ Get a result from rolling the die """
        return self._roller.next()


class Stub_Roller(object):
    """ Stub object for Roller """

    def __init__(self, dice, modifier=0, total_range=None):
        """ Set up a new instance """
        self.dice = dice
        self.modifier = modifier
        self.total_range = total_range

        if not self.total_range:
            self.total_range = self._get_modified_dice_range()

        self._roll_generator = self._sequential_generator()

    def __repr__(self):
        params = []
        params.append("dice=%s" % self.dice)
        if self.modifier:
            params.append("modifier=%d" % self.modifier)
        if self.total_range != self._get_modified_dice_range():
            params.append("total_range=%s" % self.total_range)
        result = "Stub_Roller(%s)" % ", ".join(params)
        return result

    def is_numeric(self):
        result = True
        if [d for d in self.dice if not d.is_numeric()]:
            result = False
        return result

    def _get_modified_dice_range(self):
        result = None
        if self.is_numeric():
            result = range(
                sum(min(d.faces) for d in self.dice) + self.modifier,
                sum(max(d.faces) for d in self.dice) + self.modifier + 1
            )
        return result

    def _sequential_generator(self):
        """ Generate sequential results from the range """
        die_indices = [0] * len(self.dice)
        while True:
            yield [d.faces[die_indices[i]]
                   for i, d in enumerate(self.dice)]
            for die_seq in range(len(self.dice)):
                die_indices[die_seq] += 1
                if die_indices[die_seq] < len(self.dice[die_seq].faces):
                    break
                else:
                    die_indices[die_seq] = 0

    def _random_generator(self):
        """ Generate random results from the range """
        while True:
            yield [random.choice(d.faces) for d in self.dice]

    def get_result(self):
        """ Get a result from rolling the dice """
        faces = self._roll_generator.next()
        result = Stub_RollResult(self, faces)
        return result


class Stub_RollResult(object):
    """ Stub object for RollResult class """

    def __init__(self, roller, faces):
        """ Set up a new instance """
        self.roller = roller
        self.faces = faces

    def total(self):
        result = None
        if self.roller.is_numeric():
            result = sum(self.faces) + self.roller.modifier
            result = min(result, min(self.roller.total_range))
            result = max(result, max(self.roller.total_range))
        return result
