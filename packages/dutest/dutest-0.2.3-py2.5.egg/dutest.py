#!/usr/bin/env python
# -*- coding: UTF-8 -*-

r"""An object-oriented API to test doctests using unittest runners.

Module providing classes which extend doctest module so
as to achieve better integration with unittest.

It is different from the Pyhton 2.4 doctest unittest API because:

  * A new unitest.TestLoader descendant now allows to load instances
    of TestCases for doctests using unittest-style, supports building
    complex test suites in a more natural way, and eases the use of
    specialized instances of TestCase built out of doctest examples.
  
  * Other loaders allow users to extract TestCase instances out of 
    TestCase descendants and doctests (and any other format) in a 
    single step.
    
  * In this case unittest.TestResult instances report whether
    individual examples have been successfully executed, or otherwise
    have failed or raised an unexpected exception. Formerly TestResult
    objects contained the whole report outputted by doctest module.
    
  * Test analysis require no further parsing to retrieve detailed
    information about failures.
  
  * A whole new unittest API for doctest adds object orientation and
    eliminates functions with big signatures.
  
  * It is not necessary to use DocTestRunner output streams in order
    to collect test results.
  
  * A new hierarchy of doctest TestCases is now 
    possible so for example, setUp and tearDown may
    be redefined across a hierarchy of TestCases 
    instead of providing this methods as parameters to
    a function (breaking OOP philosophy and logic); or
    maybe even failures and errors can be represented in a
    custom way.
  
  * Allows to perform regression testing over tests written
    using doctest.
    
  * Fixes a minor bug related with specifying different verbosity
    levels from the command line to unittest.TestProgram (alias main).
    
  * Loads by default test cases for doctests plus those
    formerly loaded by unittest.TestLoader

It is similar to the Pyhton 2.4 doctest unittest API because:

  * Provides integration with TestProgram and unittest test runners.
    
  * Allows to parameterize doctest behavior via doctest options


A fuller explanation can be found in the following article:

    "Doctest and unittest... now they'll live happily together", O. Lang
    (2008) The Python Papers, Volume 3, Issue 1, pp. 31:51


Note: The contents of this module were first implemented by the module
oop.utils.testing contained in `PyOOP package`_.

.. _PyOOP package: http://pypi.python.org/pypi/PyOOP

"""

# Copyright (C) 2008-2012 Olemis Lang
# 
# This module is free software, and you may redistribute it and/or modify
# it under the same terms as Python itself, so long as this copyright message
# and disclaimer are retained in their original form.
# 
# IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
# SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
# THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
# 
# THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
# AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
# SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.

__all__ = 'DocTestCase', 'DocTestSuite', 'DocTestLoader', 'main', \
          'defaultTestLoader', 'defaultTestRunner', \
          'PackageTestLoader', 'MultiTestLoader', 'REGEX', 'UNIX'

__metaclass__ = type

#------------------------------------------------------
#    Pattern matching strategies
#------------------------------------------------------

from re import compile as REGEX
from fnmatch import translate

UNIX = lambda pattern: REGEX(translate(pattern))

#------------------------------------------------------
#    unittest interface to doctest module
#------------------------------------------------------

from sys import stderr, modules

import doctest
from unittest import TestCase
import unittest

from inspect import ismodule
from StringIO import StringIO
import os

try:
    import pkg_resources
except ImportError:
    __has_resources = False
except:
    raise
else:
    __has_resources = True

# Hide this module from tracebacks written into test results.
__unittest = True

class _Doc2UnitTestRunner(doctest.DocTestRunner):
    r"""An adapter class which allows to invoke transparently a
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
    r"""A class whose instances represent tests over DocTest 
    instance's examples.
    """
    def __init__(self, dt, idx= 0):
        r"""Create an instance that will test a DocTest instance's
        example (the idx-th according to its examples member)
        """
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
        r"""Run the test without collecting errors in a TestResult"""
        raise NotImplementedError, "doctest module doesn't allow to "\
                                   "test single examples"

class DocTestSuite(unittest.TestSuite):
    r"""This test suite consists of DocTestCases derived from a single
    DocTest instance.
    """
    docRunnerClass= _Doc2UnitTestRunner
    docTestCaseClass= DocTestCase
    def __init__(self, dt, optionflags=0, checker=None, runopts=None):
        if runopts is None:
            runopts = dict()
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
        r"""Run the tests without collecting errors in a TestResult"""
        self.run(None)
        return result
    
    @property
    def globalns(self):
      r"""The global namespace used to execute the interactive 
      examples enclosed by this suite.
      """
      return self._dt.globs

class DocTestLoader(unittest.TestLoader):
    r"""This class loads DocTestCases and returns them wrapped in a
    TestSuite
    """
    doctestSuiteClass= DocTestSuite
    def __init__(self, dt_finder= None, globs=None, extraglobs=None, 
                 **opts):
        super(DocTestLoader, self).__init__()
        self._dtf= dt_finder or doctest.DocTestFinder()
        self.globs, self.extraglobs, self.opts= globs, extraglobs, opts
    
    def loadTestsFromTestCase(self, testCaseClass):
        r"""Return a suite of all DocTestsCases contained in 
        testCaseClass
        """
        raise NotImplementedError
    
    def loadTestsFromModule(self, module):
        r"""Return a suite of all DocTestCases contained in the given 
        module
        """
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
        
        # This is legacy code inspired in doctest behavior.
        # However this is not done anymore since it difficults loading
        # tests from multiple test scripts by using PackageTestLoader
        # class.
            # if not doctests:
            # # Why do we want to do this? Because it reveals a bug that
            # # might otherwise be hidden.
            #     raise ValueError(obj, "has no tests")
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
        r"""Return a suite of all tests cases given a string specifier.
        
        The name may resolve to any kind of object.
        
        The method optionally resolves the names relative to a given 
        module.
        """
        return self.loadTestsFromObject(
                                 self.findObjectByName(name, module),
                                 module)

#------------------------------------------------------
#	Default settings
#------------------------------------------------------
defaultTestRunner = unittest.TextTestRunner()

#------------------------------------------------------
#    Custom Test Suites
#------------------------------------------------------

class DocTestSuiteFixture(DocTestSuite):
  r"""Test suite that allows to set up a fixture once before all 
  its interactive examples are run and clean up after they have been 
  run (i.e. Suite Fixture Setup test pattern).
  """
  def run(self, result):
    r"""Setup the fixture, run the interactive examples (i.e. test 
    cases), and finally clean up.
    """
    try:
      proc = self.setUp
    except AttributeError :
      pass                      # No need to prepare the test suite
    else :
      try:
        proc()
      except KeyboardInterrupt:
        raise
      except:
        # Signal error for all the test cases in this suite
        for dtc in self :
          result.addError(dtc, dtc._exc_info())
        return
    
    result = DocTestSuite.run(self, result)
    
    try:
      proc = self.tearDown
    except AttributeError :
      pass                  # No need to clean up
    else :
      try :
        proc()
      except KeyboardInterrupt:
        raise
      except:
        pass                # Silence ? I have no idea about what to do.
    return result

#------------------------------------------------------
#    Test Discovery
#------------------------------------------------------

class MultiTestLoader(unittest.TestLoader):
    r"""A loader which retrieves at once unittest-like test cases from
    different sources and/or formats.
    """
    
    def __init__(self, loaders= None):
        self.loaders= loaders or []
    def loadTestsFromTestCase(self, testCaseClass):
        r"""Return a suite of all tests cases contained in 
        testCaseClass
        """
        return self.suiteClass(
                loader.loadTestsFromTestCase(testCaseClass) \
                                        for loader in self.loaders)
    def loadTestsFromModule(self, module):
        r"""Return a suite of all tests cases contained in the given
        module
        """
        return self.suiteClass(loader.loadTestsFromModule(module) \
                for loader in self.loaders)
    def loadTestsFromName(self, name, module=None):
        r"""Return a suite of all tests cases given a string 
        specifier.
        """
        return self.suiteClass(loader.loadTestsFromName(name, module) \
                                        for loader in self.loaders)
    def loadTestsFromNames(self, names, module=None):
        r"""Return a suite of all tests cases found using the given 
        sequence of string specifiers. See 'loadTestsFromName()'.
        """
        return self.suiteClass(loader.loadTestsFromNames(names, module) \
                for loader in self.loaders)

defaultTestLoader = MultiTestLoader([unittest.defaultTestLoader, 
                                DocTestLoader()])

class PackageTestLoader(unittest.TestLoader):
    r"""A unittest-like loader (Decorator/Wrapper class) that recursively
    retrieves all the tests included in all the modules found within a
    specified package and the hierarchy it determines. Some filters
    (i.e. regex) may be specified to limit the modules contributing to
    the resulting test suite.
    
    The default behavior if no parameters are specified is to load 
    all doctests and instantiate all subclasses of unittest.TestCase 
    found in all the module across the whole package structure.
    """
    
    defaultPattern = REGEX(".*")
    
    def __init__(self, pattern=defaultPattern, loader=defaultTestLoader,
                 impall=False, globs=None, ns=None, style=REGEX):
        r"""Initializes this test loader. Parameters have the following
        meaning :
        
        param pattern: A regular expression object (see re module)
            used to filter the modules which will be inspected so as
            to retrieve the test suite. If not specified then all
            modules will be processed looking for tests.
            
        param loader: Specify the loader used to retrieve test cases
            from each (single) module matching the aforementioned
            criteria.
        
        param impall: If the value of this flag evaluates to true then
            all the modules inside the package hierarchy will be
            imported (disregarding whether they will contribute to the
            test suite or not). Otherwise only those packages for
            which a match is made (i.e. those contributing to the test
            suite) are imported directly.
        
        param globs: The global namespace in which module imports will
            be carried out.
        
        param ns: The local namespace in which module imports will
            be carried out.
        param style: It is used only when a string has been specified 
            in pattern parameter. Its value *MUST* be a callable 
            object accepting a single string argument and returning a 
            Regular Expression Object to match the target module 
            names. Its possible values are : 
            
            * dutest.REGEX (default) : pattern is a standard regular 
                expression. In fact dutest.REGEX = re.compile.
            * dutest.UNIX : pattern is a Unix filename pattern. In 
                fact dutest.UNIX ~= fnmatch.translate.
        """
        if globs is None:
            globs = {}
        if ns is None:
            ns = {}
        super(PackageTestLoader, self).__init__()
        if isinstance(pattern, str):
            pattern = style(pattern)
        self.pattern = pattern
        self.loader = loader
        self.impall = impall
        self.locals = ns
        self.globs = globs
    
    def loadTestsFromTestCase(self, testCaseClass):
        r"""Return a suite of all tests cases contained in 
        testCaseClass as determined by the wrapped test loader.
        """
        return self.loader.loadTestsFromTestCase(testCaseClass)
        
    def loadTestsFromModule(self, module):
        r"""Return a suite of all test cases contained in the given
        package and the modules it contains recursively.
        
        If a ``pattern`` was not specified to the initializer then all
        modules (packages) in the aformentioned hierarchy are
        considered. Otherwise a test suite is retrieved for all those
        modules having a name matching this pattern. They are packed
        together into another test suite (its type being standard
        self.suiteClass) which is returned to the caller.
        
        If the attribute ``impall`` is set, then all modules in the
        former hierarchy are imported disregarding whether they will
        be inspected when looking for tests or not.
        """
        fnm = os.path.basename(module.__file__)
        ispyfile = any(fnm.endswith(suffix) for suffix in ['.py', '.pyc'])
        if  ispyfile and fnm.rsplit('.', 1)[0] != '__init__':
            return self.loader.loadTestsFromModule(module)
        else:
            loader = self.loader
            if ispyfile:
                root_dir = os.path.dirname(fnm)
            else:
                root_dir = fnm
            pkg_name = module.__name__
            idx = len(pkg_name)
            pend_names = [module.__name__]
            suite = self.suiteClass()
            if self.pattern.match(module.__name__) is not None:
                suite.addTest(loader.loadTestsFromModule(module))
            for modnm in pend_names:
                curdir = root_dir + modnm[idx:].replace('.', os.sep)
                for fname in os.listdir(curdir):
                    ch_path = os.path.join(curdir, fname)
                    if os.path.isdir(ch_path) \
                            and os.path.exists(os.path.join(ch_path, 
                                               '__init__.py')):
                        child_name = '.'.join([modnm, fname])
                        pend_names.append(child_name)
                    elif fname.endswith('.py') and \
                            fname != '__init__.py':
                        child_name = '.'.join([modnm, fname[:-3]])
                    else:
                        continue
                    if self.pattern.match(child_name) is not None:
                        __import__(child_name, self.globs,
                                   self.locals, [], -1)
                        suite.addTest(loader.loadTestsFromModule(
                                modules[child_name]))
                    elif self.impall:
                        __import__(child_name, self.globs,
                                   self.locals, [], -1)
            return suite

#------------------------------------------------------
#	Patch to "fix" verbosity "bug" in unittest.TestProgram
#------------------------------------------------------
class VerboseTestProgram(unittest.TestProgram):
    r"""A command-line program that runs a set of tests. 
    This is primarily for making test modules conveniently executable.
    
    This class extends unittest.TestProgram for the following 
    purposes:
    
      * Fix a minor bug in unittest.TestProgram which prevents running
        from the command line a test suite using different verbosity
        levels.
        
      * By default, load test cases from unittest.TestCase descendants
        (i.e. by using unittest.TestLoader) as well as from
        interactive examples included in doctests.
    """
    def __init__(self, module='__main__', defaultTest=None,
                 argv=None, testRunner=None, 
                 testLoader=defaultTestLoader):
        return super(VerboseTestProgram, self).__init__(self, module, 
                defaultTest, argv, testRunner, testLoader)
    
	def runTests(self):
		if self.testRunner is not None:
			self.testRunner.verbosity = self.verbosity
		super(VerboseTestProgram, self).runTests()

main = VerboseTestProgram

#------------------------------------------------------
#	Prepare for other deltha assertions
#------------------------------------------------------

class DelthaTestRunner(_Doc2UnitTestRunner):
    def _filename(self, test_name, examplenum):
        return '<doctest %s[%d]>' % (test_name, examplenum)
    def _exec_example(example, test, filename, compileflags):
        exec compile(example.source, filename, "single",
                        compileflags, 1) in test.globs
    def _DocTestRunner__run(self, test, compileflags, out):
        r"""Refactor DocTestRunner.__run so that it look like a template 
        method suitable for overloading the semantics of the deltha 
        assertion, and a few other cosmetic characteristics.
        """
        # Keep track of the number of failures and tries.
        failures = tries = 0
        
        # Save the option flags (since option directives can be used
        # to modify them).
        original_optionflags = self.optionflags
        
        SUCCESS, FAILURE, BOOM = range(3) # `outcome` state
        
        check = self._checker.check_output
        
        # Process each example.
        for examplenum, example in enumerate(test.examples):
        
            # If REPORT_ONLY_FIRST_FAILURE is set, then supress
            # reporting after the first failure.
            quiet = (self.optionflags & REPORT_ONLY_FIRST_FAILURE and
                     failures > 0)
        
            # Merge in the example's options.
            self.optionflags = original_optionflags
            if example.options:
                for (optionflag, val) in example.options.items():
                    if val:
                        self.optionflags |= optionflag
                    else:
                        self.optionflags &= ~optionflag
        
            # If 'SKIP' is set, then skip this example.
            if self.optionflags & SKIP:
                continue
        
            # Record that we started this example.
            tries += 1
            if not quiet:
                self.report_start(out, test, example)
        
            # Use a special filename for compile(), so we can retrieve
            # the source code during interactive debugging (see
            # __patched_linecache_getlines).
            filename = self._filename(test.name, examplenum)
        
            # Run the example in the given context (globs), and record
            # any exception that gets raised.  (But don't intercept
            # keyboard interrupts.)
            try:
                # Don't blink!  This is where the user's code gets run.
                self._exec_example(example, test, filename, compileflags)
                self.debugger.set_continue() # ==== Example Finished ====
                exception = None
            except KeyboardInterrupt:
                raise
            except:
                exception = sys.exc_info()
                self.debugger.set_continue() # ==== Example Finished ====
        
            got = self._fakeout.getvalue()  # the actual output
            self._fakeout.truncate(0)
            outcome = FAILURE   # guilty until proved innocent or insane
        
            # If the example executed without raising any exceptions,
            # verify its output.
            if exception is None:
                if check(example.want, got, self.optionflags):
                    outcome = SUCCESS
        
            # The example raised an exception:  check if it was expected.
            else:
                exc_info = sys.exc_info()
                exc_msg = traceback.format_exception_only(*exc_info[:2])[-1]
                if not quiet:
                    got += _exception_traceback(exc_info)
        
                # If `example.exc_msg` is None, then we weren't expecting
                # an exception.
                if example.exc_msg is None:
                    outcome = BOOM
        
                # We expected an exception:  see whether it matches.
                elif check(example.exc_msg, exc_msg, self.optionflags):
                    outcome = SUCCESS
        
                # Another chance if they didn't care about the detail.
                elif self.optionflags & IGNORE_EXCEPTION_DETAIL:
                    m1 = re.match(r'[^:]*:', example.exc_msg)
                    m2 = re.match(r'[^:]*:', exc_msg)
                    if m1 and m2 and check(m1.group(0), m2.group(0),
                                           self.optionflags):
                        outcome = SUCCESS
        
            # Report the outcome.
            if outcome is SUCCESS:
                if not quiet:
                    self.report_success(out, test, example, got)
            elif outcome is FAILURE:
                if not quiet:
                    self.report_failure(out, test, example, got)
                failures += 1
            elif outcome is BOOM:
                if not quiet:
                    self.report_unexpected_exception(out, test, example,
                                                     exc_info)
                failures += 1
            else:
                assert False, ("unknown outcome", outcome)
        
        # Restore the option flags (in case they were modified)
        self.optionflags = original_optionflags
        
        # Record and return the number of failures and tries.
        self.__record_outcome(test, failures, tries)
        return failures, tries

#------------------------------------------------------
#	Support for testing command line scripts
#------------------------------------------------------

from subprocess import Popen

class CmdTestRunner(DelthaTestRunner):
    def _exec_example(example, test, filename, compileflags):
        try:
            retcode = call(example.source, shell=True)
            if retcode < 0:
                print >>sys.stderr, "Child was terminated by signal", -retcode
            else:
                print >>sys.stderr, "Child returned", retcode
        except OSError, e:
            print >>sys.stderr, "Execution failed:", e


        exec compile(example.source, filename, "single",
                        compileflags, 1) in test.globs
