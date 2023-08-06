'''
Functionality for comparing two object or class / type instances
to determine if they are "equivalent", with more room for semantic 
interpretation than provided by builtins "==" and "is".

Intended public interface:
 Classes: EqualsEquals, SameAs, LessThan, GreaterThan, StrEquals, 
     ReprEquals, NoneValue, NotNoneValue, Anything, ExceptionValue, FloatValue
     Contain, NotContain, Empty, Length, Type,
     LessThanOrEqual, GreaterThanOrEqual
 Functions: -
 Variables: -

Intended for internal use:
 Classes: Comparator, IsComparator, NotComparator, OrComparator, Nothing

Copyright 2009 by the author(s). All rights reserved 
'''

class Comparator:
    ''' Base class for comparing a prototypical instance to an other value. '''
    
    def __init__(self, prototype):
        ''' Provide a prototypical instance to compare others against'''
        self._prototype = prototype
        
    def __eq__(self, other):
        ''' Delegate to compares_to method '''
        return self.compares_to(other)

    def compares_to(self, other):
        ''' Compare prototypical instance and other instance. 
        Subclasses return True if there is an equivalence, False otherwise.
        This base class however always returns False (no equivalence).'''
        return False
    
    def description(self):
        ''' Describe this comparator '''
        if self._prototype:
            return '%s %r' % (type(self).__name__.lower(), self._prototype)
        return '%s' % type(self).__name__.lower()

class EqualsEquals(Comparator):
    ''' Comparator for handling comparison using ==. '''
        
    def compares_to(self, other):
        ''' True iff prototypical instance == other '''
        return self._prototype == other

    def description(self):
        ''' Describe this comparator '''
        return '== %r' % self._prototype

class SameAs(Comparator):
    ''' Comparator for handling comparison using "same". '''
        
    def compares_to(self, other):
        ''' True iff prototypical instance is other '''
        return self._prototype is other

    def description(self):
        ''' Describe this comparator '''
        return 'same as %r' % self._prototype

class LessThan(Comparator):
    ''' Comparator for handling comparison using <. '''
        
    def compares_to(self, other):
        ''' True iff other < prototypical instance '''
        try :
            return other < self._prototype
        except TypeError:
            return False
        
    def description(self):
        ''' Describe this comparator '''
        return '< %r' % self._prototype

class GreaterThan(Comparator):
    ''' Comparator for handling comparison using >. '''
        
    def compares_to(self, other):
        ''' True iff other > prototypical instance '''
        try :
            return other > self._prototype 
        except TypeError:
            return False

    def description(self):
        ''' Describe this comparator '''
        return '> %r' % self._prototype

class Contain(Comparator):
    ''' Comparator for handling comparison using "in" / "contains". '''
        
    def compares_to(self, other):
        ''' True iff other contains prototypical instance '''
        try:
            return self._prototype in other
        except (AttributeError, TypeError):
            return False

class Length(Comparator):
    ''' Comparator for handling comparison using len(). '''
        
    def compares_to(self, other):
        ''' True iff len(other) == prototype instance '''
        return len(other) == self._prototype
    
class StrEquals(Comparator):
    ''' Comparator for handling comparison through str(). '''
        
    def compares_to(self, other):
        ''' True iff other str(prototypical instance) == str(other) '''
        return str(self._prototype) == str(other)

    def description(self):
        ''' Describe this comparator '''
        return 'str() value %r' % str(self._prototype)

class ReprEquals(Comparator):
    ''' Comparator for handling comparison through repr(). '''
        
    def compares_to(self, other):
        ''' True iff other repr(prototypical instance) == repr(other) '''
        return repr(self._prototype) == repr(other)

    def description(self):
        ''' Describe this comparator '''
        return 'repr() value %r' % self._prototype

class Type(Comparator):
    ''' Comparator for handling comparison of type() of instances. '''
    
    def compares_to(self, other):
        ''' True if prototypical value is a type and 
            isinstance(other, prototypical type); 
        or prototypical value is an instance and  
            isinstance(other, type(prototypical instance)) '''
        if isinstance(self._prototype, type):
            return isinstance(other, self._prototype)
        return isinstance(other, type(self._prototype))
    
    def description(self):
        ''' Describe this comparator '''
        if isinstance(self._prototype, type):
            return 'type %r' % self._prototype
        return 'type %r' % type(self._prototype)

class ExceptionValue(Comparator):
    ''' Comparator for handling comparison with Exception instances. '''
        
    def compares_to(self, other):
        ''' True iff Type(prototypical exception).compares_to(other)
        and str(other) == str(prototypical exception) '''
        if Type(self._prototype).compares_to(other):
            if isinstance(self._prototype, type):
                return True
            return StrEquals(self._prototype).compares_to(other)
        return False

    def description(self):
        ''' Describe this comparator '''
        if isinstance(self._prototype, type):
            return self._prototype.__name__
        return '%r' % self._prototype

class FloatValue(Comparator):
    ''' Comparator for handling float comparison with tolerance for FPA. '''
    
    def __init__(self, prototype, tolerance=None):
        ''' Provide a prototype float to compare others against, and an
        optional level of tolerance for the comparison. If no tolerance is
        specified explicitly then it is calculated as 0.xxxx1 where xxxx is
        the number of explicit decimal places of the prototype.'''
        super().__init__(prototype)
        if tolerance:
            self._tolerance = tolerance
        else:
            prototype_parts = str(prototype).split('.')
            try:
                num_dec_places = len(prototype_parts[1]) + 1
            except IndexError:
                num_dec_places = 1
            self._tolerance = pow(10, -num_dec_places)
        
    def tolerance(self):
        ''' The tolerance limit for comparison, either specified or calculated
        in the constructor '''
        return self._tolerance
    
    def compares_to(self, other):
        ''' True iff other is within +/- tolerance of prototypical instance '''
        if (self._prototype + self._tolerance) < other:
            return False
        return (self._prototype - self._tolerance) <= other
    
    def description(self):
        ''' Describe this comparator '''
        return 'within %s of %s' % (self._tolerance, self._prototype) 
    
class IsComparator(Comparator):
    ''' Comparator for handling "comparisons" without a prototype instance '''
    
    def __init__(self):
        ''' No args constructor since the prototypical instance is ignored '''
        super().__init__(None)
        
class NoneValue(IsComparator):
    ''' Comparator for handling comparison to None. '''
        
    def compares_to(self, other):
        ''' True iff other is None (ignoring prototypical instance) '''
        return None == other
    
    def description(self):
        ''' Describe this comparator '''
        return 'None' 
    
class Empty(IsComparator):
    ''' Comparator for handling comparison to empty (using len). '''
        
    def compares_to(self, other):
        ''' True iff len(other) == 0 (ignoring prototypical instance) '''
        return len(other) == 0
 
class Anything(IsComparator):
    ''' Comparator for handling "comparison" to anything. '''
        
    def compares_to(self, other):
        ''' True always (ignoring other and prototypical instance) '''
        return True

class Nothing(IsComparator):
    ''' Comparator for handling "comparison" to nothing. '''
        
    def compares_to(self, other):
        ''' False always (ignoring other and prototypical instance) '''
        return False

class NotComparator(IsComparator):
    ''' Comparator for handling negative comparisons. '''
    
    def __init__(self, comparator_to_negate):
        ''' Negate an instance of comparator_to_negate '''
        super().__init__()
        self._comparator_to_negate = comparator_to_negate
        
    def compares_to(self, other):
        ''' True iff other comparator_to_negate not compares_to(other) '''
        return not self._comparator_to_negate.compares_to(other)
    
    def description(self):
        ''' Describe this comparator '''
        return 'not %s' % self._comparator_to_negate.description()
   
class NotNoneValue(NotComparator):
    ''' Comparator for handling comparison to anything but None. '''
        
    def __init__(self):
        ''' Negate the NoneValue comparator '''
        super().__init__(NoneValue())
          
class NotContain(NotComparator):
    ''' Comparator for handling not-in / not-contains comparison. '''
        
    def __init__(self, value_not_to_contain):
        ''' Negate the Contain comparator '''
        super().__init__(Contain(value_not_to_contain))
        
class OrComparator(IsComparator):
    ''' Comparator for chaining comparisons using "either-or". '''

    def __init__(self, either_comparator, or_comparator):
        ''' Chain either_comparator / or_comparator comparisons together '''
        super().__init__()
        self._first_comparison = either_comparator
        self._second_comparison = or_comparator

    def compares_to(self, other):
        ''' True iff compares_to(other) is True for either_comparator /
        or_comparator '''
        if self._first_comparison.compares_to(other):
            return True
        return self._second_comparison.compares_to(other)
    
    def description(self):
        ''' Describe this comparator '''
        return '%s or %s' % (self._first_comparison.description(), 
                             self._second_comparison.description())

class LessThanOrEqual(OrComparator):
    ''' Comparator for making comparisons using <= . '''

    def __init__(self, prototype):
        ''' Specify prototype value to be <= other '''
        super().__init__(LessThan(prototype), EqualsEquals(prototype))
        self._prototype = prototype

    def description(self):
        ''' Describe this comparator '''
        return '<= %r' % self._prototype

class GreaterThanOrEqual(OrComparator):
    ''' Comparator for making comparisons using >= . '''

    def __init__(self, prototype):
        ''' Specify prototype value to be >= other '''
        super().__init__(GreaterThan(prototype), EqualsEquals(prototype))
        self._prototype = prototype
        
    def description(self):
        ''' Describe this comparator '''
        return '=> %r' % self._prototype