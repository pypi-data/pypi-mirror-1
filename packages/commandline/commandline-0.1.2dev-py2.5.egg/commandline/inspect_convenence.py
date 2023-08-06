"""These are convenience wrappers around the functions in "inspect"
They should probably be marked private before release."""

import inspect

def get_argnames(func):
    """returns the names of all arguments to func"""
    (argnames, varargs, varkw, defaults) = getargspec(func)
    return argnames

def get_args_with_defaults(func):
    """returns the names of all defaulted arguments to func, 
    paired with their default values."""
    (argnames, varargs, varkw, defaults) = getargspec(func)
    num = no_of_compulsary_args(func)
    return zip(argnames[num:], defaults)

def get_compulsary_args(func):
    """returns the names of all arguments to func which *must* be provided."""
    (argnames, varargs, varkw, defaults) = getargspec(func)
    num = no_of_compulsary_args(func)
    return argnames[:num]

def no_of_compulsary_args(func):
    """returns the number of arguments which *must* be provided."""
    (argnames, varargs, varkw, defaults) = getargspec(func)
    if defaults:
        num = len(argnames) - len(defaults)
    else:
        num = len(argnames)
    return num
    
def getargspec(func):
    """ a version of inspect.getargspec that isn't *horribly* broken """
    (argnames, varargs, varkw, defaults) = inspect.getargspec(func)
    if isinstance(func, types.MethodType) and (func.im_self is not None): 
        argnames = argnames[1:] # remove "self"
    if defaults==None:
        defaults = []
    return (argnames, varargs, varkw, defaults)

def get_usage(func, command_name):
    """Takes a function, inspects its signature, and turns it into a usage 
    message compatible with optparse."""
    (argnames, varargs, varkw, defaults) = getargspec(func)
    usage = [command_name]
    firstdefault = no_of_compulsary_args(func)
    for i, argname in enumerate(argnames):
        if i >= firstdefault:
            default = defaults[i - firstdefault]
            usage += [' [%(argname)s' % locals()]
        else: 
            usage += [argname+' ']
    usage += [']'*len(defaults)]
    return ''.join(usage)
