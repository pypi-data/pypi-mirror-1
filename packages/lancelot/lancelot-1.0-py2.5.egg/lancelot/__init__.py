'''
Lancelot is a behaviour-driven specification and verification library 
for python inspired by the BDD idiom of test driven development. 

(Sir Lancelot: "Um, I think when I'm in this idiom, I sometimes get a bit, 
    uh, sort of carried away.")  
    
Example usage scenarios are supplied with this package, e.g.

- standalone function fib(ordinal): 
    Spec(fib).fib(1).should_be(1)

- class Stack with push(), pop() and peek() methods:
    stack = Spec(Stack, given=new_stack)
    stack.when(stack.push(value='a'))
    stack.then(stack.peek()).should_be('a')
    stack.then(stack.pop()).should_be('a')
    stack.then(stack.peek()).should_raise(IndexError)
    stack.then(stack.pop()).should_raise(IndexError)

- collaborating classes Observable and Observer:
    observer = lancelot.MockSpec()
    observable = Observable()
    spec = lancelot.Spec(observable)
    spec.when(spec.add_observer(observer))
    spec.then(spec.send_notification())
    spec.should_collaborate_with(observer.notify(observable))
    
Additional ways to specify argument or return values in collaborations or 
    constraints are available in the lancelot.comparators sub-package. 
    
The latest source code is available at http://code.launchpad.net/lancelot.

Copyright 2009 by the author(s). All rights reserved 
'''

__version__ = "1.0"

from lancelot.specification import MockSpec, Spec
from lancelot.verification import grouping, verifiable, verify

__all__ = ['MockSpec', 'Spec', 'grouping', 'verifiable', 'verify']

