'''
Sub-package with some example Specs to illustrate usage scenarios 
'''

import lancelot

if __name__ == '__main__':
    # Verify all the specs as a collection 
    from lancelot.examples import fibonacci_spec, stack_spec, \
        observer_spec, additional_comparators
    lancelot.verify()