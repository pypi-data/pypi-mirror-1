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
Classes for C{(N,T,P,S)} BNF grammars that define GE Individuals.

I{See} M. O'Neill & C. Ryan, U{Grammatical Evolution: Evolutionary Automatic
Programming in an Arbitrary Language}, pp. 36-44.
"""

import copy


class NotInitializedError(Exception):
    pass


class State(object):
    """
    An instance of me is passed to each terminal in a sentence of terminals
    that represent a GE-derived individual program. I provide access to the
    program's state during evaluation.
    """
    def copy(self):
        return copy.copy(self)


class Sentence(list):
    """
    I am a sequence representing a sentence of terminals that embody a
    GE-derived individual program.
    """
    def copy(self):
        return copy.copy(self)


class Attributes(object):
    """
    An instance of me is passed to each production rule, and finally to the
    terminals produced, to effect inheritance of attributes of an attribute
    grammar.
    """
    def __init__(self, parent=None):
        """
        Constructs an attribute container with a shallow copy of any parent
        container specified. Thus changes to an attribute of a parent container
        can be made from any container inheriting that attribute.

        For instances passed to terminals, set the I{terminal} keyword C{True}.
        """
        if isinstance(parent, self):
            self._data = parent._data.copy()
            self._k = len(self.sentence)
        else:
            self._data = {'sentence':Sentence()}

    def __getattribute__(self, name):
        """
        Returns all requested attributes from the state dict except for class
        attributes (importantly, my methods) and private instance attributes
        """
        if name.startswith('_') or \
               name in object.__getattribute__(self, '__class__').__dict__:
            return object.__getattribute__(self, name)
        return object.__getattribute__(self, '_data')[name]

    def __setattr__(self, name, value):
        """
        Stores all attributes in the state dict except for class attributes and
        private instance attributes.
        """
        if name.startswith('_') or \
               name in object.__getattribute__(self, '__class__').__dict__:
            return object.__setattr__(self, name, value)
        self._data[name] = value

    def __delattr__(self, name):
        """
        Deletes attributes from the state dict except for class attributes and
        private instance attributes.
        """
        if name.startswith('_') or \
               name in object.__getattribute__(self, '__class__').__dict__:
            return object.__delattr__(self, name)
        del self._data[name]

    def terminals(self):
        """
        Returns the string representations of all terminals added to the
        sentence thus far.
        """
        return [str(x) for x in self.sentence]
        
    def next(self, N=1):
        """
        Returns the next I{N} terminals in the sentence (for terminals only)
        """
        k = self._k + 1
        return self.sentence[k:k+N]


class Terminal(object):
    """
    The GE-derived individual program consists of a sentence of instances of
    me.
    """
    def __init__(self, valuer, label=""):
        """
        Constructs a new terminal with the supplied value-producing object
        I{valuer} and an optionally specified text label.

        The value-producing object can be callable, in which case its result is
        used as the value. Any callable used must accept two objects as
        arguments:

            1. An instance I{s} of L{State} providing access to the state of
               the program during evaluation.

            2. An instance I{a} of L{Attributes} providing access to the
               attributes inherited by the terminal from the chain of
               production rules that generated it, including some useful
               methods inherited as attributes of the L{Attributes} class
               itself.
               
        """
        self.valuer = valuer
        self.label = label

    def __str__(self):
        """
        My string depiction is simply my text label, if any.
        """
        return self.label
    
    def __cmp__(self, other):
        """
        Provides string-like comparison for instances based on the name of the
        terminal function.
        """
        args = tuple([x.f.__name__ for x in (self, other)])
        return cmp(*args)

    def value(self, s):
        if callable(self.valuer):
            return self.valuer(s)
        return self.valuer


class TBase(object):
    """
    Base class for terminals of a BNF grammar.
    
    Instances includes a special list I{sentence} that contains the terminal
    objects produced from calls to my terminal-factory methods, in
    sequence. The methods, including the additional terminal factory methods of
    whatever subclass of me is used in the user's BNF grammar, are called by
    production rules of a hosting L{P} instance of that grammar.
    """
    def openParen(self, a):
        self.closer = 'closeParen'
        self.next = a.next
        return Terminal(self._evalUntilClose, label='(')

    def openBrace(self, a):
        self.closer = 'closeBrace'
        self.next = a.next
        return Terminal(self._evalUntilClose, label='{')

    def closeParen(self, a):
        return Terminal(None, label=')')

    def closeBrace(self, a):
        return Terminal(None, label='}')

    def _evalUntilClose(self, s):
        savedState = s
        s = {}
        while True:
            nextTerminal = self.next()
            if nextTerminal == self.closer:
                break
            nextTerminal.value(s)
        result = s
        s = savedState
        return result


class PBase(object):
    """
    Base class for a user-defined production rule set B{P}.
    """
    def setup(self, T, S):
        """
        @param T: A subclass of L{T} that defines a terminal set for this
          production rule set.

        @param S: One of my production rule methods to start with
        
        """
        self.t = T()
        self.S = S
    
    def derive(self, genome, a=Attributes()):
        """
        Applies the supplied I{genome} to my user-defined production rules and
        the terminal set of the supplied class I{T}, starting with rule I{S}
        and the root attribute container I{a}.

        The mapping process runs recursively and finally returns with the
        completed sentence of terminal objects when no rules are left to apply,

        @param genome: A sequence of codons defining the genome for one
          individual program.
            
        """
        self.genome  = genome
        self.rootAttributes = a
        
        self.N_codons = len(genome)
        self.k = 0

        if not hasattr(self, 't') or not isinstance(self.t, TBase):
            raise NotImplementedError(
                "You have not assigned me a terminal set subclass of TBase!")
        if not hasattr(self, 'S') or not callable(self.S):
            raise NotImplementedError(
                "You have not set my start symbol S to a production rule")

        self.rootAttributes = a
        # The initial non-terminal is called with the root attribute container
        initialRules = self.S(a)
        # The resulting production rules are applied to the first of probably
        # many recursive next() calls with that container
        self.next(a, initialRules)
        # The final result...
        return self.rootAttributes.sentence

    def codon(self, N=1):
        """
        Returns the value of the next codon in our journey along the genome,
        mapped to the modulo I{N} space if specified.
        """
        k_mod = divmod(self.k, self.N_codons)
        self.k += 1
        return divmod(self.genome[k_mod], N)[0]

    def next(self, a, rules):
        """
        Provides a copy of the supplied attribute container I{a} to each
        element of a selected one of the supplied rules. The elements of the
        selected sequences are applied in turn, with their results being
        appended to the terminal sentence or applied recursively as production
        rules.
        """
        N = len(rules)
        if N == 1:
            # If only one rule is provided to choose from, there's no need to
            # use up a codon to make that (non)decision.
            selectedRule = rules[0]
        else:
            # Select one of the provided rules based on the next codon, mapped
            # to the selection space.
            selectedRule = rules[self.codon(N)]
        # Iterate over each element of the selected rule
        for element in selectedRule:
            if not callable(element):
                raise TypeError(
                    "Non-callable element '%s' in a production rule" \
                    % repr(element))
            else:
                # Call the element with its own inherited copy of the caller's
                # attribute container to a result that is either another
                # sequnece of production rules or a terminal object
                aNext = a.copy()
                result = element(aNext)
                if isinstance(result, Terminal):
                    # The element was a terminal factory, and what it generated
                    # was a Terminal object that gets appended to the terminal
                    # sentence
                    a.sentence.append(result)
                elif isinstance(result, (list, tuple)):
                    # Otherwise, we must have a sequence of production rules to
                    # continue applying.
                    self.next(aNext, result)
                else:
                    msg = "Production rule element returned an object of "+\
                          "type '%s', must be a Terminal or sequence of "+\
                          "further production rules"
                    raise TypeError(msg % type(result))
