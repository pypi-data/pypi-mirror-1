''' Simple functions used in Specs ''' 

def dont_raise_index_error():
    ''' Simple fn that does nothing. 
    Aids specifying some behaviours around exceptions ''' 
    pass

def raise_index_error():
    ''' Simple fn that raises an index error.
    Aids specifying some behaviours around exceptions ''' 
    raise IndexError('with message')

def number_one():
    ''' Simple fn that returns the number One (1). ''' 
    return 1

def string_abc():
    ''' Simple fn that returns the string "abc". ''' 
    return 'abc'
