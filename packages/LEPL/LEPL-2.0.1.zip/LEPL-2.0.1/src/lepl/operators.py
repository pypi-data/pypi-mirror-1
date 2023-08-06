
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Support for operator syntactic sugar (and operator redefinition).
'''

from threading import local
from abc import ABCMeta

from lepl.support import open_stop


# Python 2.6
#class Matcher(metaclass=ABCMeta):
Matcher = ABCMeta('Matcher', (object, ), {})
'''ABC used to identify matchers.'''


class Namespace(local):
    '''
    A store for operator definitions.
    
    This subclasses threading.local so each thread effectively has its own 
    instance (see test).
    '''
    
    def __init__(self, base={}):
        super(Namespace, self).__init__()
        self.__stack = [base]
        
    def push(self, extra={}):
        '''
        Add further names, savign the current state to the stack.
        '''
        self.__stack.append(dict(self.current()))
        for name in extra:
            self.set_opt(name, extra[name])
        
    def pop(self):
        '''
        Return the previous state from the stack.
        '''
        self.__stack.pop(-1)
        
    def __enter__(self):
        '''
        Allow use within a with context by duplicating the current state
        and saving to the stack.  Returns self to allow manipulation via set.
        '''
        self.push()
        return self
        
    def __exit__(self, *args):
        '''
        Restore the previous state from the stack on leaving the context.
        '''
        self.pop()
        
    def current(self):
        '''
        The current state (a map from names to operator implementations).
        '''
        return self.__stack[-1]
    
    def set(self, name, value):
        '''
        Set a value.
        '''
        self.current()[name] = value
        
    def set_opt(self, name, value):
        '''
        Set a value if it is not None.
        '''
        if value != None:
            self.set(name, value)
        
    def __getitem__(self, name):
        '''
        Get a value.
        '''
        return self.current()[name]


class DefaultNamespace(Namespace):
    '''
    Define the default operators.
    '''
    
    def __init__(self):
        # Handle circular dependencies
        from lepl.matchers import And, Space, Add, Or, Apply, Drop, KApply, \
            Repeat, raise_error, First, Map
        super(DefaultNamespace, self).__init__({
            SPACE_OPT: lambda a, b: And(a, Space()[0:,...], b),
            SPACE_REQ: lambda a, b: And(a, Space()[1:,...], b),
            ADD:       lambda a, b: Add(And(a, b)),
            AND:       And,
            OR:        Or,
            APPLY:     Apply,
            NOT:       Drop,
            ARGS:      lambda a, b: Apply(a, b, args=True),
            KARGS:     KApply,
            RAISE:     lambda a, b: KApply(a, raise_error(b)),
            REPEAT:    Repeat,
            FIRST:     First,
            MAP:       Map
        })
    

__GLOBAL = None
'''
The global singleton.
'''

def Global():
    '''
    Global (per-thread) binding from operator name to implementation.
    
    This provides an interface to `__GLOBAL`.
    '''
    # Delay creation to handle circular dependencies.
    global __GLOBAL
    if __GLOBAL is None:
        __GLOBAL = DefaultNamespace()
    return __GLOBAL


SPACE_OPT = '/'
'''Name for / operator.'''
SPACE_REQ = '//'
'''Name for // operator.'''
ADD = '+'
'''Name for + operator.'''
AND = '&'
'''Name for & operator.'''
OR = '|'
'''Name for | operator.'''
APPLY = '>'
'''Name for > operator.'''
NOT = '~'
'''Name for ~ operator.'''
ARGS = '*'
'''Name for * operator.'''
KARGS = '**'
'''Name for ** operator.'''
RAISE = '^'
'''Name for ^ operator.'''
REPEAT = '[]'
'''Name for [] operator.'''
FIRST = '%'
'''Name for % operator.'''
MAP = '>>'
'''Name for >> operator.'''


class Override(object):
    '''
    Allow an operator to be redefined within a with context.
    '''

    def __init__(self, space_opt=None, space_req=None, repeat=None,
                  add=None, and_=None, or_=None, not_=None, 
                  apply=None, args=None, kargs=None, raise_=None,
                  first=None, map=None):
        self.__frame ={SPACE_OPT: space_opt, SPACE_REQ: space_req,
                       REPEAT: repeat, ADD: add, AND: and_, OR: or_, 
                       NOT: not_, APPLY: apply, ARGS: args, KARGS: kargs, 
                       RAISE: raise_, FIRST: first, MAP: map}
        
    def __enter__(self):
        '''
        On entering the context, add the new definitions.
        '''
        Global().push(self.__frame)
        
    def __exit__(self, *args):
        '''
        On leaving the context, return to previous definition.
        '''
        Global().pop()


class Separator(Override):
    '''
    Redefine ``[]`` and ``&`` to include the given matcher as a separator (so it will
    be used between list items and between matchers separated by the & 
    operator)
    '''
    
    def __init__(self, separator):
        '''
        If the separator is a string it is coerced to `lepl.matchers.Regexp()`.
        '''
        # Handle circular dependencies
        from lepl.matchers import Regexp, And, Repeat, coerce
        separator = coerce(separator, Regexp)
        and_ = lambda a, b: And(a, separator, b)
        def repeat(m, st=0, sp=None, d=0, s=None, a=False):
            if s is None: s = separator
            return Repeat(m, st, sp, d, s, a)
        super(Separator, self).__init__(and_=and_, repeat=repeat)
        
        
GREEDY = 'g'
'''Flag (splice increment) for inefficient, guaranteed greedy matching.'''
NON_GREEDY = 'n'
'''Flag (splice increment) for inefficient, guaranteed non-greedy matching.'''
DEPTH_FIRST = 'd'
'''Flag (splice increment) for efficient, quasi-greedy, matching (default).'''
BREADTH_FIRST = 'b'
'''Flag (splice increment) for efficient, quasi-non-greedy, matching.'''


class OperatorMixin(object):
    '''
    Define the operators used to combine elements in a grammar specification.
    '''

    def __init__(self):
        super(OperatorMixin, self).__init__()
        
    def __add__(self, other):
        '''
        **self + other** - Join strings, merge lists.
        
        Combine adjacent matchers in sequence, merging the result with "+" 
        (so strings are joined, lists merged).
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        self.__check(ADD, other, True)
        return Global()[ADD](self, other)

    def __radd__(self, other):
        '''
        **other + self** - Join strings, merge lists.
        
        Combine adjacent matchers in sequence, merging the result with "+" 
        (so strings are joined, lists merged).
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        self.__check(ADD, other, True)
        return Global()[ADD](other, self)

    def __and__(self, other):
        '''
        **self & other** - Append results.
        
        Combine adjacent matchers in sequence.  This is equivalent to 
        `lepl.matchers.And()`.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        self.__check(AND, other, True)
        return Global()[AND](self, other) 
        
    def __rand__(self, other):
        '''
        **other & self** - Append results.
        
        Combine adjacent matchers in sequence.  This is equivalent to 
        `lepl.matchers.And()`.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        self.__check(AND, other, True)
        return Global()[AND](other, self)
    
    def __div__(self, other):
        '''
        For 2.6
        '''
        return self.__truediv__(other)
    
    def __rdiv__(self, other):
        '''
        For 2.6
        '''
        return self.__rtruediv__(other)
    
    def __truediv__(self, other):
        '''
        **self / other** - Append results, with optional separating space.
        
        Combine adjacent matchers in sequence, with an optional space between
        them.  The space is included in the results.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        self.__check(SPACE_OPT, other, True)
        return Global()[SPACE_OPT](self, other)
        
    def __rtruediv__(self, other):
        '''
        **other / self** - Append results, with optional separating space.
        
        Combine adjacent matchers in sequence, with an optional space between
        them.  The space is included in the results.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        self.__check(SPACE_OPT, other, True)
        return Global()[SPACE_OPT](other, self)
        
    def __floordiv__(self, other):
        '''
        **self // other** - Append results, with required separating space.
        
        Combine adjacent matchers in sequence, with a space between them.  
        The space is included in the results.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        self.__check(SPACE_REQ, other, True)
        return Global()[SPACE_REQ](self, other)
        
    def __rfloordiv__(self, other):
        '''
        **other // self** - Append results, with required separating space.
        
        Combine adjacent matchers in sequence, with a space between them.  
        The space is included in the results.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        self.__check(SPACE_REQ, other, True)
        return Global()[SPACE_REQ](other, self)
        
    def __or__(self, other):
        '''
        **self | other** - Try alternative matchers.
        
        This introduces backtracking.  Matches are tried from left to right
        and successful results returned (one on each "recall").  This is 
        equivalent to `lepl.matchers.Or()`.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        self.__check(OR, other, True)
        return Global()[OR](self, other) 
        
    def __ror__(self, other):
        '''
        **other | self** - Try alternative matchers.
        
        This introduces backtracking.  Matches are tried from left to right
        and successful results returned (one on each "recall").  This is 
        equivalent to `lepl.matchers.Or()`.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        self.__check(OR, other, True)
        return Global()[OR](other, self) 
        
    def __mod__(self, other):
        '''
        **self % other** - Take first match (committed choice).
        
        Matches are tried from left to right and the first successful result
        is returned.  This is equivalent to `lepl.matchers.First()`.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        self.__check(FIRST, other, True)
        return Global()[FIRST](self, other) 
        
    def __rmod__(self, other):
        '''
        **other % self** - Take first match (committed choice).
        
        Matches are tried from left to right and the first successful result
        is returned.  This is equivalent to `lepl.matchers.First()`.
        
        :Parameters:
        
          other
            Another matcher or a string that will be converted to a literal
            match.
        '''
        self.__check(FIRST, other, True)
        return Global()[FIRST](other, self) 
        
    def __invert__(self):
        '''
        **~self** - Discard the result.

        This generates a matcher that behaves as the original, but returns
        an empty list. This is equivalent to `lepl.matchers.Drop()`.
        
        Note that `lepl.matchers.Lookahead()` overrides this method to have
        different semantics (negative lookahead).
        '''
        return Global()[NOT](self) 
        
    def __getitem__(self, indices):
        '''
        **self[start:stop:algorithm, separator, ...]** - Repetition and lists.
        
        This is a complex statement that modifies the current matcher so
        that it matches several times.  A separator may be specified
        (eg for comma-separated lists) and the results may be combined with
        "+" (so repeated matching of characters would give a word).
        
        start:stop:algorithm
          This controls the number of matches made and the order in which
          different numbers of matches are returned.
          
          [start]
            Repeat exactly *start* times
            
          [start:stop]
            Repeat *start* to *stop* times (starting with as many matches
            as possible, and then decreasing as necessary).
            
          [start:stop:algorithm]
            Direction selects the algorithm for searching.
            
            'b' (BREADTH_FIRST)
              A breadth first search is used, which tends to give shorter
              matches before longer ones.  This tries all possible matches for 
              the sub-matcher first (before repeating calls to consume more 
              of the stream).  If the sub-matcher does not backtrack then this 
              guarantees that the number of matches returned will not decrease 
              (ie will monotonically increase) on backtracking.
              
            'd' (DEPTH_FIRST)
              A depth first search is used, which tends to give longer
              matches before shorter ones.  This tries to repeats matches 
              with the sub-matcher, consuming as much of the stream as 
              possible, before backtracking to find alternative matchers.
              If the sub-matcher does not backtrack then this guarantees
              that the number of matches returned will not increase (ie will
              monotonically decrease) on backtracking.
              
            'g' (GREEDY)
              An exhaustive search is used, which finds all results (by 
              breadth first search) and orders them by length before returning 
              them ordered from longest to shortest.  This guarantees that
              the number of matches returned will not increase (ie will
              monotonically decrease) on backtracking, but can consume a lot 
              of resources.
              
            'n' (NON_GREEDY)
              As for 'g' (GREEDY), but results are ordered shortest to 
              longest.  This guarantees that the number of matches returned 
              will not decrease (ie will monotonically increase) on 
              backtracking, but can consume a lot of resources,
            
          Values may be omitted; the defaults are: *start* = 0, *stop* = 
          infinity, *algorithm* = 'd' (DEPTH_FIRST).

        separator
          If given, this must appear between repeated values.  Matched
          separators are returned as part of the result (unless, of course,
          they are implemented with a matcher that returns nothing).  If 
          *separator* is a string it is converted to a literal match.

        ...
          If ... (an ellipsis) is given then the results are joined together
          with "+".           

        Examples
        --------
        
        Any()[0:3,...] will match 3 or less characters, joining them
        together so that the result is a single string.
        
        Word()[:,','] will match a comma-separated list of words.
        
        value[:] or value[0:] or value[0::'d'] is a "greedy" match that,
        if value does not backtrack, is equivalent to the "*" in a regular
        expression.
        value[::'n'] is the "non-greedy" equivalent (preferring as short a 
        match as possible) and value[::'g'] is greedy even when value does
        provide alternative matches on backtracking.
        '''
        start = 0
        stop = None
        step = DEPTH_FIRST
        separator = None
        add = False
        if not isinstance(indices, tuple):
            indices = [indices]
        for index in indices:
            if isinstance(index, int):
                start = index
                stop = index
                step = DEPTH_FIRST
            elif isinstance(index, slice):
                start = index.start if index.start != None else 0
                stop = index.stop if not open_stop(index) else None
                step = index.step if index.step != None else DEPTH_FIRST
            elif index == Ellipsis:
                add = True
            elif separator is None:
                separator = index
            else:
                raise TypeError(index)
        return Global()[REPEAT](self, start, stop, step, separator, add)
        
    def __gt__(self, function):
        '''
        **self in function** - Process or label the results.
        
        Create a named pair or apply a function to the results.  This is
        equivalent to `lepl.matchers.Apply()`.
        
        :Parameters:
        
          function
            This can be a string or a function.
            
            If a string is given each result is replaced by a 
            (name, value) pair, where name is the string and value is the
            result.
            
            If a function is given it is called with the results as an
            argument.  The return value is used as the new result.  This
            is equivalent to `lepl.matchers.Apply()` with nolist=False.
        '''
        self.__check(APPLY, function, False)
        return Global()[APPLY](self, function) 
    
    def __rshift__(self, function):
        '''
        **self >> function** - Process or label the results (map).
        
        Create a named pair or apply a function to each result in turn.  
        This is equivalent to `lepl.matchers.Map()`.  It is similar to 
        *self >= function*, except that the function is applied to each 
        result in turn.
        
        :Parameters:
        
          function
            This can be a string or a function.
            
            If a string is given each result is replaced by a 
            (name, value) pair, where name is the string and value is the
            result.
            
            If a function is given it is called with each result in turn.
            The return values are used as the new result.
        '''
        self.__check(MAP, function, False)
        return Global()[MAP](self, function) 
        
    def __mul__(self, function):
        '''
        **self * function** - Process the results (\*args).
        
        Apply a function to each result in turn.  
        This is equivalent to `lepl.matchers.Apply()` with ``args=True``.  
        It is similar to *self > function*, except that the function is 
        applies to multiple arguments (using Python's ``*args`` behaviour).
        
        :Parameters:
        
          function
            A function that is called with the results as arguments.
            The return values are used as the new result.
        '''
        self.__check(ARGS, function, False)
        return Global()[ARGS](self, function) 
        
    def __pow__(self, function):
        '''
        **self \** function** - Process the results (\**kargs).
        
        Apply a function to keyword arguments
        This is equivalent to `lepl.matchers.KApply()`.
        
        :Parameters:
        
          function
            A function that is called with the keyword arguments described below.
            The return value is used as the new result.

            Keyword arguments:
            
              stream_in
                The stream passed to the matcher.
    
              stream_out
                The stream returned from the matcher.
                
              core
                The core, if streams are being used, else ``None``.
            
              results
                A list of the results returned.
        '''
        self.__check(KARGS, function, False)
        return Global()[KARGS](self, function) 
    
    def __xor__(self, message):
        '''
        **self ^ message**
        
        Raise a SytaxError.
        
        :Parameters:
        
          message
            The message for the SyntaxError.
        '''
        return Global()[RAISE](self, message)
                             
    def __check(self, name, other, is_match):
        '''
        Provide some diagnostics if the syntax is completely mixed up.
        '''
        if not isinstance(other, str): # can go either way
            if is_match != isinstance(other, Matcher):
                if is_match:
                    msg = 'The operator {0} for {1} was applied to something ' \
                        'that is not a matcher ({2!r}).'
                else:
                    msg = 'The operator {0} for {1} was applied to a matcher ' \
                        '({2!r}).'
                msg += ' Check syntax and parentheses.'
                raise SyntaxError(msg.format(name, self.__class__.__name__, 
                                             other))

