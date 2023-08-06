''' Specs for core library classes / behaviours ''' 

from lancelot import Spec, grouping, verifiable, verify
from lancelot.calling import WrapFunction
from lancelot.specs.simple_fns import number_one

@grouping
class WrapFunctionBehaviour:
    ''' A group of specifications for WrapFunction behaviour '''
    
    @verifiable
    def call_should_return_spec(self):
        ''' __call__() should return the spec that "owns" the WrapFunction '''
        spec = Spec('a') 
        Spec(WrapFunction(spec, None, None)).__call__().should_be(spec)

    @verifiable
    def result_invoke_underlying(self):
        '''result() should invoke the wrapped function and return its result'''
        spec = Spec(WrapFunction(None, 'a', 'startswith'))
        spec.when(spec.__call__('a')).then(spec.result()).should_be(True)
        spec.when(spec.__call__('b')).then(spec.result()).should_be(False)
    
    @verifiable
    def should_wrap_modulefunctions(self):
        '''Wrapping module functions and instance methods should be possible'''
        spec = Spec(WrapFunction(None, number_one, 'number_one'))
        spec.when(spec.__call__()).then(spec.result()).should_be(1)

if __name__ == '__main__':
    verify()
