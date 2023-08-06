'''
Lancelot is a behaviour-driven specification and verification library 
for python inspired by the BDD idiom of test driven development. 

(Sir Lancelot: "Um, I think when I'm in this idiom, I sometimes get a bit, 
    uh, sort of carried away.")  
    
Example usage scenarios are supplied with this package, e.g.

- standalone function fib(ordinal): 
    Spec(fib).fib(0).should_be(0)

- class Stack with push(), pop() and peek() methods:
    spec = Spec(Stack, given=new_stack)
    spec.when(spec.push(value='a'))
    spec.then(spec.peek()).should_be('a')
    spec.then(spec.pop()).should_be('a')
    spec.then(spec.peek()).should_raise(IndexError)
    spec.then(spec.pop()).should_raise(IndexError)

- collaborating classes Observable and Observer:
    observer = lancelot.MockSpec()
    observable = Observable()
    spec = lancelot.Spec(observable)
    spec.when(spec.add_observer(observer))
    spec.then(spec.send_notification())
    spec.should_collaborate_with(observer.notify(observable))
    
Additional ways to specify argument or return values in collaborations or 
    constraints are available in the lancelot.comparators sub-package. 

Copyright 2009 by the author(s). All rights reserved 
'''

__version__ = "1.0rc1"

from lancelot.specification import MockSpec, Spec
from lancelot.verification import verifiable, verify

__all__ = ['MockSpec', 'Spec', 'verifiable', 'verify']

