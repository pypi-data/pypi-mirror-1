''' Specs for core library classes / behaviours ''' 

from lancelot import MockSpec, Spec, verifiable, verify
from lancelot.comparators import Type
from lancelot.verification import AllVerifiable, ConsoleListener, \
                                  UnmetSpecification
from lancelot.specs.simple_fns import dont_raise_index_error, number_one, \
                                      raise_index_error, string_abc

class SilentListener(ConsoleListener):
    def __init__(self):
        super().__init__(self, self)
    def write(self, msg):
        pass
    
def all_verifiable_with_silent_listener():
    return AllVerifiable(listener=SilentListener())

@verifiable
def verifiable_annotation_should_add_fn_to_all_verifiable_and_return_it():
    all_verifiable = all_verifiable_with_silent_listener()

    spec = Spec(verifiable)
    spec.verifiable(number_one, all_verifiable).should_be(number_one)
    
    num_verifiable_before = all_verifiable.total()
    spec.when(spec.verifiable(number_one, all_verifiable))
    spec.then(all_verifiable.total).should_be(num_verifiable_before + 1)

@verifiable
def all_verifiable_total_should_increment_as_verifiable_fn_is_included():
    spec = Spec(AllVerifiable, given=all_verifiable_with_silent_listener)
    spec.total().should_be(0)
    
    spec.when(spec.include(raise_index_error))
    spec.then(spec.total()).should_be(1)
    
    spec.when(spec.include(dont_raise_index_error))
    spec.then(spec.total()).should_be(2)

@verifiable
def all_verifiable_include_should_return_self():
    all_verifiable = all_verifiable_with_silent_listener()
    spec = Spec(all_verifiable)
    spec.include(string_abc).should_be(all_verifiable)

@verifiable
def all_verifiable_verify_fn_should_execute_the_fn():
    a_list = []
    lambda_list_append = lambda: a_list.append(len(a_list))  
    
    spec = Spec(AllVerifiable, given=all_verifiable_with_silent_listener)
    spec.when(spec._verify_fn(verifiable_fn=string_abc))
    spec.then(a_list.__len__).should_be(0)
    
    spec.when(spec._verify_fn(verifiable_fn=lambda_list_append))
    spec.then(a_list.__len__).should_be(1)

@verifiable
def all_verifiable_verify_fn_should_handle_exceptions_gracefully():
    spec = Spec(AllVerifiable, given=all_verifiable_with_silent_listener)
    spec._verify_fn(raise_index_error).should_not_raise(Exception)
    
@verifiable
def all_verifiable_verify_fn_should_return_1_for_success_0_for_failure():
    spec = Spec(AllVerifiable, given=all_verifiable_with_silent_listener)
    spec._verify_fn(verifiable_fn=raise_index_error).should_be(0)
    spec._verify_fn(verifiable_fn=dont_raise_index_error).should_be(1)
    
@verifiable
def all_verifiable_verify_should_verify_each_included_item():
    a_list = []
    lambda_list_append1 = lambda: a_list.append(0)
    lambda_list_append2 = lambda: a_list.extend((1, 2)) 
    
    spec = Spec(AllVerifiable, given=all_verifiable_with_silent_listener)
    spec.when(spec.include(lambda_list_append1), 
              spec.include(lambda_list_append2), 
              spec.verify())
    spec.then(a_list.__len__).should_be(3)

@verifiable
def all_verifiable_verify_should_return_number_of_verifications():
    spec = Spec(AllVerifiable, given=all_verifiable_with_silent_listener)
    spec.verify().should_be({'total':0, 'verified':0, 'unverified':0})

    spec.when(spec.include(number_one))
    spec.then(spec.verify())
    spec.should_be({'total':1, 'verified':1, 'unverified':0})

    spec.when(spec.include(raise_index_error))
    spec.then(spec.verify())
    spec.should_be({'total':2, 'verified':1, 'unverified':1})

@verifiable
def listener_should_receive_notifications_from_all_verifiable_verify():
    
    def unmet_specification():
        ''' Simple fn that raises UnmetSpecification. ''' 
        raise UnmetSpecification()

    listener = MockSpec()
    all_verifiable_with_mock_listener = AllVerifiable(listener)
    results = {'total': 3, 'verified': 1, 'unverified': 2}
    
    spec = Spec(all_verifiable_with_mock_listener)
    spec.when(spec.include(string_abc), 
              spec.include(raise_index_error),
              spec.include(unmet_specification)) 
    spec.then(spec.verify())
    spec.should_collaborate_with(listener.all_verifiable_starting(all_verifiable_with_mock_listener),
                                 listener.verification_started(string_abc),
                                 listener.specification_met(string_abc),
                                 listener.verification_started(raise_index_error),
                                 listener.unexpected_exception(raise_index_error, Type(IndexError)),
                                 listener.verification_started(unmet_specification),
                                 listener.specification_unmet(unmet_specification, Type(UnmetSpecification)),
                                 listener.all_verifiable_ending(all_verifiable_with_mock_listener, results),
                                 and_result = results)

if __name__ == '__main__':
    verify()