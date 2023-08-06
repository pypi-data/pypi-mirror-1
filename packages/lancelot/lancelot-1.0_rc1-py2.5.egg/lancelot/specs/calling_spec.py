''' Specs for core library classes / behaviours ''' 

from lancelot import Spec, verifiable, verify
from lancelot.calling import WrapFunction
from lancelot.specs.simple_fns import number_one

@verifiable
def calling_wrapper_should_return_owning_spec():
    spec = Spec('a') 
    Spec(WrapFunction(spec, None, None)).__call__().should_be(spec)

def wrap_function_string_a_startswith():    
    return WrapFunction(Spec('a'), 'a', 'startswith')

@verifiable
def after_calling_wrapper_then_result_should_be_result_of_calling_target():
    spec = Spec(WrapFunction, given=wrap_function_string_a_startswith)
    spec.when(spec.__call__('a')).then(spec.result()).should_be(True)
    spec.when(spec.__call__('b')).then(spec.result()).should_be(False)
    
@verifiable
def wrap_function_should_wrap_module_fns_as_well_as_object_methods():
    spec = Spec(WrapFunction(None, number_one, 'number_one'))
    spec.when(spec.__call__()).then(spec.result()).should_be(1)

if __name__ == '__main__':
    verify()