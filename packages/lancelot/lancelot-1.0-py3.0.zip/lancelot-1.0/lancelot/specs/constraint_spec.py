''' Specs for core library classes / behaviours ''' 

from lancelot import MockSpec, Spec, grouping, verifiable, verify
from lancelot.constraints import Constraint, CollaborateWith, Not, Raise, \
                                 EqualsEquals
from lancelot.verification import UnmetSpecification
from lancelot.specs.simple_fns import dont_raise_index_error, number_one, \
                                      raise_index_error

@grouping
class BaseConstraintBehaviour:
    ''' A group of specifications for Constraint behaviour '''
    
    @verifiable
    def should_use_nothing_comparator(self):
        ''' Constraint should use Nothing comparator by default''' 
        spec = Spec(Constraint())
        spec.describe_constraint().should_be('should be nothing')
        spec.verify_value(1).should_be(False)
        spec.verify_value(2).should_be(False)
        spec.verify_value(None).should_be(False)
        spec.verify_value(['majestic', 'moose']).should_be(False)
        spec.verify_value({'gumby': 'brain surgeon'}).should_be(False)
    
    @verifiable
    def verify_should_invoke_callable(self):
        ''' verify should invoke callable and compare result '''
        a_list = []
        with_callable = lambda: a_list.append(True)
        spec = Spec(Constraint())
        spec.verify(with_callable).should_raise(UnmetSpecification)
        spec.then(a_list.__len__).should_be(1)

    @verifiable
    def verify_should_use_comparator(self):
        ''' verify should delegate to comparator.compares_to ''' 
        comparator = MockSpec()
        spec = Spec(Constraint(comparator))
        comparator_compares_to = comparator.compares_to(1).will_return(True)
        spec.verify(lambda: 1).should_collaborate_with(comparator_compares_to)
    
    @verifiable
    def desc_should_use_comparator(self):
        ''' describe_constraint should delegate to comparator.description ''' 
        comparator = MockSpec()
        spec = Spec(Constraint(comparator))
        comparator_description = comparator.description()
        comparator_description.will_return('subtitled')
        spec.describe_constraint()
        spec.should_collaborate_with(comparator_description,
                                     and_result='should be subtitled')
        
@grouping
class RaiseBehaviour:
    ''' A group of specifications for Raise behaviour '''
    
    @verifiable
    def should_check_type(self):
        ''' Raise should check that exception is raised '''
        spec = Spec(Raise(IndexError))
        spec.verify(raise_index_error).should_not_raise(UnmetSpecification)
        spec.verify(dont_raise_index_error).should_raise(UnmetSpecification)
    
    @verifiable
    def should_check_message(self):
        ''' Raise should verify exception type & message vs specified ''' 
        spec = Spec(Raise(IndexError('with message')))
        spec.verify(raise_index_error).should_not_raise(UnmetSpecification)
        
        spec = Spec(Raise(IndexError('with different message')))
        spec.verify(raise_index_error).should_raise(UnmetSpecification)

    @verifiable
    def should_have_meaningful_msg(self):
        ''' Raise should produce meaningful UnmetSpecification messages'''
        spec = Spec(Raise(IndexError))
        msg = "should raise IndexError"
        spec.describe_constraint().should_be(msg)
        spec.verify(dont_raise_index_error)
        spec.should_raise(UnmetSpecification(msg))

        spec = Spec(Raise(IndexError('with some message')))
        msg = "should raise IndexError('with some message',)"
        spec.describe_constraint().should_be(msg)
        unmet_msg = msg + ", not IndexError('with message',)"
        unmet_specification = UnmetSpecification(unmet_msg)
        spec.verify(raise_index_error).should_raise(unmet_specification)
 
@verifiable
def not_behaviour():
    ''' Not should raise exception iff underlying check succeeds '''
    spec = Spec(Not(Constraint(EqualsEquals(2))))
    spec.verify(number_one).should_not_raise(UnmetSpecification)

    spec = Spec(Not(Constraint(EqualsEquals(1))))
    msg = 'should not be == 1'
    spec.describe_constraint().should_be(msg)
    spec.verify(number_one).should_raise(UnmetSpecification(msg))
    
    spec = Spec(Not(Not(Constraint(EqualsEquals(2)))))
    msg = 'should be == 2'
    spec.describe_constraint().should_be(msg)
    spec.verify(number_one).should_raise(UnmetSpecification(msg))

@grouping
class CollaborateWithBehaviour: 
    ''' A group of specifications for CollaborateWith behaviour. '''
    
    @verifiable
    def should_trap_incorrect_call(self):
        ''' Specified foo() but bar() called: UnmetSpecification '''
        mock_spec = MockSpec()
        spec = Spec(CollaborateWith(mock_spec.foo()))
        spec.describe_constraint().should_be(mock_spec.foo().description())
        spec.verify(lambda: mock_spec.bar()).should_raise(UnmetSpecification)
    
    @verifiable
    def correct_call_should_be_ok(self):
        ''' Specified foo() and foo() called: met specification '''
        mock_spec = MockSpec()
        spec = Spec(CollaborateWith(mock_spec.foo()))
        spec.verify(lambda: mock_spec.foo())
        spec.should_not_raise(UnmetSpecification)

    @verifiable
    def should_trap_incorrect_args(self):
        ''' Specified foo(2) & bar(), and foo(1) called: UnmetSpecification'''
        mock_spec = MockSpec()
        collaborations = (mock_spec.foo(2), mock_spec.bar())
        descriptions = [collaboration.description() 
                        for collaboration in collaborations]
        spec = Spec(CollaborateWith(*collaborations))
        spec.describe_constraint().should_be(','.join(descriptions))
        spec.verify(lambda: mock_spec.foo(1)).should_raise(UnmetSpecification)
    
    @verifiable
    def should_trap_incorrect_return(self):
        ''' Specified and_result="bar" but was "baz": UnmetSpecification.
        Note: and_result refers to the value returned from the callable  
        invoked in verify(), not the return value from the mock. See
        the Hungarian gentleman in the examples for a clearer picture... ''' 
        mock_spec = MockSpec()
        spec = Spec(CollaborateWith(mock_spec.foo().will_return('baz'), 
                                    and_result='bar'))
        spec.verify(lambda: mock_spec.foo()).should_raise(UnmetSpecification)

    @verifiable
    def correct_result_should_be_ok(self):
        ''' Specified and_result="bar" and was "bar": met specification.
        Note: and_result refers to the value returned from the callable  
        invoked in verify(), not the return value from the mock. See
        the Hungarian gentleman in the examples for a clearer picture... ''' 
        mock_spec = MockSpec()
        spec = Spec(CollaborateWith(mock_spec.foo().will_return('bar'), 
                                    and_result='bar'))
        spec.verify(lambda: mock_spec.foo())
        spec.should_not_raise(UnmetSpecification)

if __name__ == '__main__':
    verify()
