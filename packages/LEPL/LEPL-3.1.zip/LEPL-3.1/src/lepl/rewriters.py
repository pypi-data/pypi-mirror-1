
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
Rewriters modify the graph of matchers before it is used to generate a 
parser.
'''

from lepl.graph import Visitor, preorder, loops
from lepl.operators import Matcher


def clone(node, args, kargs):
    '''
    Clone including matcher-specific attributes.
    '''
    from lepl.graph import clone as old_clone
    copy = old_clone(node, args, kargs)
    copy_standard_attributes(node, copy)
    return copy

def copy_standard_attributes(node, copy, describe=True, transform=True):
    '''
    Handle the additional attributes that matchers may have.
    '''
    from lepl.matchers import Transformable
    if isinstance(node, Transformable) and transform:
        copy.function = node.function
    if describe:
        copy.describe = node.describe 


class DelayedClone(Visitor):    
    '''
    A version of `Clone()` that uses `Delayed()` rather
    that `Proxy()` to handle circular references.  Also caches results to
    avoid duplications.
    '''
    
    def __init__(self, clone_=clone):
        super(DelayedClone, self).__init__()
        self._clone = clone_
        self._delayeds = {}
        self._visited = {}
        self._node = None
    
    def loop(self, _node):
        '''
        This is called for nodes that are arguments to Delayed.  Since we
        do not know those values yet, we return None.  We will fix the Delayed
        instances later.
        '''
        return None
    
    def node(self, node):
        '''
        Store the current node.
        '''
        self._node = node
        
    def constructor(self, *args, **kargs):
        '''
        Clone the node, taking care to handle loops.
        '''
        # delayed import to avoid dependency loops
        from lepl.matchers import Delayed
        if isinstance(self._node, Delayed):
            copy = self._clone(self._node, args, kargs)
            if self._node in self._delayeds:
                # we already created a replacement for this node, but it's
                # matcher may contain None (from loop), so fix it
                # up and return it.
                self._delayeds[self._node].matcher = copy.matcher
                copy = self._delayeds[self._node]
            else:
                # otherwise, store this version for future use
                self._delayeds[self._node] = copy
        else:
            if self._node not in self._visited:
                self._visited[self._node] = self._clone(self._node, args, kargs)
            copy = self._visited[self._node]
        return copy
    
    def leaf(self, value):
        '''
        Leaf values are unchanged.
        '''
        return value
    
    
def post_clone(function):
    '''
    Generate a clone function that applies the given function to the newly
    constructed node, except for Delayed instances (which are effectively
    proxies and so have no functionality of their own (so, when used with 
    `DelayedClone`, effectively performs a map on the graph).
    '''
    from lepl.matchers import Delayed
    def new_clone(node, args, kargs):
        '''
        Apply function as well as clone.
        '''
        copy = clone(node, args, kargs)
        if not isinstance(node, Delayed):
            copy = function(copy)
        return copy
    return new_clone


def flatten(graph):
    '''
    A rewriter that flattens `And` and `Or` lists.
    '''
    from lepl.matchers import And, Or
    def new_clone(node, old_args, kargs):
        '''
        The flattening cloner.
        '''
        table = {And: '*matchers', Or: '*matchers'}
        if type(node) in table:
            attribute_name = table[type(node)]
            new_args = []
            for arg in old_args:
                if type(arg) is type(node) \
                        and not arg.function \
                        and not node.function:
                    if attribute_name.startswith('*'):
                        new_args.extend(getattr(arg, attribute_name[1:]))
                    else:
                        new_args.append(getattr(arg, attribute_name))
                else:
                    new_args.append(arg)
        else:
            new_args = old_args
        return clone(node, new_args, kargs)
    return graph.postorder(DelayedClone(new_clone), Matcher)


def compose_transforms(graph):
    '''
    A rewriter that joins adjacent transformations into a single
    operation, avoiding trampolining in some cases.
    '''
    from lepl.matchers import Transform, Transformable
    def new_clone(node, args, kargs):
        '''
        The joining cloner.
        '''
        # must always clone to expose the matcher (which was cloned earlier - 
        # it is not node.matcher)
        copy = clone(node, args, kargs)
        if isinstance(copy, Transform) \
                and isinstance(copy.matcher, Transformable):
            return copy.matcher.compose(copy)
        else:
            return copy
    return graph.postorder(DelayedClone(new_clone), Matcher)


def memoize(memoizer):
    '''
    A rewriter that adds the given memoizer to all nodes in the matcher
    graph.
    '''
    def rewriter(graph):
        '''
        Embed the memoizer within the cloner.
        '''
        return graph.postorder(DelayedClone(post_clone(memoizer)), Matcher)
    return rewriter


def auto_memoize(conservative=None):
    '''
    Generate an all-purpose memoizing rewriter.  It is typically called after
    flattening and composing transforms.
    
    This rewrites the matcher graph to:
    1 - rewrite recursive `Or` calls so that terminating clauses are
    checked first.
    2 - add memoizers as appropriate
    
    This rewriting may change the order in which different results for
    an ambiguous grammar are returned.
    
    If ``conservative`` is not specified then `optimize_or(False)` and
    `context_memoize(True)` are used.  This gives conservative memoisation 
    with minimal rewriting of alternatives.
    '''
    def rewriter(graph):
        '''
        Apply the two sub-rewriters in turn.
        '''
        graph = optimize_or(False if conservative is None 
                            else conservative)(graph)
        graph = context_memoize(True if conservative is None 
                                else conservative)(graph)
        return graph
    return rewriter


def left_loops(node):
    '''
    Return (an estimate of) all left-recursive loops from the given node.
    
    We cannot know for certain whether a loop is left recursive because we
    don't know exactly which parsers will consume data.  But we can estimate
    by assuming that all matchers eventually (ie via their children) consume
    something.  We can also improve that slightly by ignoring `Lookahead`.
    
    So we estimate left-recursive loops as paths that start and end at
    the given node, and which are first children of intermediate nodes
    unless the node is `Or`, or the preceding matcher is a
    `Lookahead`.  
    
    Each loop is a list that starts and ends with the given node.
    '''
    from lepl.matchers import Or, Lookahead
    stack = [[node]]
    known = set([node]) # avoid getting lost in embedded loops
    while stack:
        ancestors = stack.pop()
        parent = ancestors[-1]
        if isinstance(parent, Matcher):
            for child in parent:
                family = list(ancestors) + [child]
                if child is node:
                    yield family
                else:
                    if child not in known:
                        stack.append(family)
                        known.add(child)
                if not isinstance(parent, Or) and \
                        not isinstance(child, Lookahead):
                    break
    
                    
def either_loops(node, conservative):
    '''
    Select between the conservative and liberal loop detection algorithms.
    '''
    if conservative:
        return loops(node, Matcher)
    else:
        return left_loops(node)
    

def optimize_or(conservative=True):
    '''
    Generate a rewriter that re-arranges `Or` matcher contents for
    left--recursive loops.
    
    When a left-recursive rule is used, it is much more efficient if it
    appears last in an `Or` statement, since that forces the alternates
    (which correspond to the terminating case in a recursive function)
    to be tested before the LMemo limit is reached.
    
    This rewriting may change the order in which different results for
    an ambiguous grammar are returned.
    
    `conservative` refers to the algorithm used to detect loops; False
    may classify some left--recursive loops as right--recursive.
    '''
    from lepl.matchers import Delayed, Or
    def rewriter(graph):
        '''
        The Or-rewriting rewriter.
        '''
        for delayed in [x for x in preorder(graph, Matcher) 
                        if isinstance(x, Delayed)]:
            for loop in either_loops(delayed, conservative):
                for i in range(len(loop)):
                    if isinstance(loop[i], Or):
                        # we cannot be at the end of the list here, since that
                        # is a Delayed instance
                        matchers = loop[i].matchers
                        target = loop[i+1]
                        # move target to end of list
                        index = matchers.index(target)
                        del matchers[index]
                        matchers.append(target)
        return graph
    return rewriter


def context_memoize(conservative=True):
    '''
    Generate a memoizer that only applies LMemo to left recursive loops.
    Everything else can use the simpler RMemo.
    
    `conservative` refers to the algorithm used to detect loops; False
    may classify some left--recursive loops as right--recursive.
    '''
    from lepl.matchers import Delayed
    from lepl.memo import LMemo, RMemo
    def rewriter(graph):
        '''
        Detect loops and clone appropriately.
        '''
        dangerous = set()
        for delayed in [x for x in preorder(graph, Matcher) 
                        if isinstance(x, Delayed)]:
            for loop in either_loops(delayed, conservative):
                for node in loop:
                    dangerous.add(node)
        def new_clone(node, args, kargs):
            '''
            Clone with the appropriate memoizer 
            (cannot use post_clone as need to test original)
            '''
            copy = clone(node, args, kargs)
            if isinstance(node, Delayed):
                # no need to memoize the proxy (if we do, we also break 
                # rewriting, since we "hide" the Delayed instance)
                return copy
            elif node in dangerous:
                return LMemo(copy)
            else:
                return RMemo(copy)
        return graph.postorder(DelayedClone(new_clone), Matcher)
    return rewriter

