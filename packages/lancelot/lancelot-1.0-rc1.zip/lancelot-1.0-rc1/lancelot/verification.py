'''
Functionality for collating together verifiable functions and verifying them.

Intended public interface:
 Classes: UnmetSpecification, ConsoleListener, AllVerifiable
 Functions: verifiable [used as "@verifiable" in client code], verify()
 Variables: -

Intended for internal use:
 Variables: ALL_VERIFIABLE (the default collation of verifiable functions)

Copyright 2009 by the author(s). All rights reserved 
'''

import sys, traceback

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
        self._listener = listener
    
    def include(self, verifiable_fn):
        ''' Add a verifiable function to the collation '''
        self._fn_list.append(verifiable_fn)
        return self
        
    def total(self):
        ''' The number of verifiable functions in the collation '''
        return len(self._fn_list)
        
    def verify(self):
        ''' Verify all the verifiable functions in the collation '''
        verified = 0
        self._listener.all_verifiable_starting(self)
        for verifiable_fn in self._fn_list:
            verified += self._verify_fn(verifiable_fn)
        outcome = {'total': self.total(), 
                   'verified': verified, 
                   'unverified': self.total() - verified}
        self._listener.all_verifiable_ending(self, outcome)
        return outcome 
    
    def _verify_fn(self, verifiable_fn):
        ''' Verify a single verifiable function '''
        self._listener.verification_started(verifiable_fn)
        try:
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

def verifiable(annotated_fn, collator=ALL_VERIFIABLE):
    ''' Function decorator: collates functions for later verification '''
    collator.include(annotated_fn)
    return annotated_fn

def verify(single_verifiable_fn=None):
    ''' Verify either a single specified function or the default collection '''
    if single_verifiable_fn:
        return AllVerifiable().include(single_verifiable_fn).verify()
    else:
        return ALL_VERIFIABLE.verify()
