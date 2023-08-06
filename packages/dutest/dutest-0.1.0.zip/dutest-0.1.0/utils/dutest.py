#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
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

Copyright (C) 2008-2012 Olemis Lang

This module is free software, and you may redistribute it and/or modify
it under the same terms as Python itself, so long as this copyright message
and disclaimer are retained in their original form.

IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
"""

__all__ = 'DocTestCase', 'DocTestSuite', 'DocTestLoader'

#------------------------------------------------------
#    unittest interface to doctest module
#------------------------------------------------------

from sys import stderr

import doctest
from unittest import TestCase
import unittest

from inspect import ismodule
from StringIO import StringIO


class _Doc2UnitTestRunner(doctest.DocTestRunner):
    """An adapter class which allows to invoke transparently a
    doctest runner from inside a unittest run. Besides it reports
    the match made for each Example instance into separate
    TestResult objects.
    
    Note: Users should not use this class directly. It is present
            here as an implementation detail.
    """
    def __init__(self, checker=None, verbose=None, optionflags=0,
                 result= None):
        doctest.DocTestRunner.__init__(self, checker, verbose,
                                       optionflags)
        self.result= result
    def summarize(verbose= None): 
        pass
    def run(self, test, compileflags=None, out=None, 
            clear_globs=True):
        doctest.DocTestRunner.run(self, test, compileflags, out,
                                  clear_globs)
    
    def __cleanupTC(self, tc, result): pass
                
    def report_start(self, out, test, example):
        result= self.result
        if not result or result.shouldStop:
            return
        tc= example.tc
        tc.ok= True
        test.globs['__tester__']= tc
        result.startTest(tc)
        try:
            tc.setUp()
        except KeyboardInterrupt:
            raise
        except:
            result.addError(tc, tc._exc_info())
            tc.ok= False
    def report_success(self, out, test, example, got):
        tc= example.tc
        if not tc.ok:        # example is Ok but setUp failed
            return
        result= self.result
        if (not result) or result.shouldStop:
            return
        try:
            tc.tearDown()
        except KeyboardInterrupt:
            raise
        except:
            result.addError(tc, tc._exc_info())
        else:
            result.addSuccess(tc)
    def report_failure(self, out, test, example, got):
        tc= example.tc
        if not tc.ok:        # example is Ok but setUp failed
            return
        result= self.result
        if not result or result.shouldStop:
            return
        msg = 'Example expected\n%s \n...but test outputted...\n%s'% \
                                                (example.want, got)
        try:
            tc.ok= False
            buff = StringIO()
            doctest.DocTestRunner.report_failure(self, buff.write, 
                                                 test, example, got)
            
            msg = buff.getvalue().split('\n', 2)[2]
            buff.close()
            buff = None
        finally:
            try:
                tc.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                # Errors take precedence over failures
                result.addError(tc, tc._exc_info())
            else:
                result.addFailure(tc, (tc.failureException, 
                        msg,
                        None))
    def report_unexpected_exception(self, out, test, example, 
                                    exc_info):
        tc= example.tc
        if not tc.ok:        # example is Ok but setUp failed
            return
        result= self.result
        if not result or result.shouldStop:
            return
        try:
            tc.ok= False
            tc.tearDown()
        except KeyboardInterrupt:
            raise
        except:
            if issubclass(exc_info[0], tc.failureException):
                # Report faulty tearDown only if failure was detected
                result.addError(tc, tc._exc_info())
            else:
                result.addError(tc, exc_info)
        else:
            if issubclass(exc_info[0], tc.failureException):
                result.addFailure(tc, exc_info)
            else:
                result.addError(tc, exc_info)

class DocTestCase(unittest.TestCase):
    """A class whose instances represent tests over DocTest 
    instance's examples.
    """
    def __init__(self, dt, idx= 0):
        """Create an instance that will test a DocTest instance's
        example (the idx-th according to its examples member)
        """
        super(DocTestCase, self).__init__(None)
        self.ok= True
        self._dt= dt
        ex= dt.examples[idx]
        self._ex= ex
        ex.tc= self
        self._testMethodDoc= '%s (line %s)'% (dt.name, 
                self.lineno is not None and self.lineno or '?')
    
    @property
    def lineno(self):
        if self._dt.filename:
            if self._dt.lineno is not None and \
                                         self._ex.lineno is not None:
                return self._dt.lineno + self._ex.lineno + 1
            elif self._ex.lineno is not None:
                return self._ex.lineno+ 1
            else:
                return None
        else:
            return self._ex.lineno+ 1
    
    @property
    def _testMethodName(self):
        return "%s line %s"% (self._dt.name, self.lineno)
    
    def defaultTestResult(self):
        return TestResult()
    
    def id(self):
        return "Test "+ self._methodName
    
    def __repr__(self):
        return "<%s test=%s line=%s>"% \
                                (unittest._strclass(self.__class__), 
                                self._dt.name, self.lineno)
    
    def run(self, result=None):
        raise NotImplementedError, "doctest module doesn't allow to "\
                                   "test single examples"
    
    def debug(self):
        """Run the test without collecting errors in a TestResult"""
        raise NotImplementedError, "doctest module doesn't allow to "\
                                   "test single examples"

class DocTestSuite(unittest.TestSuite):
    """This test suite consists of DocTestCases derived from a single
    DocTest instance.
    """
    docRunnerClass= _Doc2UnitTestRunner
    docTestCaseClass= DocTestCase
    def __init__(self, dt, optionflags=0, checker=None, runopts= {}):
        unittest.TestSuite.__init__(self)
        self._dt= dt
        self.dt_opts, self.dt_checker, self.dt_ropts = \
                        optionflags, checker, runopts
        for idx in xrange(len(dt.examples)):
            unittest.TestSuite.addTest(self, \
                                       self.docTestCaseClass(dt, idx))
    
    def addTest(self, test):
        raise RuntimeError, "No test can be added to this Test Suite."
    
    def run(self, result):
        self.docRunnerClass(optionflags= self.dt_opts, 
                checker=self.dt_checker, verbose=False, \
                result= result).run(self._dt, **self.dt_ropts)
        return result
    
    def debug(self):
        """Run the tests without collecting errors in a TestResult"""
        self.run(None)
        return result

class DocTestLoader(unittest.TestLoader):
    """This class loads DocTestCases and returns them wrapped in a
    TestSuite
    """
    doctestSuiteClass= DocTestSuite
    def __init__(self, dt_finder= None, globs=None, extraglobs=None, 
                 **opts):
        super(DocTestLoader, self).__init__()
        self._dtf= dt_finder or doctest.DocTestFinder()
        self.globs, self.extraglobs, self.opts= globs, extraglobs, opts
    
    def loadTestsFromTestCase(self, testCaseClass):
        """Return a suite of all DocTestsCases contained in 
        testCaseClass"""
        
        raise NotImplementedError
    
    def loadTestsFromModule(self, module):
        """Return a suite of all DocTestCases contained in the given 
        module"""
        return self.loadTestsFromObject(module)
    
    def loadModuleFromName(self, name):
        parts_copy = name.split('.')
        while parts_copy:
            try:
                module = __import__('.'.join(parts_copy))
                return module
            except ImportError:
                del parts_copy[-1]
                if not parts_copy: raise
    
    def findObjectByName(self, name, module=None):
        parts = name.split('.')
        if module is None:
            module= self.loadModuleFromName(name)
        parts = parts[1:]
        obj = module
        for part in parts:
            parent, obj = obj, getattr(obj, part)
        return obj
        
    def loadTestsFromObject(self, obj, module=None):
        global modules
        doctests = self._dtf.find(obj, module=module, 
                                  globs=self.globs, 
                                  extraglobs=self.extraglobs)
        if module is None:
            if ismodule(obj):
                module= obj
            else:
                try:
                    module= modules[obj.__module__]
                except:
                    module= None
        if self.globs is None:
            globs = module and module.__dict__ or dict()
        if not doctests:
        # Why do we want to do this? Because it reveals a bug that
        # might otherwise be hidden.
            raise ValueError(obj, "has no tests")
        doctests.sort()
        try:
            filename = module and module.__file__ or '?'
        except:
            filename = '?'
        if filename[-4:] in (".pyc", ".pyo"):
            filename = filename[:-1]
        ts= self.suiteClass()
        for dt in doctests:
            if len(dt.examples) != 0:
                if not dt.filename:
                    dt.filename = filename
                ts.addTest(self.doctestSuiteClass(dt, **self.opts))
        return ts
    
    def loadTestsFromName(self, name, module=None):
        """Return a suite of all tests cases given a string specifier.
        
        The name may resolve to any kind of object.
        
        The method optionally resolves the names relative to a given 
        module.
        """
        return self.loadTestsFromObject(
                                 self.findObjectByName(name, module),
                                 module)

#------------------------------------------------------
#    Custom Test Loaders
#------------------------------------------------------

class MultiTestLoader(unittest.TestLoader):
    """A loader which retrieves at once unittest-like test cases from
    different sources and/or formats.
    """
    
    def __init__(self, loaders= []):
        self.loaders= loaders
    def loadTestsFromTestCase(self, testCaseClass):
        """Return a suite of all tests cases contained in 
        testCaseClass"""
        return self.suiteClass(
                [loader.loadTestsFromTestCase(testCaseClass) \
                                        for loader in self.loaders])
    def loadTestsFromModule(self, module):
        """Return a suite of all tests cases contained in the given
        module"""
        return self.suiteClass([loader.loadTestsFromModule(module) \
                for loader in self.loaders])
    def loadTestsFromName(self, name, module=None):
        """Return a suite of all tests cases given a string 
        specifier.
        """
        return self.suiteClass( \
                [loader.loadTestsFromName(name, module) \
                                        for loader in self.loaders])
    def loadTestsFromNames(self, names, module=None):
        """Return a suite of all tests cases found using the given 
        sequence of string specifiers. See 'loadTestsFromName()'.
        """
        return self.suiteClass([loadTestsFromNames(names, module) \
                for loader in self.loaders])
