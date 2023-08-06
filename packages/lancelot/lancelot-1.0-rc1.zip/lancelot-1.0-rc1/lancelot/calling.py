'''
Functionality for wrapping / deferring / mocking __call__() invocations 

Intended public interface:
 Classes: WrapFunction, MockCall
 Functions: -
 Variables: -

Intended for internal use:
 -

Copyright 2009 by the author(s). All rights reserved 
'''

from lancelot.verification import UnmetSpecification
import logging

class WrapFunction:
    ''' Wraps a callable that is invoked when the specification is verified '''
    
    def __init__(self, within_spec, target, name):
        ''' Instance used within_spec, wrapping a named target invocation '''
        self._within_spec = within_spec
        self._target = target
        if type(target).__name__ == 'function' and target.__name__ == name:
            self._name = ''
        else:
            self._name = name
        self._args = ()
        self._kwds = {}

    def __call__(self, *args, **kwds):
        ''' Capture the args to be used for the later invocation ''' 
        self._args = args
        self._kwds = kwds
        return self._within_spec
    
    def result(self):
        ''' Perform the actual invocation ''' 
        logging.debug('wrapper executing %s %s %s %s' % \
                      (self._target, self._name, self._args, self._kwds))
        if self._name:
            call = getattr(self._target, self._name)
            return call(*self._args, **self._kwds)
        return self._target(*self._args, **self._kwds)

class MockCall:
    ''' Wraps an instance of a collaboration for a Mock Specification '''
      
    def __init__(self, mock_spec, name):
        ''' An instance is created by a "mock_spec" for a given method "name" 
        A default instance will_return(None), and expects invocation once() '''
        self._mock_spec = mock_spec
        self._name = name
        self._specified_args = ()
        self._specified_kwds = {}
        self._specified_result = (None,)
        self._successive_times = 1
        self._current_time = 0
        
    def __call__(self, *args, **kwds):
        ''' Receive the args specified in a should_collaborate... block 
        while in "specification" mode '''
        self._specified_args = self._mock_spec.comparable_args(args)
        self._specified_kwds = self._mock_spec.comparable_kwds(kwds)
        return self
        
    def will_return(self, *values):
        ''' Specify the return value from the result of the collaboration.
        If a list of values is given they will be iterated over on each
        occasion the collaboration occurs, otherwise the same value will be
        used every time '''
        self._specified_result = values
        return self
    
    def once(self):
        ''' Specify that the collaboration will happen once (the default) '''
        return self.times(1)
    
    def twice(self):
        ''' Specify that the collaboration will happen twice '''
        return self.times(2)
    
    def times(self, num_times):
        ''' Specify that the collaboration will happen num_times '''
        self._successive_times = num_times
        return self
    
    #TODO: ugly?
    def start_collaborating(self):
        ''' Switch from "specification" to "collaboration" mode '''
        self._mock_spec.start_collaborating()
        return self._mock_spec
    
    def description(self):
        ''' Describe this part of the should_collaborate specification '''
        return 'should be collaborating with %s%s' % \
            (self._name, self._format_specified_args())
    
    def _format_specified_args(self):
        ''' Format the args specified in a should_collaborate... block '''
        return self._format_args(self._specified_args, self._specified_kwds)

    def _format_args(self, args, kwds):
        ''' Format args for prettier display '''
        formatted_args = ['%r' % arg for arg in args]
        formatted_args.extend(['%s=%r' % (kwd, value) 
                               for kwd, value in kwds.items()])
        return '(%s)' % ','.join(formatted_args)
    
    def result_of(self, name):
        ''' Check that the collaboration is as specified,
        and return the current value specified by will_return '''
        if name == self._name:
            self._remove_from_spec()
            return self._current_result
        raise UnmetSpecification('%s, not %s()' % (self.description(), name))
    
    #TODO: ugly?
    def _remove_from_spec(self):
        ''' Check the number of times that this collaboration was specified
        to occur, and remove this collaboration from those remaining '''
        self._current_time += 1
        if self._successive_times == self._current_time:
            self._mock_spec.collaboration_verified(self)
    
    def _verify(self, *args, **kwds):
        ''' Check that the collaboration is as specified '''
        if self._successive_times < self._current_time:
            msg = '%s only %s successive times' % \
                (self.description(), self._successive_times)
            raise UnmetSpecification(msg)
        if self._specified_args == args and self._specified_kwds == kwds:
            return 
        supplied = self._format_args(args, kwds)
        msg = '%s, not %s%s' % (self.description(), self._name, supplied)
        raise UnmetSpecification(msg)

    def _current_result(self, *args, **kwds):
        ''' The current will_return value for this collaboration '''
        self._verify(*args, **kwds)
        try:
            return self._specified_result[self._current_time -1]
        except IndexError:
            return self._specified_result[0]
        return result
