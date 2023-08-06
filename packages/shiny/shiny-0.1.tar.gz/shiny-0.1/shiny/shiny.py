"""

This module really is very shiny. If you want to make it any more shiny, send me an email.

TODO: actually wrap all these decorators in a decorator decorator.

"""

import types
import sys
import pdb

#TODO: split helper functions into a helper-functions module.
DEBUG=True
def dprint(*args):
    """ THIS IS NOT A DECORATOR,
    like py3k's print function, but controllable like logging. """
    if DEBUG:
        for arg in args:
            print arg,
        print
        sys.stdout.flush()



#Annotation decorators. TODO: decide on somewhere to put all annotations.

def blocking(func):
    """A decorator for blocking functions, so that you don't accidentally call
    them from within event handlers."""
    func.is_blocking = True
    return func









#TODO: import some memoising decorators
def only_once(func):
    """ 
    >>> import shiny
    >>> @shiny.only_once
    ... def print_hello():
    ...     print 'hello'
    >>> print_hello()
    hello
    >>> print_hello()
    >>>
    """
    func.done = False
    def call(*args, **kwargs):
        if not func.done:
            func.done = True
            func.retval = func(*args, **kwargs)
        return func.retval
            
    return call

#TODO: write guard decorator
def debug_exceptions(func):
    """Useful if some calling function is ignoring exceptions you raised 
    (eg threads, mainloops)"""
    def call(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            pdb.post_mortem()
            
    return call
    
#TODO: write an "only for functions" decorator, to trivialise this.
def debug_method(func, prefix='', ignore_self=False):
    if not isinstance(func, (types.FunctionType, types.MethodType)):
        return func #untouched, as it's not a func
    else:
        def call(*args, **kwargs):
            callstr = (prefix + func.func_name + '(' + ', '.join(
                        list(map(repr, args[ignore_self:])) + 
                        [k+'='+repr(v) for k,v in kwargs.items()]
                    )+')')
            dprint(' '*debug_method.depth, callstr)
            debug_method.depth += 1
            retval = debug_exceptions(func)(*args, **kwargs)
            debug_method.depth -= 1
            dprint(' '*debug_method.depth, '->', retval)
            return retval
        return call
debug_method.depth = 0

def debug_class(cls, prefix='', exclude=['Get']):
    prefix = prefix + cls.__name__ + '.'
    for name in dir(cls):
        if name.strip('_') == name and name not in exclude: #not private or magic
            attr = getattr(cls, name)
            attr = debug_method(attr, prefix, True)
            setattr(cls, name, attr)
    cls.__init__ = debug_exceptions(cls.__init__)
    return cls