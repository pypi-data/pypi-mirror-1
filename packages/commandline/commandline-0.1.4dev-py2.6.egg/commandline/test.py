"""
Just a test module, using doctests. Run tests using python setup.py test
or python test.py
"""
def doctests():
    """
    >>> import commandline
    >>> commandline.TESTMODE=1
    >>> def test1(arg1=1, arg2=2, arg3=3):
    ...     print [arg1, arg2, arg3]
    ...
    >>> commandline.run_as_main(test1, [])
    [1, 2, 3]
    >>> commandline.run_as_main(test1, ['6'])
    [6, 2, 3]
    >>> commandline.run_as_main(test1, ['--arg1=6', '--arg2=7', '--arg3=8'])
    [6, 7, 8]
    >>> commandline.run_as_main(test1, ['6', '7', '8'])
    [6, 7, 8]
    
    >>> commandline.run_as_main(test1, ['6', '7', '8', '9'], 'test.py')
    Usage: test.py [arg1 [arg2 [arg3]]] [Options]
    <BLANKLINE>
    (Please put options last, and no more args than shown.)
    Unexpected argument(s): 9
    
    >>> commandline.run_as_main(test1, ['--arg1=6', '7', '8'], 'test.py')
    Usage: test.py [arg1 [arg2 [arg3]]] [Options]
    <BLANKLINE>
    (Please put options last, and no more args than shown.)
    Unexpected argument(s): 7, 8
    
    >>> def test2(arg1=1, arg2=2, arg3=3):
    ...     return [arg1, arg2, arg3]
    ...
    >>> commandline.run_as_main(test2, ['6', '7', '8'])
    [6, 7, 8]
    
    >>> def nodefault(arg1, arg2, arg3):
    ...     return [arg1, arg2, arg3]
    >>> # If we have no default arguments, we assume you want strings:
    >>> commandline.run_as_main(nodefault, ['6', '7', '8'])
    ['6', '7', '8']
    >>> commandline.run_as_main(nodefault, [], 'test.py')
    Usage: test.py arg1 arg2 arg3 [Options]
    <BLANKLINE>
    The following compulsory arguments are missing: arg1, arg2, arg3
    """
    doctest.testmod()


import doctest
import unittest
suite = unittest.TestSuite()
suite.addTest(doctest.DocTestSuite())

if __name__ == "__main__":
    doctests()
