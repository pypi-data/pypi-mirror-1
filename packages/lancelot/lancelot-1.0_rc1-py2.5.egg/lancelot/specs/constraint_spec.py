''' Specs for core library classes / behaviours ''' 

from lancelot import MockSpec, Spec, verifiable, verify
from lancelot.constraints import Constraint, BeEqualTo, CollaborateWith, \
                                 Not, Raise
from lancelot.verification import UnmetSpecification
from lancelot.specs.simple_fns import dont_raise_index_error, number_one, \
                                      raise_index_error, string_abc

@verifiable
def base_constraint_behaviour():
    ''' base Constraint should invoke callable and verify the result.
    Verification should delegate to a comparator, Nothing() by default, 
    that is used to describe the constraint '''
    a_list = []
    with_callable = lambda: a_list.append(True)
    spec = Spec(Constraint())
    spec.verify(with_callable).should_raise(UnmetSpecification)
    spec.then(a_list.__len__).should_be(1)
    
    spec.verify_value(1).should_be(False)
    spec.verify_value(2).should_be(False)
    spec.verify_value(None).should_be(False)
    spec.verify_value(['majestic', 'moose']).should_be(False)
    spec.verify_value({'gumby': 'brain surgeon'}).should_be(False)
    
    comparator = MockSpec()
    spec = Spec(Constraint(comparator))
    comparator_compares_to = comparator.compares_to(1).will_return(True)
    spec.verify(lambda: 1).should_collaborate_with(comparator_compares_to)
    
    comparator = MockSpec()
    spec = Spec(Constraint(comparator))
    comparator_description = comparator.description().will_return('subtitled')
    spec.describe_constraint()
    spec.should_collaborate_with(comparator_description,
                                 and_result='should be subtitled')
 
@verifiable
def raise_behaviour():
    ''' Raise constraint should check that exception is raised
    and that exception type and message are as specified ''' 
    spec = Spec(Raise(IndexError))
    spec.verify(raise_index_error).should_not_raise(UnmetSpecification)
    spec.verify(dont_raise_index_error).should_raise(UnmetSpecification)
    
    spec = Spec(Raise(IndexError('with message')))
    spec.verify(raise_index_error).should_not_raise(UnmetSpecification)
    
    spec = Spec(Raise(IndexError('with different message')))
    spec.verify(raise_index_error).should_raise(UnmetSpecification)

    spec = Spec(Raise(IndexError))
    msg = "should raise IndexError"
    spec.describe_constraint().should_be(msg)
    spec.verify(dont_raise_index_error).should_raise(UnmetSpecification(msg))

    spec = Spec(Raise(IndexError('with some message')))
    msg = "should raise IndexError('with some message',)"
    spec.describe_constraint().should_be(msg)
    unmet_msg = msg + ", not IndexError('with message',)"
    unmet_specification = UnmetSpecification(unmet_msg)
    spec.verify(raise_index_error).should_raise(unmet_specification)
    
@verifiable
def be_equal_to_behaviour():
    ''' BeEqualTo constraint should raise exception iff objects unequal '''
    spec = Spec(BeEqualTo(1))
    spec.verify(number_one).should_not_raise(UnmetSpecification)

    spec = Spec(BeEqualTo(2))
    msg = 'should be == 2'
    spec.describe_constraint().should_be(msg)
    spec.verify(number_one).should_raise(UnmetSpecification)
    
    spec = Spec(BeEqualTo('abc'))
    spec.verify(string_abc).should_not_raise(UnmetSpecification)

    spec = Spec(BeEqualTo('def'))
    msg = "should be == 'def'"
    spec.describe_constraint().should_be(msg)
    spec.verify(string_abc).should_raise(UnmetSpecification)
    
@verifiable
def not_behaviour():
    ''' Not should raise exception iff underlying check succeeds '''
    spec = Spec(Not(BeEqualTo(2)))
    spec.verify(number_one).should_not_raise(UnmetSpecification)

    spec = Spec(Not(BeEqualTo(1)))
    msg = 'should not be == 1'
    spec.describe_constraint().should_be(msg)
    spec.verify(number_one).should_raise(UnmetSpecification(msg))
    
    spec = Spec(Not(Not(BeEqualTo(2))))
    msg = 'should be == 2'
    spec.describe_constraint().should_be(msg)
    spec.verify(number_one).should_raise(UnmetSpecification(msg))

@verifiable
def collaboratewith_behaviour(): 
    '''CollaborateWith should start collaborations and finally verify them '''
    mock_spec = MockSpec()
    spec = Spec(CollaborateWith(mock_spec.foo()))
    spec.describe_constraint().should_be(mock_spec.foo().description())
    # Specified foo() but was bar()
    spec.verify(lambda: mock_spec.bar()).should_raise(UnmetSpecification)
    
    mock_spec = MockSpec()
    spec = Spec(CollaborateWith(mock_spec.foo()))
    # Specified foo() and was foo()
    spec.verify(lambda: mock_spec.foo()).should_not_raise(UnmetSpecification)

    mock_spec = MockSpec()
    collaborations = (mock_spec.foo(1), mock_spec.bar())
    descriptions = [collaboration.description() 
                    for collaboration in collaborations]
    spec = Spec(CollaborateWith(*collaborations))
    spec.describe_constraint().should_be(','.join(descriptions))
    # Specified foo(1) then bar(), and was only foo(1)
    spec.verify(lambda: mock_spec.foo(1)).should_raise(UnmetSpecification)
    
    mock_spec = MockSpec()
    spec = Spec(CollaborateWith(mock_spec.foo(), and_result='bar'))
    # Specified foo() and was foo() but no result is returned 
    spec.verify(lambda: mock_spec.foo()).should_raise(UnmetSpecification)

    mock_spec = MockSpec()
    spec = Spec(CollaborateWith(mock_spec.foo().will_return('bar'), 
                                and_result='bar'))
    # Specified foo() and was foo() with result 'bar' returned 
    # Note: and_result refers to the value returned from the callable  
    # invoked in verify(), not the return value from the mock 
    spec.verify(lambda: mock_spec.foo()).should_not_raise(UnmetSpecification)

if __name__ == '__main__':
    verify()
