
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
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
The main configuration object and various standard configurations.
'''

from lepl.monitor import MultipleMonitors

# A major driver for this being separate is that it decouples dependency loops


class Configuration(object):
    '''
    Encapsulate various parameters that describe how the matchers are
    rewritten and evaluated.
    '''
    
    __default = None
    __managed = None
    
    def __init__(self, rewriters=None, monitors=None):
        '''
        `rewriters` Are functions that take and return a matcher tree.  They
        can add memoisation, restructure the tree, etc.  They are applied left
        to right.
        
        `monitors` Subclasses of `MonitorInterface` that will be
        invoked by `trampoline()`.  Multiple values are combined into a single 
        monitor.  Note that monitors are typically stateful and, since a
        configuration can be reused, a created on use by function invocation.
        So a monitor is typically defined as ``lambda: SomeInstance(...)``. 
        '''
        self.rewriters = [] if rewriters is None else rewriters 
        if not monitors:
            self.monitor = None
        elif len(monitors) == 1:
            self.monitor = monitors[0]()
        else:
            self.monitor = MultipleMonitors(monitors)
        
    @classmethod    
    def default(cls):
        '''
        Generate a default configuration instance.  Currently this flattens
        nested `And()` and `Or()` instances;
        adds memoisation (which allows left recursion, but may alter the order 
        in which matches are returned for ambiguous grammars);
        adds a lexer if any tokens are found (assuming unicode input);
        and supports tracing (which is initially disabled, but can be enabled
        using the `Trace()` matcher).
        '''
        if cls.__default is None:
            from lepl.lexer.rewriters import lexer_rewriter
            from lepl.rewriters import flatten, compose_transforms, auto_memoize
            from lepl.trace import TraceResults
            cls.__default = \
                Configuration(
                    rewriters=[flatten, compose_transforms, lexer_rewriter(),
                               auto_memoize()],
                    monitors=[TraceResults(False)])
        return cls.__default
    
    @classmethod
    def managed(cls):
        '''
        Add generator management (no limit, but enables `Commit()`) to the
        default configuration.
        '''
        if cls.__managed is None:
            from lepl.lexer.rewriters import lexer_rewriter
            from lepl.manager import GeneratorManager
            from lepl.rewriters import flatten, compose_transforms, auto_memoize
            from lepl.trace import TraceResults
            cls.__managed = \
                Configuration(
                    rewriters=[flatten, compose_transforms, lexer_rewriter(),
                               auto_memoize()],
                    monitors=[TraceResults(False), 
                              GeneratorManager(queue_len=0)])
        return cls.__managed
    
    @classmethod    
    def tokens(cls, alphabet):
        '''
        Tokens for a unicode alphabet are already suppored by the default
        configuration; this allows other alphabets to be supported.
        
        If alphabet is not specified, Unicode is assumed.
        '''
        from lepl.lexer.rewriters import lexer_rewriter
        from lepl.regexp.unicode import UnicodeAlphabet
        from lepl.rewriters import flatten, compose_transforms, auto_memoize
        from lepl.trace import TraceResults
        alphabet = UnicodeAlphabet.instance() if alphabet is None else alphabet
        return Configuration(
                rewriters=[flatten, compose_transforms,
                           lexer_rewriter(alphabet), auto_memoize()],
                monitors=[TraceResults(False)])
    
    @classmethod
    def nfa(cls, alphabet=None):
        '''
        Rewrite fragments of the matcher graph as regular expressions.
        This uses a pushdown automaton and should return all possible matches.
        
        If alphabet is not specified, Unicode is assumed.
        '''
        from lepl.lexer.rewriters import lexer_rewriter
        from lepl.regexp.rewriters import regexp_rewriter
        from lepl.regexp.unicode import UnicodeAlphabet
        from lepl.rewriters import flatten, compose_transforms, auto_memoize
        from lepl.trace import TraceResults
        alphabet = UnicodeAlphabet.instance() if alphabet is None else alphabet
        return Configuration(
                rewriters=[flatten, compose_transforms,
                           regexp_rewriter(alphabet, False),
                           compose_transforms, lexer_rewriter(alphabet),
                           auto_memoize()],
                monitors=[TraceResults(False)])
    
    @classmethod
    def dfa(cls, alphabet=None):
        '''
        Rewrite fragments of the matcher graph as regular expressions.
        This uses a finite automaton and returns only the greediest match,
        so may produce changed results with ambiguous parsers.
        
        Note - this assumes that the value being parsed is Unicode text.
        '''
        from lepl.lexer.rewriters import lexer_rewriter
        from lepl.regexp.matchers import DfaRegexp
        from lepl.regexp.rewriters import regexp_rewriter
        from lepl.regexp.unicode import UnicodeAlphabet
        from lepl.rewriters import flatten, compose_transforms, auto_memoize
        from lepl.trace import TraceResults
        alphabet = UnicodeAlphabet.instance() if alphabet is None else alphabet
        return Configuration(
                rewriters=[flatten, compose_transforms,
                           regexp_rewriter(UnicodeAlphabet.instance(), 
                                           False, DfaRegexp),
                           compose_transforms, lexer_rewriter(alphabet),
                           auto_memoize()],
                monitors=[TraceResults(False)])
    
