# -*- coding: utf-8 -*-

# die.py
# Part of alea, a library of random generators for games
#
# Copyright © 2007 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Implementation of dice for determining chance
"""

import random


class Die(object):
    """ Parameters and behaviour for a polyhedral chance die """

    def __init__(self, faces):
        """ Set up a new instance """
        self.faces = list(faces)

    def __repr__(self):
        params = []
        params.append("faces=%s" % self.faces)
        result = "Die(%s)" % ", ".join(params)
        return result

    def is_numeric(self):
        """ Determine whether the die has all numeric faces """
        result = True
        for face in self.faces:
            try:
                int(face)
            except ValueError:
                result = False
                break
        return result

    def roll(self):
        """ Roll the die """
        result = random.choice(self.faces)
        return result


class Roller(object):
    """ Parameters for a roll of dice """

    def __init__(self, dice, modifier=0, total_range=None):
        """ Set up a new instance """
        self.dice = dice
        self.modifier = modifier
        self.total_range = total_range

        if not self.total_range:
            self.total_range = self.modified_dice_range

    def __repr__(self):
        params = []
        params.append("dice=%s" % self.dice)
        if self.modifier:
            params.append("modifier=%s" % self.modifier)
        if self.total_range != self.modified_dice_range:
            params.append("total_range=%s" % self.total_range)
        result = "Roller(%s)" % ", ".join(params)
        return result

    def is_numeric(self):
        """ Determine whether the dice are all numeric """
        result = True
        if [d for d in self.dice if not d.is_numeric()]:
            result = False
        return result

    def _get_modified_dice_range(self):
        result = None
        if self.is_numeric():
            dice_min = sum([min(d.faces) for d in self.dice])
            dice_max = sum([max(d.faces) for d in self.dice])
            result = range(
                dice_min + self.modifier,
                dice_max + self.modifier + 1
            )
        return result
    modified_dice_range = property(_get_modified_dice_range)

    def get_result(self):
        """ Get a random result """

        faces = []
        for die in self.dice:
            faces.append(die.roll())

        result = RollResult(self, faces)

        return result


class RollResult(object):
    """ Result of a roll of the dice """

    def __init__(self, roller, faces):
        """ Set up a new instance """
        self.roller = roller
        self.faces = faces

    def __repr__(self):
        params = []
        params.append("roller=%s" % self.roller)
        params.append("faces=%s" % self.faces)
        result = "RollResult(%s)" % ", ".join(params)
        return result

    def total(self):
        result = None
        if self.roller.is_numeric():
            result = sum(self.faces) + self.roller.modifier
            result = min(result, min(self.roller.total_range))
            result = max(result, max(self.roller.total_range))
        return result
