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

import sys

from sptest.result import TestResult
from sptest.output import FancyCLIOutput

__author__ = 'Stephan Peijnik'
__version__ = '0.2.1'

## test main class
class TestMain(object):
    ## Constructor.
    # @param testsuite unittest.TestSuite object.
    # @param output_class Output handler class [default: FancyCLIOutput].
    # @param prepare_func Preparation function [default: None].
    # @param cleanup_func Cleanup function [default: None].
    # @param parse_testid_func Testcase id parser function [default: None].
    # @param args Non-keyword arguments.
    # @param kwargs Keyword-arguments.
    def __init__(self, testsuite, output_class=FancyCLIOutput,
                 prepare_func=None, cleanup_func=None, parse_testid_func=None,
                 *args, **kwargs):
        ## unittest.TestSuite object.
        self.testsuite = testsuite
        ## Class implementing interface sptest.output.IOutput.
        self.output_class = output_class
        ## Custom preparation function.
        # Signature has to be "def prepare_func(testmain_object)".
        self.prepare_func = prepare_func
        ## Custom cleanup function.
        # Signature has to be "def cleanup_func(testmain_object)".
        self.cleanup_func = cleanup_func
        ## Custom testid parser function.
        # Signature has to be "def parse_testid_func(test_obj)".
        self.parse_testid_func = parse_testid_func
        ## Keyword arguments.
        self.kwargs = kwargs
        ## sptest.result.TestResult object.
        self.result = None

    ## Runs the tests.
    def run(self):
        self.result = TestResult(self.output_class, self.parse_testid_func,
                                 **self.kwargs)
        self.result.test_count = self.testsuite.countTestCases()

        self.result.prepare()
        if self.prepare_func:
            if self.prepare_func(self):
                sys.stderr.write('Error during preparation.\n')
                sys.exit(1)

        self.result.run()
        self.testsuite.run(self.result)
        self.result.done()

        self.result.cleanup()
        if self.cleanup_func:
            if self.cleanup_func(self):
                sys.stderr.write('Error during cleanup.\n')
                sys.exit(1)
        
        self.result.after_cleanup()
