'''
Some example Specs to illustrate usage scenarios with given/when/then semantics
'''

import lancelot

class Stack:
    ''' 
    Very simple Stack class. Has no is_empty() method: 
    peek() and pop() raise IndexError to indicate emptiness instead.
    '''
    
    def __init__(self):
        ''' A new stack has no items, i.e. it is empty '''
        self._items = []
        
    def push(self, value):
        ''' Push a value of any sort (including None) on to the stack '''
        self._items.append(value)
        
    def pop(self):
        ''' Remove and return the top-most item from the stack '''
        return self._items.pop()
        
    def peek(self):
        ''' Have a look at the top-most item from the stack without pop-ing'''
        return self._items[-1]

def new_stack():
    ''' Descriptive helper method used for Spec(Stack, given=...) '''
    return Stack()

@lancelot.verifiable
def behaviour_of_new_stack():
    '''' Illustrate Spec(<type>, given=<initial state>) 
    (Behaviour: given a new stack it can't peek or pop) '''
    lancelot.Spec(Stack, given=new_stack).pop().should_raise(IndexError)
    
    lancelot.Spec(Stack, given=new_stack).peek().should_raise(IndexError)
    
    spec = lancelot.Spec(Stack, given=new_stack)
    spec.pop().should_raise(IndexError)
    spec.then(spec.pop()).should_raise(IndexError)
    
    spec = lancelot.Spec(Stack, given=new_stack)
    spec.peek().should_raise(IndexError)
    spec.then(spec.pop()).should_raise(IndexError)

@lancelot.verifiable
def behaviour_of_stack_with_values():
    ''' Illustrate Spec when(...), then(...) sequence 
    (Behaviour: when stack is non-empty then able to peek or pop values) '''
    spec = lancelot.Spec(Stack, given=new_stack)
    spec.when(spec.push(value='a'))
    spec.then(spec.peek()).should_be('a')
    spec.then(spec.pop()).should_be('a')
    spec.then(spec.peek()).should_raise(IndexError)
    spec.then(spec.pop()).should_raise(IndexError)
    
    spec = lancelot.Spec(Stack, given=new_stack)
    spec.when(spec.push(value=1))
    spec.then(spec.pop()).should_be(1)
    spec.then(spec.peek()).should_raise(IndexError)
    spec.then(spec.pop()).should_raise(IndexError)
    
    spec = lancelot.Spec(Stack, given=new_stack)
    spec.when(spec.push(value='a'), spec.push(value='b'))
    spec.then(spec.peek()).should_be('b')
    spec.then(spec.pop()).should_be('b')
    spec.then(spec.peek()).should_be('a')
    spec.then(spec.pop()).should_be('a')
    spec.then(spec.pop()).should_raise(IndexError)
    spec.then(spec.peek()).should_raise(IndexError)
    
if __name__ == '__main__':
    # Verify all the specs as a collection 
    lancelot.verify()