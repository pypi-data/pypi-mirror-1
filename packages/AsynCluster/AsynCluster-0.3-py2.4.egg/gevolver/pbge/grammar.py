# pbGE:
# Grammatical Evolution (GE) run by a "master" server and a bunch of "worker"
# clients via Twisted's Perspective Broker (PB). Computations are dispatched
# and carried out asynchronously using Twisted's deferred processing
# capabilities.
#
# Copyright (C) 2006 by Edwin A. Suominen, http://www.eepatents.com
#
#
# This code is not currently released for any public use.

"""
Classes for C{(N,T,P,S)} BNF grammars that define GE Individuals.

I{See} M. O'Neill & C. Ryan, U{Grammatical Evolution: Evolutionary Automatic
Programming in an Arbitrary Language}, pp. 36-44.
"""

# Imports
import copy
from twisted.internet.defer import Deferred


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

    def __getattr__(self, name):
        """
        Returns all requested attributes from the state dict except for class
        attributes (importantly, my methods) and private instance attributes
        """
        isAttr = not name.startswith('_') and \
                 not name in self.__class__.__dict__
        if isAttr:
            return self._data[name]
        else:
            return object.__getattr__(self, name)

    def __setattr__(self, name, value):
        """
        Stores all attributes in the state dict except for class attributes and
        private instance attributes.
        """
        isAttr = not name.startswith('_') and \
                 not name in self.__class__.__dict__
        if isAttr:
            self._data[name] = value
        else:
            object.__setattr__(self, name, value)

    def __delattr__(self, name):
        """
        Deletes attributes from the state dict except for class attributes and
        private instance attributes.
        """
        isAttr = not name.startswith('_') and \
                 not name in self.__class__.__dict__
        if isAttr:
            del self._data[name]
        else:
            object.__delattr__(self, name)

    def copy(self):
        """
        """
        return Attribute(self)
    
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
        return self.sentence[self._k + 1 : self._k + 1 + N]


class Terminal:
    """
    The GE-derived individual program consists of a sentence of instances of
    me.
    """
    def __init__(self, value, label=""):
        """
        Constructs a new terminal with the supplied value-producing object I{value)
        and an optionally specified text label.

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
        self.label = label
        if callable(value):
            self.value = value
        else:
            self.value = lambda s, a: value

    def __str__(self):
        """
        """
        return self.label
    
    def __cmp__(self, other):
        """
        Provides string-like comparison for instances based on the name of the
        terminal function.
        """
        this = self.f.__name__
        if this < other:
            return -1
        elif this > other:
            return 1
        else:
            return 0


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
        self.closer = 'closeParen'
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

        The mapping process runs in a thread and returns a C{Deferred}, which
        fires with the completed sentence of terminal objects when no rules are
        left to apply,

        @param genome: A sequence of codons defining the genome for one
            individual program.
            
        """
        def done(null):
            return self.rootAttributes.sentence

        def oops(failure):
            """TODO"""
            raise Exception()

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
        return deferToThread(next, a, initialRules).addCallbacks(done, oops)

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
