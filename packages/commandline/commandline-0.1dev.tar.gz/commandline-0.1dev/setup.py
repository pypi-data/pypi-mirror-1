from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='commandline',
      version=version,
      description="Exposes your APIs to the command line.",
      long_description="""\
This is a helper module for making intuitive command line programs with
zero effort. Let's say you have a function that looks like this:
 example_function(string1, string2='something', string3='something else')

The simplest way to make it into a script is to do:
 if __name__ == "__main__":
     import sys
     example_function(*sys.argv[1:])

But this fails when someone writes script.py --help on the command line.
("--help" will just be passed as the first argument to example_function)
It also causes pain if you try to do it with a function like this:
 example_function2(string1, int1=5, int2=4, float1=0.3)

What commandline allows you to do is (without changing example_function):
 if __name__ == "__main__":
    import commandline
    commandline.run_as_main(example_function)

and it will do option parsing, and also convert all arguments to the same type
as the default arguments (as in example_function2).

Limitations
============

Note that it currently can't print help information for arguments other than their default values,
but it will print your docstring for you if that's of any use.
Help for arguments will probably come with python3000's function annotations.
http://www.python.org/dev/peps/pep-3107/

The code is a bit ugly at the moment.
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='command line commandline script',
      author='David Laban',
      author_email='alsuren@gmail.com',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
