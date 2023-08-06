# AsynCluster: gevolver
# Python-based Grammatical Evolution with attribute grammars
#
# Copyright (C) 2006-2007 by Edwin A. Suominen, http://www.eepatents.com
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the file COPYING for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
This example solves the knapsack problem for a camping trip using a
C{{N,T,P,S}} BNF grammar with attributes. I{See} R. Cleary, U{Extending
Grammatical Evolution with Attribute Grammars: An Application to Knapsack
Problems}, pp. 83-93.
"""

# Imports
from gevolver.grammar import TBase, NBase


class Setting(object):
    """
    A base class for objects representing settings for camping trips
    """
    pass


class Canadian_Rockies(Setting):
    """
    The Canadian Rockies have lots of bears and are very remote, but handguns
    are a no-no. Water is plentiful.
    """
    handguns = False
    bears = True
    remote = True
    dry = False
    cold = True
    hot = False


class American_Rockies(Canadian_Rockies):
    """
    Handguns are OK in the American Rockies, however.
    """
    handguns = True


class Yellowstone(Setting):
    """
    Yellowstone has lots of bears but isn't remote with all the tourists. Handguns
    are a no-no. Water is plentiful.
    """
    handguns = False
    bears = True
    remote = False
    dry = False
    cold = False
    hot = False


class Death_Valley(Setting):
    """
    Death valley has no bears but is hot, remote, and has no water.
    """
    handguns = True
    bears = False
    remote = True
    dry = True
    cold = False
    hot = True


class T(TBase):
    """
    BNF Grammar Terminal Set
    """
    def handgun(self, a):
        """
        The handgun shouldn't be brought where it isn't allowed. Otherwise,
        it adds value depending on the danger present.
        """
        def valuer(s):
            s.bulk += 1
            if s.setting.handguns:
                s.value += s.setting.bears + s.setting.remote
            else:
                s.value -= 10

        return Terminal(valuer, 'handgun')

    def propane(self, a):
        """
        Propane is bulky and has no usefulness on its own.
        """
        return Terminal(lambda s: s.bulk += 2, 'propane')

    def pan(self, a):
        """
        A pan is heavy and has only a little usefulness on its own, and then
        only if the setting isn't dry.
        """
        def valuer(s):
            s.bulk += 2
            if not s.setting.dry:
                s.value += 1

        return Terminal(valuer, 'pan')

    def stove(self, a):
        """
        A stove is useful if propane and a pan have been brought.
        """
        def valuer(s):
            s.bulk += 2
            if 'propane' in a.items and 'pan' in a.items:
                s.value += 2

        return Terminal(valuer, 'stove')

    def heater(self, a):
        """
        A heater is somewhat useful if it's cold and propane has been brought.
        """
        def valuer(s):
            s.bulk += 1
            if s.setting.cold and 'heater' in a.items:
                s.value += 1

        return Terminal(valuer, 'heater')

    def literOfWater(self, a):
        """
        A liter of water is useful, especially if it's hot and the setting is dry.
        """
        s.bulk += 1
        addedValue = 1 + (s.setting.dry and s.setting.hot)
        s.value += addedValue


class P(PBase):
    """
    BNF Grammar Rule Set
    """
    def singleItem(self, a):
        possibilites = [self.next]
        choices = ('handgun', 'propane', 'pan', 'stove', 'heater')
        while choices:
            itemName = choices.pop(self.codon(len(choices)))
            if itemName not in a.items:
                possibilites.append(
                    [self.addItem, getattr(self.t, itemName)])
                break
        return possibilites

    # TODO TODO TODO
    def addItem(self, terminal):
        a.items.append(terminal)
        return item

    def done(self, a):
        pass


def fitness(initialState, resultState):
    pass
    

    
