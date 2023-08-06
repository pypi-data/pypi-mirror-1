# Copyright (C) 2008 Stephan Peijnik
#
# This file is part of sptest.
#
#  sptest is free software: you can redistribute it and/or modify     
#  it under the terms of the GNU General Public License as published by      
#  the Free Software Foundation, either version 3 of the License, or         
#  (at your option) any later version.                                       
#                                                                              
#  sptest is distributed in the hope that it will be useful,          
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             
#  GNU General Public License for more details.                             
#                                                                              
#  You should have received a copy of the GNU General Public License       
#  along with sptest.  If not, see <http://www.gnu.org/licenses/>.

import unittest

## Implementation of unittest.TestResult
class TestResult(unittest.TestResult):
    ## Constructor.
    # @param parse_testid_func Testcase id parser function [default: None].
    # @param output_class Output handler class.
    # @param args Non-keyword arguments.
    # @param kwargs Keyword-arguments.
    def __init__(self, output_class, parse_testid_func=None,
                 *args, **kwargs):
        unittest.TestResult.__init__(self)

        ## Number of tests.
        self.test_count = 0
        ## Number of tests that have already run.
        self.tests_run = 0
        ## Number of tests with a result of success.
        self.tests_success = 0
        ## Number of tests run in the current TestCase.
        self.tests_run_in_case = 0
        ## Information whether errors have occured in current TestCase.
        self.errors_in_case = False
        ## Information whether failures have occured in current TestCase.
        self.failures_in_case = False
        ## Last TestCase's name.
        self.last_case = None
        ## Last module's name.
        self.last_module = None

        ## Pointer parse_testid_func.
        self.parse_testid_func = parse_testid_func
        ## Output handler class.
        self.output = output_class(self, **kwargs)

    ## tests_error attribute.
    # @returns Error count.
    @property
    def tests_error(self):
        return len(self.errors)

    ## tests_failure attribute.
    # @returns Failure count.
    @property
    def tests_failure(self):
        return len(self.failures)

    ## Parses a testid.
    # @param testobj unittest.TestCase object.
    # @returns Tuple containing module name, testcase name and test name.
    def parse_testid(self, testobj):
        if self.parse_testid_func:
            return self.parse_testid_func(testobj)

        parts = testobj.id().split('.')
        
        return (parts[1], parts[-2], parts[-1])

    ## Checks if the module or testcase has changed and calls
    # the corresponding methods of output_class.
    # @param module Module name.
    # @param case TestCase name.
    def _check_new_module_or_case(self, module, case):
        if self.last_module != module:
            self.output.new_module(module)
            self.last_module = module

        if self.last_case != case:
            self.output.new_case(module, case)
            self.last_case = case
            self.errors_in_case = False
            self.failures_in_case = False
            self.tests_run_in_case = 0
            

    ## Implementation of unittest.TestResult.startTest.
    # @param testobj unittest.TestCase object.
    def startTest(self, testobj):
        module, case, testname = self.parse_testid(testobj)

        self._check_new_module_or_case(module, case)

        self.output.test_started(module, case, testname)

    ## Implementation of unittest.TestResult.stopTest.
    # @param testobj unittest.TestCase object.  
    def stopTest(self, testobj):
        self.tests_run += 1
        self.tests_run_in_case += 1

    ## Implementation of unittest.TestResult.addSuccess.
    # @param testobj unittest.TestCase object.  
    def addSuccess(self, testobj):
        module, case, testname = self.parse_testid(testobj)
        self.tests_success += 1
        
        self.output.test_success(module, case, testname)

    ## Implementation of unittest.TestResult.addFailure.
    # @param testobj unittest.TestCase object.
    # @param errobj Tuple of error type, error info and error traceback.
    def addFailure(self, testobj, errobj):
        module, case, testname = self.parse_testid(testobj)
        self.failures.append(((module, case, testname), errobj))
        self.failures_in_case = True
        self.output.test_failure(module, case, testname, errobj)

    ## Implementation of unittest.TestResult.addError.
    # @param testobj unittest.TestCase object.
    # @param errobj Tuple of error type, error info and error traceback.
    def addError(self, testobj, errobj):
        module, case, testname = self.parse_testid(testobj)
        self.errors.append(((module, case, testname), errobj))
        self.errors_in_case = True
        self.output.test_error(module, case, testname, errobj)

    ## Calls output_class.prepare.
    def prepare(self):
        self.output.prepare()

    ## Calls output_class.cleanup.
    def cleanup(self):
        self.output.cleanup()

    ## Calls output_class.after_cleanup.
    def after_cleanup(self):
        self.output.after_cleanup()

    ## Calls output_class.done.
    def done(self):
        self.output.done()

    ## Calls output_class.run.
    def run(self):
        self.output.run()
