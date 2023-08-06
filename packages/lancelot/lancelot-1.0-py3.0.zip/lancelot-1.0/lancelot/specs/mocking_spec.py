''' Specs for core library classes / behaviours ''' 

from lancelot import MockSpec, Spec, grouping, verifiable, verify
from lancelot.calling import MockCall, MockResult
from lancelot.comparators import ExceptionValue, FloatValue, Type, \
                                 EqualsEquals, Nothing
from lancelot.verification import UnmetSpecification

@verifiable
def mock_spec_has_name():
    '''A MockSpec has a name -- used to supply meaningful messages '''
    Spec(MockSpec()).name().should_be('unnamed_mock')
    Spec(MockSpec(name='named_mock')).name().should_be('named_mock')

@verifiable
def mock_call_call_returns_self():
    '''making a mock call should return the mock call'''
    mock_call = MockSpec().foo
    spec = Spec(mock_call)
    spec.__call__().should_be(mock_call)
    
@grouping
class MockCallResultOfBehaviour:
    ''' Grouping of behaviour specs for MockCall.result_of '''
     
    @verifiable
    def should_verify_name(self):
        ''' result_of should verify the name specification '''
        mock_call = MockSpec(name='p').foo()
        spec = Spec(mock_call)
        msg = 'should be collaborating with p.foo(), not p.bar()'
        spec.result_of('bar').should_raise(UnmetSpecification(msg))
    
        mock_call = MockSpec().foo()
        spec = Spec(mock_call)
        spec.result_of('foo').should_not_raise(UnmetSpecification)

    @verifiable
    def should_mimic_specification(self):
        ''' result_of should be callable and return specified value or raise
        specified exception '''
        mock_call = MockSpec().foo()
        mock_call_result = mock_call.result_of('foo')
        spec = Spec(mock_call_result)
        spec.__call__().should_be(None)
    
        mock_call = MockSpec().foo().will_return(1)
        mock_call_result = mock_call.result_of('foo')
        spec = Spec(mock_call_result)
        spec.__call__().should_be(1)
        
        mock_call = MockSpec().foo().will_return((2, 3))
        mock_call_result = mock_call.result_of('foo')
        spec = Spec(mock_call_result)
        spec.__call__().should_be((2, 3))

        mock_call = MockSpec().foo().will_raise(StopIteration)
        mock_call_result = mock_call.result_of('foo')
        spec = Spec(mock_call_result)
        spec.__call__().should_raise(StopIteration)

        value_error = ValueError("that's no ordinary rabbit")
        mock_spec = MockSpec()
        mock_call = mock_spec.foo().will_raise(value_error)
        mock_call_result = mock_call.result_of('foo')
        spec = Spec(mock_call_result)
        spec.__call__().should_raise(value_error)
        # check that after exception raised the collaboration is 'over' 
        Spec(mock_spec).verify().should_not_raise(UnmetSpecification)

    @verifiable
    def should_verify_args_specification(self):
        ''' result_of should verify the args specification and supply a 
        meaningful message if specification is unmet '''
        mock_call = MockSpec(name='a').foo()
        mock_call_result = mock_call.result_of('foo')
        spec = Spec(mock_call_result)
        msg = 'should be collaborating with a.foo(), not a.foo(1)'
        spec.__call__(1).should_raise(UnmetSpecification(msg))
        
        mock_call = MockSpec(name='b').foo(1)
        mock_call_result = mock_call.result_of('foo')
        spec = Spec(mock_call_result)
        msg = "should be collaborating with b.foo(1), not b.foo('1')"
        spec.__call__('1').should_raise(UnmetSpecification(msg))
        
        mock_call = MockSpec(name='c').foo(1)
        mock_call_result = mock_call.result_of('foo')
        spec = Spec(mock_call_result)
        msg = 'should be collaborating with c.foo(1), not c.foo()'
        spec.__call__().should_raise(UnmetSpecification(msg))
        
        mock_call = MockSpec(name='d').foo(1)
        mock_call_result = mock_call.result_of('foo')
        spec = Spec(mock_call_result)
        msg = 'should be collaborating with d.foo(1), not d.foo(2)'
        spec.__call__(2).should_raise(UnmetSpecification(msg))
        
        mock_call = MockSpec(name='e').foo(1)
        mock_call_result = mock_call.result_of('foo')
        spec = Spec(mock_call_result)
        spec.__call__(1).should_not_raise(UnmetSpecification)
        
        mock_call = MockSpec(name='f').foo(1).will_return(2)
        mock_call_result = mock_call.result_of('foo')
        spec = Spec(mock_call_result)
        spec.__call__(1).should_be(2)
        
        mock_call = MockSpec(name='g').bar(keyword='named argument')
        mock_call_result = mock_call.result_of('bar')
        spec = Spec(mock_call_result)
        msg = "should be collaborating with g.bar(keyword='named argument'), "\
                + "not g.bar(keyword='wrong argument')"
        spec.__call__(keyword='wrong argument').should_raise(
                UnmetSpecification(msg))
    
        mock_call = MockSpec(name='h').bar(keyword='named argument')
        mock_call_result = mock_call.result_of('bar')
        spec = Spec(mock_call_result)
        msg = "should be collaborating with h.bar(keyword='named argument'), "\
                + "not h.bar(bad_keyword='named argument')"
        spec.__call__(bad_keyword='named argument').should_raise(
                UnmetSpecification(msg))
            
        mock_call = MockSpec(name='i').bar(keyword='named argument')
        mock_call_result = mock_call.result_of('bar')
        spec = Spec(mock_call_result)
        spec.__call__(keyword='named argument').should_not_raise(
                UnmetSpecification)
            
        mock_call = MockSpec(name='j').bar(
                keyword='named argument').will_return('monty')
        mock_call_result = mock_call.result_of('bar')
        spec = Spec(mock_call_result)
        spec.__call__(keyword='named argument').should_be('monty')
        
@verifiable
def mock_call_successive_times():
    ''' once(), twice() and times() should return the mock call '''
    mock_call = MockSpec().foo()
    Spec(mock_call).once().should_be(mock_call)
    mock_call = MockSpec().foo()
    Spec(mock_call).twice().should_be(mock_call)
    mock_call = MockSpec().foo()
    Spec(mock_call).times(3).should_be(mock_call)

@verifiable
def mock_call_will_return():
    ''' will_return should return the mock call '''
    mock_call = MockSpec().foo()
    Spec(mock_call).will_return(1).should_be(mock_call)

@verifiable
def result_of_successive_times():
    ''' result_of should "iterate" over will_return value(s) and
    provide a meaningful error message if the specification is unmet'''
    mock_call = MockSpec(name='x').foo().times(2).will_return(3, 4)
    spec = Spec(mock_call.result_of('foo'))
    spec.__call__().should_be(3)
    spec = Spec(mock_call.result_of('foo'))
    spec.__call__().should_be(4)
    spec = Spec(mock_call.result_of('foo'))
    msg = 'should be collaborating with x.foo() only 2 successive times'
    spec.__call__().should_raise(UnmetSpecification(msg))
    
    mock_call = MockSpec(name='y').bar().times(3).will_return(5)
    spec = Spec(mock_call.result_of('bar'))
    spec.__call__().should_be(5)
    spec = Spec(mock_call.result_of('bar'))
    spec.__call__().should_be(5)
    spec = Spec(mock_call.result_of('bar'))
    spec.__call__().should_be(5)
    spec = Spec(mock_call.result_of('bar'))
    msg = 'should be collaborating with y.bar() only 3 successive times'
    spec.__call__().should_raise(UnmetSpecification(msg))

@verifiable
def using_mock_call():
    ''' collaboration specification should use MockCall '''
    spec = Spec(MockSpec())
    spec.foo().should_be(Type(MockCall))
    spec.bar(12).should_be(Type(MockCall))
    spec.baz(keyword='named argument').should_be(Type(MockCall))

@grouping
class StartCollaboratingBehaviour:
    ''' Group of specs for MockSpec.start_collaborating '''
    
    @verifiable
    def should_notify_mock_spec(self):
        ''' start_collaborating should pass message on to mock_spec '''
        mock_spec = MockSpec()
        mock_call = mock_spec.foo().once()
        Spec(mock_call).start_collaborating().should_be(mock_spec)
        Spec(mock_spec).bar().should_raise(UnmetSpecification)
        Spec(mock_spec).foo().should_not_raise(UnmetSpecification)
    
    @verifiable
    def should_verify_specified_collaborations(self):
        ''' after start_collaborating, collaborations should be verified '''
        spec = Spec(MockSpec(name='a'))
        spec.when(spec.start_collaborating())
        spec.then(spec.foo())
        msg = 'should not be collaborating with a.foo()'
        spec.should_raise(UnmetSpecification(msg))
    
        spec = Spec(MockSpec(name='b'))
        spec.when(spec.foo(), spec.start_collaborating())
        spec.then(spec.bar())
        msg = 'should be collaborating with b.foo(), not b.bar()'
        spec.should_raise(UnmetSpecification(msg))
    
        spec = Spec(MockSpec(name='c'))
        spec.when(spec.foo(), spec.bar(), spec.start_collaborating())
        spec.then(spec.foo()).should_not_raise(UnmetSpecification)
        msg = 'should be collaborating with c.bar(), not c.baz()'
        spec.then(spec.baz()).should_raise(UnmetSpecification(msg))
        
        mock = MockSpec(name='d')
        mock.foo().times(2).will_return('camelot')
        spec = Spec(mock)
        spec.when(spec.start_collaborating())
        spec.then(spec.foo()).should_not_raise(UnmetSpecification)
        spec.then(spec.foo()).should_not_raise(UnmetSpecification)
        msg = 'should not be collaborating with d.foo()'
        spec.then(spec.foo()).should_raise(UnmetSpecification(msg))
    
    @verifiable
    def should_check_unverified_collaborations(self):
        ''' check for unverified collaborations after start_collaborating '''
        spec = Spec(MockSpec())
        spec.when(spec.foo(), spec.start_collaborating())
        spec.then(spec.verify())
        msg = 'should be collaborating with unnamed_mock.foo()'
        spec.should_raise(UnmetSpecification(msg))
        
        spec = Spec(MockSpec())
        spec.when(spec.foo(), spec.start_collaborating(), spec.foo())
        spec.then(spec.verify())
        spec.should_not_raise(UnmetSpecification)

@grouping
class MockCallArgsComparatorBehaviour:    
    ''' Group of specs for how MockCall uses comparators to verify args ''' 
    
    @verifiable
    def default_mock_spec_comparators(self):
        ''' ExceptionValue should be default for comparing exceptions, and 
        FloatValue for comparing floats. All other types compare with 
        EqualsEquals '''
        spec = Spec(MockSpec())
        
        spec.comparable(IndexError('the number of the counting'))
        spec.should_be(Type(ExceptionValue))
    
        spec.comparable(1.99)
        spec.should_be(Type(FloatValue))
    
        spec.comparable(3).should_be(Type(EqualsEquals))
        spec.comparable('holy hand grenade').should_be(Type(EqualsEquals))
        spec.comparable([]).should_be(Type(EqualsEquals))
        spec.comparable({}).should_be(Type(EqualsEquals))
        
    @verifiable
    def verify_exceptions_with_comparator(self):
        ''' ExceptionValue should be used to verify Exception args '''
        mock_call = MockSpec().your_mother(TypeError('hamster'))
        mock_call_result = mock_call.result_of('your_mother')
        spec = Spec(mock_call_result)
        spec.__call__(TypeError('hamster'))
        spec.should_not_raise(UnmetSpecification)
        
        mock_call = MockSpec().your_father(smelt_of=TypeError('elderberries'))
        mock_call_result = mock_call.result_of('your_father')
        spec = Spec(mock_call_result)
        spec.__call__(smelt_of=TypeError('elderberries'))
        spec.should_not_raise(UnmetSpecification)
    
    @verifiable
    def verify_floats_with_comparator(self):
        ''' FloatValue should be used to verify float args '''
        mock_call = MockSpec().kernigget(3.14)
        mock_call_result = mock_call.result_of('kernigget')
        spec = Spec(mock_call_result)
        spec.__call__(3.141).should_not_raise(UnmetSpecification)
     
    @verifiable
    def can_override_comparators(self):
        ''' should be able to specify any comparator for arg verification '''
        mock_spec = MockSpec(comparators={Exception:Nothing})
        mock_call = mock_spec.your_mother(TypeError('hamster'))
        mock_call_result = mock_call.result_of('your_mother')
        spec = Spec(mock_call_result)
        spec.__call__(TypeError('hamster')).should_raise(UnmetSpecification)

    @verifiable
    def override_comparators_dont_replace_all(self):
        ''' comparator overrides only affect comparator used for that type '''
        mock_spec = MockSpec(comparators={float:EqualsEquals})
        mock_call = mock_spec.your_mother(TypeError('hamster'))
        mock_call_result = mock_call.result_of('your_mother')
        spec = Spec(mock_call_result)
        spec.__call__(TypeError('hamster'))
        spec.should_not_raise(UnmetSpecification)

@grouping
class MockResultBehaviour:
    ''' Group of specs for MockResult '''
    
    @verifiable
    def defaults(self):
        ''' By default should return None just once ''' 
        spec = Spec(MockResult(MockCall(MockSpec(), '')))
        spec.specified_times().should_be(1)
        spec.times_remaining().should_be(1)
        spec.then(spec.next()).should_be(None)
        spec.then(spec.times_remaining()).should_be(0)
        spec.then(spec.next()).should_raise(UnmetSpecification)

    @verifiable
    def return_twice(self):
        ''' times(2) should return default (None) value just twice '''
        spec = Spec(MockResult(MockCall(MockSpec(), '')))
        spec.when(spec.times(2))
        spec.then(spec.specified_times()).should_be(2)
        spec.then(spec.times_remaining()).should_be(2)
        spec.then(spec.times_remaining()).should_be(2)
        spec.then(spec.next()).should_be(None)
        spec.then(spec.times_remaining()).should_be(1)
        spec.then(spec.next()).should_be(None)
        spec.then(spec.times_remaining()).should_be(0)
        spec.then(spec.next()).should_raise(UnmetSpecification)

    @verifiable
    def supply_single_value(self):
        ''' supplies(a_value) should return that value, once '''
        spec = Spec(MockResult(MockCall(None, '')))
        spec.when(spec.supplies('f'))
        spec.then(spec.specified_times()).should_be(1)
        spec.then(spec.next()).should_be('f')

    @verifiable
    def supply_single_value_twice(self):
        ''' combining supplies(a_value) & times(2) (in any order) 
        should return a_value, twice '''
        spec = Spec(MockResult(MockCall(None, '')))
        spec.when(spec.times(2), spec.supplies('f'))
        spec.then(spec.specified_times()).should_be(2)
        spec.then(spec.next()).should_be('f')
        spec.then(spec.next()).should_be('f')
    
        spec = Spec(MockResult(MockCall(None, '')))
        spec.when(spec.supplies('f'), spec.times(2))
        spec.then(spec.specified_times()).should_be(2)
        spec.then(spec.next()).should_be('f')
        spec.then(spec.next()).should_be('f')
    
    @verifiable
    def check_number_values_against_times(self):
        ''' supplies(a,b,...) iff times(len(a,b,...)) '''
        spec = Spec(MockResult(MockCall(None, '')))
        spec.when(spec.times(2))
        spec.then(spec.supplies('a', 'b')).should_not_raise(ValueError)
        spec.then(spec.supplies('x', 'y', 'z')).should_raise(ValueError)

    @verifiable
    def supply_different_values_each_time(self):
        ''' supplies(a,b,...) should return a,b,... on successive
        calls '''
        spec = Spec(MockResult(MockCall(MockSpec(), '')))
        spec.when(spec.times(3))
        spec.then(spec.supplies('x', 
                                          'y', 
                                          'z')).should_not_raise(ValueError)
        spec.then(spec.specified_times()).should_be(3)
        spec.then(spec.next()).should_be('x')
        spec.then(spec.next()).should_be('y')
        spec.then(spec.next()).should_be('z')
        spec.then(spec.next()).should_raise(UnmetSpecification)
        
    @verifiable
    def raise_exception(self):
        ''' raises(exception) should raise exceptions in the same
        fashion as will_suppply_values should return values '''
        spec = Spec(MockResult(MockCall(MockSpec(), '')))
        exception = ValueError('the number of the counting shall be three')
        spec.when(spec.raises(exception))
        spec.then(spec.next()).should_raise(exception)
        spec.then(spec.times_remaining()).should_be(0)
        spec.then(spec.next()).should_raise(UnmetSpecification)
        
        spec = Spec(MockResult(MockCall(MockSpec(), '')))
        exception = ValueError('the number of the counting shall be three')
        spec.when(spec.times(2), spec.raises(exception))
        spec.then(spec.next()).should_raise(exception)
        spec.then(spec.next()).should_raise(exception)
        spec.then(spec.next()).should_raise(UnmetSpecification)

        spec = Spec(MockResult(MockCall(MockSpec(), '')))
        exceptions = (ValueError('the number of the counting shall be three'),
                      ValueError('Four shalt thou not count'))
        spec.when(spec.times(2), spec.raises(*exceptions))
        spec.then(spec.next()).should_raise(exceptions[0])
        spec.then(spec.next()).should_raise(exceptions[1])
        spec.then(spec.next()).should_raise(UnmetSpecification)

if __name__ == '__main__':
    verify()