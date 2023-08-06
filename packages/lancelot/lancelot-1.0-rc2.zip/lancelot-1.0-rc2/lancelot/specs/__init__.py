'''
Sub-package with Specs for the behaviours of all core classes 
'''

import lancelot 

if __name__ == '__main__':
    # Verify all the specs as a collection 
    from lancelot.specs import verification_spec, comparator_spec, \
        constraint_spec, calling_spec, mocking_spec, specification_spec
    lancelot.verify()
    