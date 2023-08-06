'''
Functionality for wrapping / deferring / mocking __call__() invocations 

Intended public interface:
 Classes: WrapFunction, MockCall
 Functions: -
 Variables: -

Intended for internal use:
 Classes: MockResult
 Functions: _format_args()

Copyright 2009 by the author(s). All rights reserved 
'''

from lancelot.verification import UnmetSpecification
import logging, types

class WrapFunction:
    ''' Wraps a callable that is invoked later for its result() '''
    
    def __init__(self, within_spec, target, name):
        ''' Instance used within_spec, wrapping a named target __call__ '''
        self._within_spec = within_spec
        self._target = target
        if type(target) == types.FunctionType and target.__name__ == name:
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
        ''' Perform the actual invocation on the target''' 
        logging.debug('wrapper executing %s %s %s %s' % \
                      (self._target, self._name, self._args, self._kwds))
        if self._name:
            call = getattr(self._target, self._name)
            return call(*self._args, **self._kwds)
        return self._target(*self._args, **self._kwds)

def _format_args(args, kwds):
    ''' Format args for prettier display '''
    formatted_args = ['%r' % arg for arg in args]
    formatted_args.extend(['%s=%r' % (kwd, value) 
                           for kwd, value in kwds.items()])
    return '(%s)' % ','.join(formatted_args)
    
class MockCall:
    ''' Wraps an instance of a collaboration for a Mock Specification '''
      
    def __init__(self, mock_spec, name):
        ''' An instance is created by a "mock_spec" for a given method "name" 
        A default instance will_return(None), and expects invocation once() '''
        self._mock_spec = mock_spec
        self._name = name
        self._specified_args = ()
        self._specified_kwds = {}
        self._specified_result = MockResult(self)
        
    def __call__(self, *args, **kwds):
        ''' Receive the args specified in a should_collaborate() block 
        while in "specification" mode '''
        self._specified_args = args
        self._specified_kwds = kwds
        return self
        
    def will_return(self, *values):
        ''' Specify the return value from the result of the collaboration.
        If a list of values is given they will be iterated over on each
        occasion the collaboration occurs, otherwise the same value will be
        used every time '''
        self._specified_result.supplies(*values)
        return self

    def will_raise(self, *exceptions):
        ''' Specify the exceptions raised from the collaboration.
        If a list of values is given they will be iterated over on each
        occasion the collaboration occurs, otherwise the same value will be
        used every time '''
        self._specified_result.raises(*exceptions)
        return self
    
    def once(self):
        ''' Specify that the collaboration will happen once (the default) '''
        return self.times(1)
    
    def twice(self):
        ''' Specify that the collaboration will happen twice '''
        return self.times(2)
    
    def times(self, num_times):
        ''' Specify that the collaboration will happen num_times '''
        self._specified_result.times(num_times)
        return self
    
    def start_collaborating(self):
        ''' Switch from "specification" to "collaboration" mode '''
        self._mock_spec.start_collaborating()
        return self._mock_spec
    
    def description(self):
        ''' Describe this part of the should_collaborate specification '''
        return 'should be collaborating with %s%s' % \
            (self._name, 
             _format_args(self._specified_args, self._specified_kwds))
    
    def result_of(self, name):
        ''' Check that the collaboration is as specified,
        and return the current value specified by will_return '''
        if name != self._name:
            msg = '%s, not %s()' % (self.description(), name)
            raise UnmetSpecification(msg)
        return self._current_result
    
    def _verify(self, *args, **kwds):
        ''' Check that the collaboration is as specified '''
        if self._mock_spec.comparable_args(self._specified_args) != args \
        or self._mock_spec.comparable_kwds(self._specified_kwds) != kwds:
            supplied = _format_args(args, kwds)
            msg = '%s, not %s%s' % (self.description(), self._name, supplied)
            raise UnmetSpecification(msg)

    def _current_result(self, *args, **kwds):
        ''' The current will_return value for this collaboration '''
        self._verify(*args, **kwds)
        result = self._specified_result.next()
        if self._specified_result.times_remaining() == 0:
            self._mock_spec.collaboration_over(self)
        return result

class MockResult:
    ''' Class responsible for supplying result values for a MockCall '''
    
    def __init__(self, mock_call):
        ''' An instance for a mock call.'''
        self._mock_call = mock_call
        self._values = [None]
        self._specified_times = 1
        self._is_raising = False
        
    def supplies(self, *values):
        ''' Specify the result values to use.
        len(values) must be 1, or == self._specified_times. '''
        self._values = []
        self._values.extend(values)
        self.times(self._specified_times)
        
    def raises(self, *exceptions):
        ''' Specify the exceptions to raise. Overrides any previous calls to  
        supplies(). len(exceptions) must be 1, or == self._specified_times. '''
        self._is_raising = True
        self.supplies(*exceptions)
        
    def times(self, num_times):
        ''' Supply the result value num_times '''
        self._specified_times = num_times
        if len(self._values) == 1 and num_times > 1:
            self._values = [self._values[0] for i in range(0, num_times)]
        elif len(self._values) != num_times:
            msg = 'num specified return values %s does not match num times %s'
            raise ValueError(msg % (len(self._values), num_times))
    
    def specified_times(self):
        ''' The number of times the result value will be supplied '''
        return self._specified_times
    
    def times_remaining(self):
        ''' The remaining times that the result value to be supplied '''
        return len(self._values)
    
    def next(self):
        ''' Supply the next result value '''
        if self.times_remaining() == 0:
            msg = '%s only %s successive times' % \
                (self._mock_call.description(), self.specified_times())
            raise UnmetSpecification(msg)
        next_value = self._values.pop(0)
        if self._is_raising:
            raise next_value
        return next_value