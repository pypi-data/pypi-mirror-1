#!/usr/bin/env python

from distutils.core import setup

DESC = """Object-oriented API for doctest/unittest integration.

    Module providing classes which extend doctest module so
    as to achieve better integration with unittest.
    
    doctest extensions:
    -->    A whole new unittest API to integrate doctest tests.
    -->    It allows to acquire the individual results of each 
        and every DocTest instances' example.
    -->    You do not need to use DocTestRunner output streams
        to collect test results.
    -->    Gathering individual examples' results.
    -->    Failures and errors are collected individually into
        TestResults, making easier the automation of
        post-testing analysis.
    -->    A new hierarchy of doctest TestCases is now 
        possible so for example, setUp and tearDown may
        be redefined across a hierarchy of TestCases 
        instead of providing this methods as parameters to
        a function (breaking OOP philosophy and logic); or
        maybe even to represent failures and errors in a
        custom way.
    -->    A new doctest TestLoader now allows to load doctest
        TestCases using unittest-style, provides integration
        with TestProgram, supports building complex TestSuites
        in a more natural way, and eases the use of specialized 
        instances of TestCases built out of doctest examples.
    -->    Allows to perform regression testing over tests written
        using doctest.
"""

setup(
	name='dutest',
	version='0.1.0',
	description=DESC.split('\n', 1)[0],
	author='FLiOOPS Project',
	author_email='flioops@gmail.com',
	maintainer='Olemis Lang',
	maintainer_email='olemis@gmail.com',
	url='http://flioops.sourceforge.net',
	package_dir = {'': 'utils'},
	py_modules = ['dutest'],
	long_description= DESC
	)

