'''
Some example Specs to illustrate additional comparator usage
'''

import lancelot
from lancelot.comparators import Anything, FloatValue, NotNoneValue, \
    NoneValue, GreaterThan, LessThan, StrEquals, Empty, Length

@lancelot.verifiable
def value_based_comparators():
    ''' Illustrate use of Anything, FloatValue, NotNoneValue, NoneValue,
    GreaterThan, LessThan, StrEquals '''
    spec = lancelot.Spec(1)
    spec.__add__(1).should_be(Anything())
    spec.__add__(2).should_be(FloatValue(3.0))
    spec.__add__(3).should_be(NotNoneValue())
    spec.__add__(4).should_not_be(NoneValue())
    spec.__add__(5).should_be(GreaterThan(5))
    spec.__add__(6).should_be(LessThan(8))
    spec.__add__(7).should_be(StrEquals('8'))
    
@lancelot.verifiable
def content_based_comparators():
    ''' Illustrate use of should_contain() and should_not_contain() with first
    a list, then a dict'''
    camelot = 'a silly place'
    spec = lancelot.Spec(camelot)
    spec.split().should_contain('place')
    spec.split().should_not_contain('sequins')
    
    def one_day_lad():
        ''' Simple fn to return a dict that can be used in example '''
        return {'all this':'will be yours'}
    
    spec = lancelot.Spec(one_day_lad)
    spec.one_day_lad().should_contain('all this')
    spec.one_day_lad().should_not_contain('swamp')
 
@lancelot.verifiable
def length_based_comparators():
    ''' Illustrate Empty and Length comparators with both str and list.
    Also illustrates use of spec.it() '''
    spec = lancelot.Spec('huge...')
    spec.join([]).should_be(Empty())
    spec.join(['tracts of land']).should_be(Length(14))
    
    castles = ['sank into the swamp',
               'sank into the swamp', 
               'burned down, fell over, then sank into the swamp',
               'stayed up']
    spec = lancelot.Spec(castles)
    spec.when(spec.remove('sank into the swamp'))
    spec.then(spec.it()).should_be(Length(3))
    
    spec.when(spec.pop(), spec.pop(), spec.pop())
    spec.then(spec.it()).should_be(Empty())
    
@lancelot.verifiable
def collaboration_with_comparators():
    ''' Illustrate use of Anything() in should_collaborate_with() '''
    
    class Hungarian:
        ''' A gentleman who needs a phrasebook to speak english ''' 
        def __init__(self, phrasebook):
            ''' supply the phrasebook '''
            self._phrasebook = phrasebook
        def say(self, phrase):
            ''' use the phraseboook to translate something into english '''
            return '<<%s>>' % self._phrasebook.translate(phrase)
        
    phrasebook = lancelot.MockSpec()
    spec = lancelot.Spec(Hungarian(phrasebook))
    eels = 'My hovercraft is full of eels'
    mistranslation = phrasebook.translate(Anything()).will_return(eels)
    
    spec.say('Do you have any matches')
    spec.should_collaborate_with(mistranslation, 
                                 and_result='<<%s>>' % eels)

if __name__ == '__main__':
    lancelot.verify()