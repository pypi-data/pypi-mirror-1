''' Specs for core library classes / behaviours ''' 

from lancelot import Spec, grouping, verifiable, verify
from lancelot.comparators import Comparator, EqualsEquals, \
     ExceptionValue, SameAs, LessThan, GreaterThan, Contain, \
     NoneValue, NotNoneValue, FloatValue, StrEquals, ReprEquals, Anything, \
     Nothing, NotComparator, OrComparator, NotContain, Length, Empty, Type, \
     LessThanOrEqual, GreaterThanOrEqual

@grouping
class BaseComparatorBehaviour:
    ''' A group of specifications for Comparator behaviour '''
    
    @verifiable
    def should_find_nothing_equivalent(self):
        ''' base Comparator should find all compared objects unequivalent. '''
        Spec(Comparator(1)).compares_to(1).should_be(False)
        Spec(Comparator(2)).compares_to(2).should_be(False)
        Spec(Comparator(3)).compares_to(int).should_be(False)

    @verifiable
    def should_delegate_eq(self):
        ''' base Comparator should delegate __eq__ to compare_to. '''
        #TODO: nicer way of forcing spec to use underlying __eq__
        base_comparator_equals = Comparator(1).__eq__
        spec = Spec(base_comparator_equals)
        spec.__call__(1).should_be(False)
        spec.__call__(2).should_be(False)
        spec.__call__(int).should_be(False)
    
    @verifiable
    def should_use_comparator_desc(self):
        ''' base Comparator description should be type name plus prototype '''
        Spec(Comparator('x')).description().should_be("comparator 'x'")
        Spec(Comparator(1)).description().should_be("comparator 1")

@verifiable
def type_behaviour():
    ''' Type comparator should compare type() '''
    spec = Spec(Type(list))
    spec.compares_to([]).should_be(True)
    spec.compares_to({}).should_be(False)
    spec.description().should_be("type <class 'list'>")

    spec = Spec(Type([]))
    spec.compares_to([]).should_be(True)
    spec.compares_to({}).should_be(False)
    spec.description().should_be("type <class 'list'>")
    
@verifiable
def exceptionvalue_behaviour():
    ''' ExceptionValue comparator should compare type and messsage '''
    spec = Spec(ExceptionValue(IndexError('with message')))
    spec.description().should_be('%r' % IndexError('with message'))
    spec.compares_to(IndexError('with message')).should_be(True)
    spec.compares_to(IndexError('different message')).should_be(False)
    spec.compares_to(ValueError('with message')).should_be(False)

    spec = Spec(ExceptionValue(IndexError))
    spec.description().should_be('IndexError')
    spec.compares_to(IndexError('with message')).should_be(True)
    spec.compares_to(IndexError('different message')).should_be(True)
    spec.compares_to(ValueError('with message')).should_be(False)

@verifiable
def floatvalue_behaviour():
    ''' FloatValue comparator should compare objects with tolerance for FPA '''
    spec = Spec(FloatValue(1.1))
    spec.tolerance().should_be(0.01)
    spec.compares_to(1.1).should_be(True)
    spec.description().should_be('within 0.01 of 1.1')
    spec.compares_to(1.11).should_be(True)
    spec.compares_to(1.12).should_be(False)
    spec.compares_to(1.2).should_be(False)
    spec.compares_to(1.09).should_be(True)
    spec.compares_to(1.08).should_be(False)
    spec.compares_to(1.0).should_be(False)

    spec = Spec(FloatValue(1.1, 0.05))
    spec.tolerance().should_be(0.05)
    spec.description().should_be('within 0.05 of 1.1')
    spec.compares_to(1.1).should_be(True)
    spec.compares_to(1.11).should_be(True)
    spec.compares_to(1.12).should_be(True)
    spec.compares_to(1.2).should_be(False)
    spec.compares_to(1.09).should_be(True)
    spec.compares_to(1.08).should_be(True)
    spec.compares_to(1.0).should_be(False)

    spec = Spec(FloatValue(1.11))
    spec.tolerance().should_be(0.001)
    spec.description().should_be('within 0.001 of 1.11')
    
    spec = Spec(FloatValue(1.99))
    spec.tolerance().should_be(0.001)
    
    spec = Spec(FloatValue(2))
    spec.tolerance().should_be(0.1)
    
@verifiable
def equalsequals_behaviour():
    ''' EqualsEquals comparator should compare objects with == '''
    spec = Spec(EqualsEquals(1))
    spec.description().should_be('== 1')
    spec.compares_to(1).should_be(True)
    spec.compares_to(2).should_be(False)
    
    spec = Spec(EqualsEquals([]))
    spec.description().should_be('== []')
    spec.compares_to([]).should_be(True)
    spec.compares_to([1]).should_be(False)
    
@verifiable
def sameas_behaviour():
    ''' SameAs comparator should compare objects with "same" / "is" '''
    spec = Spec(SameAs(1))
    spec.description().should_be('same as 1')
    spec.compares_to(1).should_be(True)
    spec.compares_to(2).should_be(False)
    
    spec = Spec(SameAs([]))
    spec.description().should_be('same as []')
    spec.compares_to([]).should_be(False) 
    
@verifiable
def lessthan_behaviour():
    ''' LessThan comparator should compare objects with < '''
    spec = Spec(LessThan(1))
    spec.description().should_be('< 1')
    spec.compares_to(0).should_be(True)
    spec.compares_to(1).should_be(False)
    spec.compares_to('a').should_be(False)
    
    spec = Spec(LessThan([1]))
    spec.description().should_be('< [1]')
    spec.compares_to([]).should_be(True)
    spec.compares_to([1]).should_be(False)
    
@verifiable
def greaterthan_behaviour():
    ''' GreaterThan comparator should compare objects with > '''
    spec = Spec(GreaterThan(1))
    spec.description().should_be('> 1')
    spec.compares_to(2).should_be(True)
    spec.compares_to(1).should_be(False)
    spec.compares_to('a').should_be(False)
    
    spec = Spec(GreaterThan([]))
    spec.description().should_be('> []')
    spec.compares_to([]).should_be(False)
    spec.compares_to([1]).should_be(True)
    
@verifiable
def contain_behaviour():
    ''' Contain comparator should compare objects with "in" / "contains" '''
    spec = Spec(Contain('a'))
    spec.description().should_be("contain 'a'")
    spec.compares_to(['a', 'b']).should_be(True)
    spec.compares_to(['a']).should_be(True)
    spec.compares_to(['b']).should_be(False)
    spec.compares_to('abc').should_be(True)
    spec.compares_to('def').should_be(False)
    spec.compares_to({'a':1}).should_be(True)
    spec.compares_to({'b':'a'}).should_be(False)
    spec.compares_to(2).should_be(False)
    
    spec = Spec(Contain(1))
    spec.description().should_be('contain 1')
    spec.compares_to([1, 2]).should_be(True)
    spec.compares_to([1]).should_be(True)
    spec.compares_to([2]).should_be(False)
    spec.compares_to('12').should_be(False)
    spec.compares_to({1:'a'}).should_be(True)
    spec.compares_to({'b':1}).should_be(False)

@verifiable
def notcontain_behaviour():
    ''' NotContain comparator should negate the behaviour of Contain '''
    spec = Spec(NotContain(1))
    spec.description().should_be('not contain 1')
    spec.compares_to([1, 2]).should_be(False)
    spec.compares_to([1]).should_be(False)
    spec.compares_to([2]).should_be(True)

@verifiable
def length_behaviour():
    ''' Length comparator should compare len(object) to specified length '''
    spec = Spec(Length(1))
    spec.description().should_be('length 1')
    spec.compares_to([1, 2]).should_be(False)
    spec.compares_to([1]).should_be(True)
    spec.compares_to([2]).should_be(True)
    spec.compares_to('z').should_be(True)
    spec.compares_to('xyz').should_be(False)

@verifiable
def empty_behaviour():
    ''' Empty comparator should compare len(object) to 0 '''
    spec = Spec(Empty())
    spec.description().should_be('empty')
    spec.compares_to([1, 2]).should_be(False)
    spec.compares_to([1]).should_be(False)
    spec.compares_to([]).should_be(True)
    spec.compares_to('z').should_be(False)
    spec.compares_to('').should_be(True)

@verifiable
def nonevalue_behaviour():
    ''' NoneValue comparator should compare objects with None '''
    spec = Spec(NoneValue())
    spec.description().should_be('None')
    spec.compares_to(None).should_be(True)
    spec.compares_to(1).should_be(False)
    spec.compares_to(2).should_be(False)
    spec.compares_to([]).should_be(False)
    spec.compares_to('').should_be(False)

@verifiable
def notnonevalue_behaviour():
    ''' NotNoneValue comparator should compare objects with not-None '''
    spec = Spec(NotNoneValue())
    spec.description().should_be('not None')
    spec.compares_to(None).should_be(False)
    spec.compares_to(1).should_be(True)
    spec.compares_to(2).should_be(True)
    spec.compares_to([]).should_be(True)
    spec.compares_to('').should_be(True)

@verifiable
def strequals_behaviour():
    ''' StrEquals comparator should compare objects with str() '''
    spec = Spec(StrEquals(1))
    spec.description().should_be("str() value '1'")
    spec.compares_to(1).should_be(True)
    spec.compares_to('1').should_be(True)
    spec.compares_to([1]).should_be(False)
    
    spec = Spec(StrEquals('1'))
    spec.description().should_be("str() value '1'")
    spec.compares_to(1).should_be(True)
    spec.compares_to('1').should_be(True)
    spec.compares_to([1]).should_be(False)
    
@verifiable
def reprequals_behaviour():
    ''' ReprEquals comparator should compare objects with repr() '''
    spec = Spec(ReprEquals(1))
    spec.description().should_be('repr() value 1')
    spec.compares_to(1).should_be(True)
    spec.compares_to('1').should_be(False)
    spec.compares_to([1]).should_be(False)
    
    spec = Spec(ReprEquals('1'))
    spec.description().should_be("repr() value '1'")
    spec.compares_to('1').should_be(True)
    spec.compares_to(1).should_be(False)
    spec.compares_to([1]).should_be(False)
    
@verifiable
def notcomparator_behaviour():
    ''' NotComparator should negate other comparisons '''
    spec = Spec(NotComparator(EqualsEquals(1)))
    spec.description().should_be('not == 1')
    spec.compares_to(1).should_be(False)
    spec.compares_to('1').should_be(True)
    spec.compares_to([1]).should_be(True)
    
    spec = Spec(NotComparator(EqualsEquals('1')))
    spec.description().should_be("not == '1'")
    spec.compares_to('1').should_be(False)
    spec.compares_to(1).should_be(True)
    spec.compares_to([1]).should_be(True)
    
@verifiable
def orcomparator_behaviour():
    ''' OrComparator should chain "either-or" comparisons together '''
    spec = Spec(OrComparator(LessThan(2), EqualsEquals(2)))
    spec.description().should_be("< 2 or == 2")
    spec.compares_to(1).should_be(True)
    spec.compares_to(2).should_be(True)
    spec.compares_to(3).should_be(False)
    spec.compares_to('a').should_be(False)

    spec = Spec(OrComparator(GreaterThan(2), EqualsEquals(2)))
    spec.description().should_be("> 2 or == 2")
    spec.compares_to(2).should_be(True)
    spec.compares_to(1).should_be(False)
    spec.compares_to('a').should_be(False)

@verifiable
def lessthanorequal_behaviour():
    ''' LessThanOrEqual should compare using <= '''
    spec = Spec(LessThanOrEqual(2))
    spec.description().should_be("<= 2")
    spec.compares_to(1).should_be(True)
    spec.compares_to(2).should_be(True)
    spec.compares_to(3).should_be(False)
    spec.compares_to('a').should_be(False)

@verifiable
def greaterthanorequal_behaviour():
    ''' GreaterThanOrEqual should compare using >= '''
    spec = Spec(GreaterThanOrEqual(2))
    spec.description().should_be("=> 2")
    spec.compares_to(2).should_be(True)
    spec.compares_to(1).should_be(False)
    spec.compares_to('a').should_be(False)
    
@verifiable
def anything_behaviour():
    ''' Anything comparator should find all compared objects equivalent. '''
    spec = Spec(Anything())
    spec.description().should_be("anything")
    spec.compares_to(1).should_be(True)
    spec.compares_to('1').should_be(True)
    spec.compares_to([1]).should_be(True)
    spec.compares_to('xyz').should_be(True)
    
@verifiable
def nothing_behaviour():
    ''' Nothing comparator should never find compared objects equivalent. '''
    spec = Spec(Nothing())
    spec.description().should_be("nothing")
    spec.compares_to(1).should_be(False)
    spec.compares_to('1').should_be(False)
    spec.compares_to([1]).should_be(False)
    spec.compares_to('xyz').should_be(False)

if __name__ == '__main__':
    verify()