''' Specs for core library classes / behaviours ''' 

from lancelot import MockSpec, Spec, grouping, verifiable, verify
from lancelot.comparators import Type
from lancelot.verification import AllVerifiable, ConsoleListener, \
                                  UnmetSpecification
from lancelot.specs.simple_fns import dont_raise_index_error, number_one, \
                                      raise_index_error, string_abc

class SilentListener(ConsoleListener):
    ''' AllVerifiable Listener that does not print any messages '''
    def __init__(self):
        ''' Override ConsoleListener to redirect write() calls '''
        super().__init__(self, self)
    def write(self, msg):
        ''' Write nothing so that messages are not printed '''
        pass
    
def silent_listener():
    ''' Descriptive fn: creates AllVerifiable instance with SilentListener '''
    return AllVerifiable(listener=SilentListener())

def unmet_specification():
    ''' Simple fn that raises UnmetSpecification. ''' 
    raise UnmetSpecification()

@grouping
class VerifiableDecoratorBehaviour:
    ''' A group of specifications for @verifiable decorator behaviour '''

    @verifiable
    def should_add_to_collation(self): 
        ''' verifiable should add fn to ALL_VERIFIABLE and return it '''
        all_verifiable = silent_listener()
    
        spec = Spec(verifiable)
        spec.verifiable(number_one, all_verifiable).should_be(number_one)
        
        num_verifiable_before = all_verifiable.total()
        spec.when(spec.verifiable(string_abc, all_verifiable))
        spec.then(all_verifiable.total).should_be(num_verifiable_before + 1)
    
    @verifiable
    def should_reject_non_callables(self):
        ''' verifiable should reject non-callable args '''
        msg = '1 is not callable, so it cannot be verifiable'
        Spec(verifiable).verifiable(1).should_raise(TypeError(msg))

@grouping
class AllVerifiableTotalBehaviour:
    ''' A group of specifications for AllVerifiable total() behaviour '''
    
    @verifiable
    def should_increment(self):
        ''' total() should increment as verifiable_fn is included '''
        spec = Spec(AllVerifiable, given=silent_listener)
        spec.total().should_be(0)
        
        spec.when(spec.include(raise_index_error))
        spec.then(spec.total()).should_be(1)
        
        spec.when(spec.include(dont_raise_index_error))
        spec.then(spec.total()).should_be(2)
    
    @verifiable
    def should_ignore_duplicates(self):
        ''' total() should ignore duplicate include()s '''
        spec = Spec(AllVerifiable, given=silent_listener)
        spec.when(spec.include(raise_index_error),
                  spec.include(raise_index_error))
        spec.then(spec.total()).should_be(1)

@verifiable
def all_verif_include_behaviour():
    ''' include() method should return self '''
    all_verifiable = silent_listener()
    spec = Spec(all_verifiable)
    spec.include(string_abc).should_be(all_verifiable)

@grouping
class AllVerifiableVerifyFnBehaviour:
    ''' A group of specifications for AllVerifiable verify_fn behaviour '''
    
    @verifiable
    def should_execute_fn(self):
        ''' verify_fn() should execute the fn '''
        a_list = []
        lambda_list_append = lambda: a_list.append(len(a_list))  
        spec = Spec(AllVerifiable, given=silent_listener)
        spec.when(spec.verify_fn(verifiable_fn=string_abc))
        spec.then(a_list.__len__).should_be(0)
        
        spec.when(spec.verify_fn(verifiable_fn=lambda_list_append))
        spec.then(a_list.__len__).should_be(1)

    @verifiable
    def should_handle_exceptions(self):
        ''' verify_fn() should handle exceptions gracefully '''
        spec = Spec(AllVerifiable, given=silent_listener)
        spec.verify_fn(raise_index_error).should_not_raise(Exception)
    
    @verifiable
    def should_return_0_or_1(self):
        ''' verify_fn() should return 1 for success, 0 for unmet 
        specification'''
        spec = Spec(AllVerifiable, given=silent_listener)
        spec.verify_fn(verifiable_fn=raise_index_error).should_be(0)
        spec.verify_fn(verifiable_fn=dont_raise_index_error).should_be(1)

@grouping
class AllVerifiableVerifyBehaviour:
    ''' A group of specifications for AllVerifiable verify() behaviour '''

    @verifiable
    def should_verify_each_item(self):
        ''' verify() should execute each included item '''
        a_list = []
        lambda_list_append1 = lambda: a_list.append(0)
        lambda_list_append2 = lambda: a_list.extend((1, 2)) 
        
        spec = Spec(AllVerifiable, given=silent_listener)
        spec.when(spec.include(lambda_list_append1), 
                  spec.include(lambda_list_append2), 
                  spec.verify())
        spec.then(a_list.__len__).should_be(3)

    @verifiable
    def should_return_all_results(self): 
        ''' verify() should return the result of all attempted / successful 
        verifications '''
        spec = Spec(AllVerifiable, given=silent_listener)
        spec.verify().should_be({'total':0, 'verified':0, 'unverified':0})

        spec = Spec(AllVerifiable, given=silent_listener)
        spec.when(spec.include(number_one))
        spec.then(spec.verify())
        spec.should_be({'total':1, 'verified':1, 'unverified':0})
    
        spec.when(spec.include(raise_index_error))
        spec.then(spec.verify())
        spec.should_be({'total':2, 'verified':1, 'unverified':1})
        
class RelatedVerifiables:
    ''' Simple class to use in specifications '''
    def verifiable1(self):
        ''' Something verifiable '''
        pass
    def verifiable2(self):
        ''' Something else verifiable '''
        pass
    
@grouping
class GroupingDecoratorBehaviour:
    ''' A group of specifications for @grouping decorator behaviour '''
    
    @verifiable
    def should_return_decorated_class(self):
        ''' grouping(cls) should return the cls '''
        spec = Spec(grouping)
        spec.grouping(RelatedVerifiables, silent_listener())
        spec.should_be(RelatedVerifiables)
        
    @verifiable
    def grouped_methods_should_verify(self):
        ''' grouping() methods should allow them to be executed & verified '''
        all_verifiable = silent_listener()
        def add_related_verifiables():
            grouping(RelatedVerifiables, all_verifiable)
            verifiable(RelatedVerifiables.verifiable1, all_verifiable)
            verifiable(RelatedVerifiables.verifiable2, all_verifiable)
        all_verifiable.add_related_verifiables = add_related_verifiables
           
        spec = Spec(all_verifiable)
        spec.when(spec.add_related_verifiables())
        spec.then(spec.total()).should_be(2)
        spec.then(spec.verify())
        spec.should_be({'total':2, 'verified':2, 'unverified':0})
        
    @verifiable
    def should_reject_non_classes(self):
        ''' grouping(not a type or class) should raise exception '''
        msg = '1 is not a type: perhaps you meant to use @verifiable instead?'
        Spec(grouping).grouping(1).should_raise(TypeError(msg))

@verifiable
def  all_verif_failfast_behaviour():
    ''' verify(fail_fast=True) should stop after the first unmet specification
    or unexpected exception'''    
    spec = Spec(AllVerifiable, given=silent_listener)
    spec.when(spec.include(raise_index_error), 
              spec.include(dont_raise_index_error))
    spec.then(spec.verify(fail_fast=True))
    spec.should_be({'total':2, 'verified':0, 'unverified':2, 'fail_fast':True})

    spec = Spec(AllVerifiable, given=silent_listener)
    spec.when(spec.include(unmet_specification), 
              spec.include(dont_raise_index_error))
    spec.then(spec.verify(fail_fast=True))
    spec.should_be({'total':2, 'verified':0, 'unverified':2, 'fail_fast':True})
     
@verifiable
def notification_behaviour(): 
    ''' listener should receive notifications AllVerifiable.verify() '''
    listener = MockSpec()
    all_verifiable_with_mock_listener = AllVerifiable(listener)
    results = {'total': 3, 'verified': 1, 'unverified': 2}
    
    spec = Spec(all_verifiable_with_mock_listener)
    spec.when(spec.include(string_abc), 
              spec.include(raise_index_error),
              spec.include(unmet_specification)) 
    spec.then(spec.verify())
    spec.should_collaborate_with(
        listener.all_verifiable_starting(all_verifiable_with_mock_listener),
        listener.verification_started(string_abc),
        listener.specification_met(string_abc),
        listener.verification_started(raise_index_error),
        listener.unexpected_exception(raise_index_error, Type(IndexError)),
        listener.verification_started(unmet_specification),
        listener.specification_unmet(unmet_specification, 
                                     Type(UnmetSpecification)),
        listener.all_verifiable_ending(all_verifiable_with_mock_listener, 
                                       results),
        and_result = results)

if __name__ == '__main__':
    verify()