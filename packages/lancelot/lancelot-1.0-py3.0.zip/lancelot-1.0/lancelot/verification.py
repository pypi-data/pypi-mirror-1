'''
Functionality for collating together verifiable functions and verifying them.

Intended public interface:
 Classes: UnmetSpecification, ConsoleListener, AllVerifiable
 Functions: verifiable [used as "@verifiable" in client code], verify(),
     grouping [used as "@grouping" in Python3 client code]
 Variables: -

Intended for internal use:
 Variables: ALL_VERIFIABLE (the default collation of verifiable functions)

Copyright 2009 by the author(s). All rights reserved 
'''

import sys, traceback, types

class UnmetSpecification(Exception):
    ''' Indicator that a Spec should...() specification is unmet '''
    pass

class ConsoleListener:    
    ''' Listener for verification messages that prints to the console '''
    
    def __init__(self, stdout=sys.stdout, stderr=sys.stderr):
        ''' Default consoles are:
         - sys.stdout for normal messages 
         - sys.stderr for tracebacks '''
        self._stdout = stdout
        self._stderr = stderr
        
    def all_verifiable_starting(self, all_verifiable):
        ''' A verification run is starting '''
        self._print('Verifying: ', end='', to_console=self._stdout)
        
    def verification_started(self, verifiable_fn):
        ''' A verification of a single function is starting '''
        self._print('.', end='', to_console=self._stdout)
    
    def specification_met(self, verifiable_fn):
        ''' A verification of a function has completed successfully '''
        pass
    
    def specification_unmet(self, verifiable_fn, unmet):
        ''' A verification of a function has completed unsuccessfully '''
        msg = 'Specification not met: %s' % unmet
        self._exception_raised(msg, unmet)
        
    def _exception_raised(self, msg, exception):
        ''' Print an exception msg and traceback to the console'''
        self._print(msg, to_console=self._stderr)
        tb_items = traceback.extract_tb(exception.__traceback__)
        if len(tb_items) > 1:
            tb_items.pop(0) # remove AllVerifiable._verify_fn
        for item in traceback.format_list(tb_items):
            self._print(item, end='', to_console=self._stderr)
    
    def unexpected_exception(self, verifiable_fn, exception):
        ''' An unexpected exception was raised from a function '''
        msg = 'Unexpected exception: %r' % exception
        self._exception_raised(msg, exception)

    def all_verifiable_ending(self, all_verifiable, outcome):
        ''' A verification run is ending '''
        self._print('\n%s' % outcome, to_console=self._stdout)
        
    def _print(self, msg, end='\n', to_console=None):
        ''' Print a msg to the console '''
        console = to_console and to_console or self._stdout
        print(msg, end=end, file=console)

class AllVerifiable:
    ''' A collation of verifiable functions and the ability to verify them '''
    
    def __init__(self, listener=ConsoleListener()):
        ''' Events notified by this instance are sent to the listener '''
        self._fn_list = []
        self._fn_groups = {}
        self._listener = listener
    
    def include(self, verifiable_fn):
        ''' Add a verifiable function to the collation '''
        if verifiable_fn not in self._fn_list:
            self._fn_list.append(verifiable_fn)
        return self
    
    def include_grouping(self, grouping_class):
        ''' Include a group of verifiable functions as bound class methods '''
        class_attrs = grouping_class.__dict__.values()
        functions = [item for item in class_attrs \
                     if type(item) == types.FunctionType]
        group = grouping_class()
        for fn in functions:
            self._fn_groups[fn] = getattr(group, fn.__name__)
        
    def total(self):
        ''' The number of verifiable functions in the collation '''
        return len(self._fn_list)
        
    def verify(self, fail_fast=False):
        ''' Verify all the verifiable functions in the collation.
        Entry point for usage in module verify() function. '''
        verified = 0
        self._listener.all_verifiable_starting(self)
        for verifiable_fn in self._fn_list:
            fn_verified = self.verify_fn(verifiable_fn)
            verified += fn_verified
            if fail_fast and not fn_verified:
                break
        outcome = {'total': self.total(), 
                   'verified': verified, 
                   'unverified': self.total() - verified}
        if fail_fast:
            outcome['fail_fast'] = True
        self._listener.all_verifiable_ending(self, outcome)
        return outcome 
    
    def verify_fn(self, verifiable_fn):
        ''' Verify a single verifiable function (for internal use). '''
        self._listener.verification_started(verifiable_fn)
        try:
            if verifiable_fn in self._fn_groups:
                self._fn_groups[verifiable_fn]()
            else:
                verifiable_fn()
            self._listener.specification_met(verifiable_fn)
            return 1
        except UnmetSpecification as unmet:
            self._listener.specification_unmet(verifiable_fn, unmet)
            return 0
        except Exception as exception:
            self._listener.unexpected_exception(verifiable_fn, exception)
            return 0

ALL_VERIFIABLE = AllVerifiable() # Default collection to verify

def verifiable(decorated_fn, collator=ALL_VERIFIABLE):
    ''' Function decorator: collates functions for later verification '''
    if not hasattr(decorated_fn, '__call__'):
        msg = '%r is not callable, so it cannot be verifiable'
        raise TypeError(msg % decorated_fn)
    collator.include(decorated_fn)
    return decorated_fn

def grouping(decorated_class, collator=ALL_VERIFIABLE):
    ''' Class decorator: collates groups of methods for later verification '''
    if not isinstance(decorated_class, type):
        msg = '%r is not a type: perhaps you meant to use @verifiable instead?'
        raise TypeError(msg % decorated_class) 
    collator.include_grouping(decorated_class)
    return decorated_class

def verify(single_verifiable_fn=None, fail_fast=False):
    ''' Verify either a single specified function or the default collection.
    If fail_fast is True then the verification run will stop as soon as
    the first unmet specification or unexpected exception occurs.'''
    if single_verifiable_fn:
        return AllVerifiable().include(single_verifiable_fn).verify(fail_fast)
    else:
        return ALL_VERIFIABLE.verify(fail_fast)
