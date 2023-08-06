
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
Tools for logging and tracing.
'''

from itertools import count
from traceback import print_exc

from lepl.monitor import ExposedMonitor
from lepl.support import CircularFifo


class TraceResults(ExposedMonitor):
    '''
    A basic logger (implemented as a monitor - `MonitorInterface`)
    that records the flow of control during parsing.  It can be controlled by 
    `Trace()`.
    '''
    
    def __init__(self, enabled=False):
        super(TraceResults, self).__init__()
        self.generator = None
        self.depth = -1
        self.action = None
        self.enabled = 1 if enabled else 0
    
    def next_iteration(self, epoch, value, exception, stack):
        self.epoch = epoch
        self.depth = len(stack)
    
    def before_next(self, generator):
        if self.enabled > 0:
            self.generator = generator
            self.action = 'next({0})'.format(generator.describe)
    
    def after_next(self, value):
        if self.enabled > 0:
            self.result(value, self.fmt_result(value))
    
    def before_throw(self, generator, value):
        if self.enabled > 0:
            self.generator = generator
            if type(value) is StopIteration:
                self.action = ' stop -> {0}({1!s})'.format(generator.matcher.describe, generator.stream)
            else:
                self.action = '{2!r} -> {0}({1!s})'.format(generator.matcher.describe, generator.stream, value)
    
    def after_throw(self, value):
        if self.enabled > 0:
            self.result(value, self.fmt_result(value))
    
    def before_send(self, generator, value):
        if self.enabled > 0:
            self.generator = generator
            self.action = '{1!r} -> {0}'.format(generator.matcher.describe, value)
    
    def after_send(self, value):
        if self.enabled > 0:
            self.result(value, self.fmt_result(value))
    
    def exception(self, value):
        if self.enabled > 0:
            if type(value) is StopIteration:
                self.done(self.fmt_done())
            else:
                self.error(value, self.fmt_result(value))
        
    def fmt_result(self, value):
        (stream, depth) = self.fmt_stream_depth() 
        return '{0:05d} {1:11s} {2} ({3:04d}) {4:03d} {5:>60s} -> {6!r}' \
                .format(self.epoch, 
                        stream,
                        self.fmt_location(self.generator.stream),
                        depth,
                        self.depth,
                        self.action,
                        value)
                
    def fmt_stream_depth(self):
        try:
            depth = self.generator.stream.depth()
            stream = str(self.generator.stream)
        except:
            depth = -len(self.generator.stream)
            if len(self.generator.stream) > 10:
                stream = repr(self.generator.stream[0:7]) + '...'
            else:
                stream = repr(self.generator.stream)
        return (stream, depth)
        
    def fmt_done(self):
        (stream, depth) = self.fmt_stream_depth() 
        return '{0:05d} {1:11s} {2} ({3:04d}) {4:03d} {5:>60s} -> stop' \
                .format(self.epoch, 
                        stream,
                        self.fmt_location(self.generator.stream),
                        depth,
                        self.depth,
                        self.action)
                
    def fmt_location(self, stream):
        try:
            (line, char) = stream.location()
            if line < 0:
                return '  eof  '
            else:
                return '{0:3d}.{1:<3d}'.format(line, char)
        except:
            return '<unknown>'

    def yield_(self, value):
        if self.enabled > 0:
            self._info(self.fmt_final_result(value))
        
    def raise_(self, value):
        if self.enabled > 0:
            if type(value) is StopIteration:
                self._info(self.fmt_final_result('raise {0!r}'.format(value)))
            else:
                self._warn(self.fmt_final_result('raise {0!r}'.format(value)))
        
    def fmt_final_result(self, value):
        return '{0:05d}                            {1:03d} {2} {3}' \
                .format(self.epoch,
                        self.depth,
                        ' ' * 63,
                        value)

    def result(self, value, text):
        (self._info if type(value) is tuple else self._debug)(text)    

    def error(self, value, text):
        self._warn(text)    

    def done(self, text):
        self._debug(text)
        
    def switch(self, increment):
        self.enabled += increment
    

class RecordDeepest(TraceResults):
    '''
    A logger (implemented as a monitor - `MonitorInterface`)
    that records the deepest match found during a parse.
    '''
    
    def __init__(self, n_before=6, n_results_after=2, n_done_after=2):
        super(RecordDeepest, self).__init__(enabled=True)
        self.n_before = n_before
        self.n_results_after = n_results_after
        self.n_done_after = n_done_after
        self._limited = CircularFifo(n_before)
        self._before = []
        self._results_after = []
        self._done_after = []
        self._deepest = -1e99
        self._countdown_result = 0
        self._countdown_done = 0
        
    def result(self, value, text):
        if type(value) is tuple:
            self.record(True, text)

    def error(self, value, text):
        self.record(True, text)

    def done(self, text):
        self.record(False, text)

    def record(self, is_result, text):
        stream = self.generator.stream
        try:
            depth = stream.depth()
        except:
            depth = -len(stream)
        if depth >= self._deepest and is_result:
            self._deepest = depth
            self._countdown_result = self.n_results_after
            self._countdown_done = self.n_done_after
            self._before = list(self._limited)
            self._results_after = []
            self._done_after = []
        elif is_result and self._countdown_result:
            self._countdown_result -= 1
            self._results_after.append(text)
        elif not is_result and self._countdown_done:
            self._countdown_done -= 1
            self._done_after.append(text)
        self._limited.append(text)
        
    def yield_(self, value):
        self._deepest = 0
        self._limited.clear()
        self.display()
        
    def raise_(self, value):
        self._deepest = 0
        self._limited.clear()
        self.display()
        
    def display(self):
        self._info(self.format())
        
    def format(self):
        return '\nUp to {0} matches before and including longest match:\n{1}\n' \
            'Up to {2} failures following longest match:\n{3}\n' \
            'Up to {4} successful matches following longest match:\n{5}\n' \
            .format(self.n_before, '\n'.join(self._before),
                    self.n_done_after, '\n'.join(self._done_after),
                    self.n_results_after, '\n'.join(self._results_after))
        
