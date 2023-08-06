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
GE Individuals
"""

# Imports
import copy


class ConditionError(Exception):
    pass


class Termiterator(object):
    """
    """
    def __init__(self, sentence, inputState):
        self.remnant = copy.copy(sentence)
        self.state = copy.copy(inputState)

    def __iter__(self):
        """
        """
        return self

    def next(self):
        """
        Running the C{value} method on the terminal can't take too long or it
        will mess up the coiteration.
        """
        if self.remnant:
            terminal = self.remnant.pop(0)
            terminal.value(self.state)
        else:
            raise StopIteration


class Individual(object):
    """
    I manage a set of production rules B{P} and a terminal set B{T}, applying
    them to supplied genomes and evaluating the resulting individual program.
    """
    def evaluate(self, sentence, inputStates, f):
        """
        Evaluates the program defined by the supplied I{sentence} of terminals,
        sequence of I{inputStates}, and fitness function I{f}.
        
        Returns the mean fitness for all the input states supplied.
        """
        results = []
        for inputState in inputStates:
            resultState = self.run(sentence, inputState)
            fitness = f(inputState, resultState)
            results.append(fitness)
        return sum(abs(results)) / len(results)

    def run(self, sentence, inputState):
        """
        Runs the program defined by the supplied I{sentence} of terminals,
        giving it a copy of the supplied I{inputState} to access and
        modify.

        When done, returns a reference to the program's copy of the state, as
        modified by the program.
        """
        for terminal in sentence:
            terminal.value(self.state)

        Termiterator(sentence, inputState)
        return coiterate(ti).addCallback(ti.getState)
