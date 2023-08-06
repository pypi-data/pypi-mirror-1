"""
Just a test module, using doctests. Run tests using python setup.py test
or python test.py
"""
def doctests():
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
    doctest.testmod()


import doctest
import unittest
suite = unittest.TestSuite()
suite.addTest(doctest.DocTestSuite())

if __name__ == "__main__":
    doctests()
