#!/usr/bin/python
"""This is a helper module for making intuitive command line programs with 
zero effort. It takes a function signature like:
 example_function(string1, string2='something', string3='something else')
and turns it into a simple command-line app with usage:
 example_program string1 [string2 [string3]]

All you have to do is:
 if __name__ == "__main__":
    import commandline
    commandline.run_as_main(example_function)

Limitations
============

Note that it currently can't print help information for arguments other than their default values,
but it will print your docstring for you if that's of any use.

Help for arguments will probably come with python3000's function annotations. 
http://www.python.org/dev/peps/pep-3107/

# All arguments are currently treated as strings. If you want them passed in as 
# something else, use map:
#  def distance(x, y, z):
#      x, y, z = map(float, [x, y, z])
#      print sqrt(x**2 + y**2 + z**2)
# I might make a decorator for this kind of thing at some point, but in reality,
# I think it would be better done using annotations.
FIXED 2009: Types of arguments are now inferred from their default values.
Boolean options are translated into a --argname and a --no_argname flag.

currently, you can't run [bound] class methods as main, because of a limitation in the "inspect" module.
#FIXED 20090221

I need to think about how to create a "choice" data type which doesn't screw up the API
def example(name=choice('Fred', 'Bill')):
    print name 
name must quack like 'Fred': I will have to inheret from string, but have an "alternatives" member variable, which can be used by commandline.
#Done 20090221

Currently, only a single function can be exposed per executable. 
Eventually, I want to be able to do subcommands, like how bzr does

Things passed in as positional arguments will currently be passed in as strings, 
and override things passed in as options. I really need to migrate to some 
optparse-like library that understands positional arguments.

"""
__all__=["run_as_main", "run_if_main", "run_as_subcommand", "choice"]

import sys
import inspect
import types
from optparse import OptionParser

class Choice(str):
    pass # This is just so that we can add stuff to it
    
def choice(*choices):
    ret = Choice(choices[0])
    ret.choices = choices
    return ret

def add_to_parser(parser, argname, default):
    assert argname == argname.strip('_'), "Limitation caused by optparse."
    if isinstance(default, bool):
        parser.add_option('--'+argname, action="store_true", default=default, 
                            dest=argname, help='default="%default"')
        parser.add_option('--no'+argname, action="store_false", default=default, 
                            dest=argname, help='opposite of"')
    elif isinstance(default, Choice):
        parser.add_option('--'+argname, type="choice", default=default, dest=argname, 
                                choices=default.choices, help='default="%default"')
    elif isinstance(default, int):
        parser.add_option('--'+argname, type="int", default=default, dest=argname, 
                                help='default=%default')
    elif isinstance(default, float):
        parser.add_option('--'+argname, type="float", default=default, dest=argname, 
                                help='default=%default')
    elif isinstance(default, complex):
        parser.add_option('--'+argname, type="complex", default=default, dest=argname, 
                                help='default=%default')
    elif isinstance(default, str):
        parser.add_option('--'+argname, type="str", default=default, dest=argname, 
                                help='default="%default"')
    else:
        raise TypeError("Sorry. You can't have default arguments of type %s" % type(default)) 

def expose_subcommands(name):
    expose_module_subcommands(name)

def expose_module_subcommands(name):
    """Only exposes functions defined within the file named"""
    if name == "__main__":
        module = sys.modules[name]
        subcommands = get_subcommand_names(module)
        if len(sys.argv) > 1 and sys.argv[1] in subcommands:
            func = getattr(module, sys.argv[1])
            run_as_subcommand(func, sys.argv[2:])
        else:
            print 'Usage:', sys.argv[0], 'command [args] [options]'
            print "commands are:"
            for subcommand in subcommands:
                print subcommand#, getattr(module, subcommand).__help__

def get_subcommand_names(module):
    """Lists all functions defined within the module (no imported functions or methods)"""
    subcommands = []
    for obj_name in dir(module):
        if obj_name == obj_name.strip('_'):
            obj = getattr(module, obj_name)
            if isinstance(obj, types.FunctionType):
                if obj.__module__ == module.__name__:
                    subcommands.append(obj_name)
    return subcommands

def run_if_main(name):
    """ A convenience function. At the bottom of your file, put:
    import commandline
    commandline.run_if_main(__name__)
    which is equivalent to:
    if __name__ == "__main__":
        import commandline
        commandline.run_as_main(main)
    
    In the future, I plan to support subcommands like "test" automatically.
    """
    if name == '__main__':
        run_as_main(sys.modules[name].main)



def run_as_main(func, args=sys.argv[1:]):
    """ At the bottom of your file, put:
    if __name__ == "__main__":
        import commandline
        commandline.run_as_main(main)
    and suddenly, you have yourself a command line program.
    """
    # Create our option parser by using heavy introspection.
    return run_as_subcommand(func, args, sys.argv[0])

def run_as_subcommand(func, args=sys.argv[1:], command_name=None):
    if command_name is None:
        command_name = func.func_name
    usage =  get_usage(func, command_name)
    parser = OptionParser(usage=usage, epilog=inspect.getdoc(func))
    for argname, default in get_args_with_defaults(func):
        #print "defaults", argname, default
        add_to_parser(parser, argname, default)
    
    # Actually run the parser :O
    options, args = parser.parse_args(args)
    
    # Why can't optparse just return a dict? Stupid piece of shit.
    kwargs = dict([(key, value) for (key, value) in options.__dict__.items() 
                    if key == key.strip('_')])

    # Why can't I just tell optparse what my positional arguments are?
    num_compulsary = no_of_compulsary_args(func)
    if len(args) < num_compulsary:
        print "You need to supply more arguments than that"
        parser.print_help()
        sys.exit(1)
    else:
        argnames = get_argnames(func)
        #print argnames
        #print kwargs
        #TODO: pass this through getopt or something to convert types properly.
        morekwargs = dict(zip(argnames, args))
        kwargs.update(morekwargs)
        #print kwargs
        return func(**kwargs)

# These are convenience wrappers around the functions in "inspect"
# They should probably be marked private before release.

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

if __name__ == "__main__":
    def example_function(   string1, 
                            string2='something',
                            string3='something else'):
        """This is just an example. You should really try writing your own 
        commandline programs."""
        print string1, string2, string3
    run_as_main(example_function)
