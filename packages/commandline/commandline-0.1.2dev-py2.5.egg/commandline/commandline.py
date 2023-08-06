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

Argument types are inferred from the default arguments. Currently supported are:
int, float, bool, str, commandline.Choice
If things don't have a default argument, I can't infer the type, so assume str.

Things passed in as positional arguments will currently be passed in as strings, 
and override things passed in as options. I really need to migrate to some 
optparse-like library that understands positional arguments.

"""

changelog="""
#Currently, only a single function can be exposed per executable. 
#Eventually, I want to be able to do subcommands, like how bzr does
Fixed 2009, with expose_subcommands, but still a bit messy/bad at handling errors
I think that defining some kind of @subcommand('progname') decorator might be better.
and then use run('progname') to run it. Guess we'll see.

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


"""

__all__=["run_as_main", "run_if_main", "run_as_subcommand", "choice"]

import sys
from optparse import OptionParser
from inspect_convenience import *

class Choice(str):
    pass # This is just so that we can add members to string objects.
    
def choice(*choices):
    """
    returns something which behaves like a string, but provides api docs
    which can be read by the commandline interface translator, telling
    the user which strings are valid options.

    Usage:
    def which_door(door=choice('a','b','c')):
        print 'you chose door', door
    """
    ret = Choice(choices[0])
    ret.choices = choices
    return ret

def _add_to_parser(parser, argname, default=None):
    """An internal helper function to wrap around optparse."""
    assert argname == argname.strip('_'), "Limitation caused by optparse not giving me a dict."
    if default is None:
        parser.add_option('--'+argname, type="str", dest=argname, 
                                help='default="%default"')
    elif isinstance(default, bool):
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
    """See expose_module_subcommands"""
    expose_module_subcommands(name)

def expose_module_subcommands(name):
    """Only exposes functions defined within the file named.
    This function is likely to be depricated, as it uses a lot of magic."""
    if name == "__main__":
        module = sys.modules[name]
        try:
            subcommand = sys.argv[1]
        except KeyError:
            print_usage(subcommands)
        subcommands = get_subcommand_names(module)
        if subcommand in subcommands:
            func = getattr(module, sys.argv[1])
            run_as_subcommand(func, sys.argv[2:])
        else:
            print subcommand, 'is not a valid subcommand.'
            print_usage(subcommands)

def print_usage(subcommands):
            print 'Usage:', sys.argv[0], 'command [args] [options]'
            print "commands are:"
            for subcommand in subcommands:
                print subcommand#, getattr(module, subcommand).__help__

def get_subcommand_names(module):
    """An internal function for inspecting modules looking for subcommands.
    Lists all functions defined within the module (no imported functions or methods)"""
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
    
    I might delete this function in the future.
    """
    if name == '__main__':
        run_as_main(sys.modules[name].main)



def run_as_main(func, args=sys.argv[1:], name=sys.argv[0]):
    """ At the bottom of your file, put:
    if __name__ == "__main__":
        import commandline
        commandline.run_as_main(main)
    and suddenly, you have yourself a command line program.
    
    >>> import commandline
    >>> def test1(arg1, arg2=2, arg3=3):
    ...     print arg1, arg2, arg3
    ...
    >>> commandline.run_as_main(test1, ['hi'])
    hi 2 3
    """
    # Create our option parser by using heavy introspection.
    return run_as_subcommand(func, args, name)

def create_parser(func, command_name):
    """Creates an OptParse.OptionParser, and populates it using the arguments
    to func.
    """
    usage =  get_usage(func, command_name)
    parser = OptionParser(usage=usage, epilog=inspect.getdoc(func))
    for argname, default in get_args_with_defaults(func):
        #print "defaults", argname, default
        _add_to_parser(parser, argname, default)
    for argname in get_compulsary_args(func):
        _add_to_parser(parser, argname)
    return parser

def fudge_args(args, argnames):
    """Basically add positional argument support to optparse"""
    for i in range(min(len(args), len(argnames))):
        if not args[i].startswith('-'):
            args[i] = '--%s=%s' % (argnames[i], args[i])
        else:
            break
    return args

def run_as_subcommand(func, args=sys.argv[2:], command_name=None):
    """An internal function for enabling subcommands."""
    if command_name is None:
        command_name = func.func_name
    argnames = get_argnames(func)
    parser = create_parser(func, command_name)
    
    # Add --argname= to the first few arguments.
    args = fudge_args(args, argnames)
    
    # Actually run the parser
    options, leftover_args = parser.parse_args(args)
    
    # Why can't optparse just return a dict? Stupid piece of shit.
    kwargs = dict([(key, value) 
                    for (key, value) in options.__dict__.items() 
                        if key == key.strip('_')
                   ])

    # Why can't I just tell optparse what my positional arguments are?
    num_compulsary = no_of_compulsary_args(func)
    argnames = get_argnames(func)
    if len(leftover_args)!=0:
        parser.print_usage()
        print '(Please put options last, and no more args than shown.)'
        print "Unexpected argument(s):", ','.join(leftover_args)
        exit(1)
    elif len(args) < num_compulsary:
        parser.print_usage()
        print "Some compulsary arguments missing."
        exit(1)
    else:
        return func(**kwargs)

TESTMODE = False
# Set TESTMODE to True to allow doctests to work. 
# Otherwise we get screwed by SystemExit exceptions.
def exit(status):
    if TESTMODE:
        pass
    else:
        sys.exit(status)

if __name__ == "__main__":
    def example_function(   string1, 
                            string2='something',
                            int1=1):
        """This is just an example. You should really try writing your own 
        commandline programs."""
        print string1, string2, int1
    run_as_main(example_function)
