#!/usr/bin/env python
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

from sptest import TestMain

class TestCaseWithoutErrors(unittest.TestCase):
    def test0_one_is_one(self):
        self.assertEqual(1, 1)
        
    def test1_none_is_none(self):
        self.assertEqual(None, None)

TestSuiteWithoutErrors = unittest.TestLoader().\
                         loadTestsFromTestCase(TestCaseWithoutErrors)

class TestCaseWithFailure(unittest.TestCase):
    def test0_one_is_null(self):
        self.assertEqual(1, 0)

TestSuiteWithFailure = unittest.TestLoader().\
                       loadTestsFromTestCase(TestCaseWithFailure)

class TestCaseWithError(unittest.TestCase):
    def setUp(self):
        raise Exception('ERROR!')

    def test0_one_is_one(self):
        self.assertEqual(1, 1)

TestSuiteWithError = unittest.TestLoader().\
                     loadTestsFromTestCase(TestCaseWithError)

TestSuite = unittest.TestSuite([TestSuiteWithoutErrors, TestSuiteWithFailure,
                                TestSuiteWithError])

def prepare_func(tmain):
    print 'prepare_func().'

def cleanup_func(tmain):
    print 'cleanup_func().'

def parse_testid_func(testobj):
    parts = testobj.id().split('.')
    return ('example0', parts[-2], parts[-1])

if __name__ == '__main__':
    tmain = TestMain(TestSuite, prepare_func=prepare_func,
                     cleanup_func=cleanup_func,
                     parse_testid_func=parse_testid_func).run()
