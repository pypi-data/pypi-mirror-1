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
import traceback

from datetime import datetime

## Used internally for checking whether xml.dom is available.
HAVE_XML = False

try:
    from xml.dom import getDOMImplementation
    HAVE_XML = True
except ImportError:
    pass

## Output class interface.
class IOutput(object):
    ## Constructor.
    # @param result TestResult object.
    # @param args Non-keyword arguments.
    # @param kwargs Keyword-arguments.
    def __init__(self, result, *args, **kwargs):
        ## TestResult object pointer.
        self.result = result

    ## Handler stub.
    # Called when the current module has changed.
    # @param module New module's name.
    def new_module(self, module):
        raise NotImplementedError()

    ## Handler stub.
    # Called when the current TestCase has changed.
    # @param module Module's name.
    # @param case New TestCase's name.
    def new_case(self, module, case):
        raise NotImplementedError()
    
    ## Handler stub.
    # Called when a test is started.
    # @param module Module's name.
    # @param case TestCase's name.
    # @param testname Test's name.
    def test_started(self, module, case, testname):
        raise NotImplementedError()

    ## Handler stub.
    # Called when a test's result is success.
    # @param module Module's name.
    # @param case TestCase's name.
    # @param testname Test's name.
    def test_success(self, module, case, testname):
        raise NotImplementedError()

    ## Handler stub.
    # Called when a test's result is failure.
    # @param module Module's name.
    # @param case TestCase's name.
    # @param testname Test's name.
    # @param error Tuple of error type, error info and error traceback.
    def test_failure(self, module, case, testname, error):
        raise NotImplementedError()

    ## Handler stub.
    # Called when a test's result is error.
    # @param module Module's name.
    # @param case TestCase's name.
    # @param testname Test's name.
    # @param error Tuple of error type, error info and error traceback. 
    def test_error(self, module, case, testname, error):
        raise NotImplementedError()

    ## Handler stub.
    # Called when all tests have finished.
    def done(self):
        raise NotImplementedError()

    ## Handler stub.
    # Called before prepare_func is called.
    def prepare(self):
        raise NotImplementedError()

    ## Handler stub.
    # Called before cleanup_func is called.
    def cleanup(self):
        raise NotImplementedError()

    ## Handler stub.
    # Called after cleanup_func has been called.
    def after_cleanup(self):
        raise NotImplementedError()

    ## Handler stub.
    # Called before executing the first test.
    def run(self):
        raise NotImplementedError()

## Fancy command line interface output (coloured).
class FancyCLIOutput(IOutput):
    ## Stub, does nothing.
    # @param module Module's name.
    def new_module(self, module):
        pass

    ## Handles a new test case.
    # @param module Module's name.
    # @param case TestCase's name.
    def new_case(self, module, case):
        # Only do this if it is not the first test case.
        if self.result.last_case != None:
            # move cursor up
            print '\x1b[%dF' % (self.result.tests_run_in_case+2)
            csi = ''
                
            if self.result.failures_in_case:
                csi = '\x1b[31;01m'
            elif self.result.errors_in_case:
                csi = '\x1b[33;01m'
            else:
                csi = '\x1b[32;01m'
                
            print '%s[%s.%s]\x1b[0m' % (csi, self.result.last_module,
                                            self.result.last_case)

            # move cursor back down
            print '\x1b[%dE' % (self.result.tests_run_in_case)

            
        if module and case:
            print '\x1b[34;01m[%s.%s]\x1b[0m' % (module, case)

    ## Handles starting of a test.
    # @param module Module's name.
    # @param case TestCase's name.
    # @param testname Test's name.
    def test_started(self, module, case, testname):
        print '\x1b[34;01m [R] %s...\x1b[0m\r' % (testname),
        sys.stdout.flush()

    ## Handles result of a test being success.
    # @param module Module's name.
    # @param case TestCase's name.
    # @param testname Test's name.
    def test_success(self, module, case, testname):
        print '\x1b[32;01m [S] %s   \x1b[0m' % (testname)

    ## Handles result of a test being failure.
    # @param module Module's name.
    # @param case TestCase's name.
    # @param testname Test's name.
    # @param errobj Tuple of error type, error info and error traceback.
    def test_failure(self, module, case, testname, errobj):
        print '\x1b[31;01m [F] %s   \x1b[0m' % (testname)

    ## Handles result of a test being error.
    # @param module Module's name.
    # @param case TestCase's name.
    # @param testname Test's name.
    # @param errobj Tuple of error type, error info and error traceback. 
    def test_error(self, module, case, testname, errobj):
        print '\x1b[33;01m [E] %s   \x1b[0m' % (testname)

    ## Handles all tests having finished.
    def done(self):
        self.new_case(None, None)

    ## Prints summary after cleanup.
    def after_cleanup(self):
        print '\x1b[01m>> Summary\x1b[0m'

        success_cnt = self.result.tests_success
        error_cnt = self.result.tests_error
        failure_cnt = self.result.tests_failure

        one_pc = 100/float(self.result.test_count)

        success_pc = one_pc*self.result.tests_success
        error_pc = one_pc*self.result.tests_error
        failure_pc = one_pc*self.result.tests_failure

        print '\x1b[32;01m success : %d [%.1f%%]\x1b[0m' % (success_cnt,
                                                            success_pc)
        print '\x1b[33;01m error   : %d [%.1f%%]\x1b[0m' % (error_cnt,
                                                            error_pc)
        print '\x1b[31;01m failure : %d [%.1f%%]\x1b[0m' % (failure_cnt,
                                                            failure_pc)
        ## Shared function for printing errors and failures.
        def print_details(d_list, d_csi, d_desc):
            print '\x1b[01m>> %s details\x1b[0m' % (d_desc)
            for (module, case, testname), (errtype, errstr, errtb) in d_list:
                print '%s [%s.%s] %s:\x1b[0m' % (d_csi, module, case,
                                                 testname)
                print '  - type      : %s' % (str(errtype))
                print '  - info      : %s' % (errstr)
                print '  - traceback :'
                tbinfo = traceback.extract_tb(errtb)
                for line in traceback.format_list(tbinfo):
                    # Ignore unittest-specific traceback info (useless).
                    if '/unittest.py' in line:
                        continue
                    print '    - %s' % (line)
                print ''

        if error_cnt > 0:
            print_details(self.result.errors, '\x1b[33;01m', 'Error')

        if failure_cnt > 0:
            print_details(self.result.failures, '\x1b[31;01m', 'Failure')

        print '\x1b[01m>> Done\x1b[0m'

    ## Prints info that tests are being prepared.
    def prepare(self):
        print '\x1b[01m>> Preparation\x1b[0m'

    ## Prints info that tests are being run.
    def run(self):
        print '\x1b[01m>> Tests\x1b[0m'

    ## Prints info that cleanup is being done.
    def cleanup(self):
        print '\x1b[1F\x1b[01m>> Cleanup\x1b[0m'

## XML Output handler class.
class _XMLOutput(IOutput):
    ## Constructor.
    # @param result TestResult object.
    # @param output_file File to write XML output to.
    # @param args Non-keyword arguments.
    # @param kwargs Keyword arguments.
    def __init__(self, result, output_file=None, *args, **kwargs):
        IOutput.__init__(self, result, *args, **kwargs)

        ## Output file object.
        self.fp = None
        ## XML element of current module.
        self.current_module = None
        ## XML element of current TestCase.
        self.current_case = None
        ## XML document.
        self.doc = None
        ## XML root element.
        self.xml_root = None
        
        if output_file:
            try:
                self.fp = open(output_file, 'w')
            except IOError, e:
                sys.stderr.write('Could not open %s for writing: %s' \
                                 % (output_file, e))
                sys.stderr.flush()
                sys.exit(1)
        else:
            self.fp = sys.stderr
    ## Handles a new test module.
    # @param module Module's name.
    def new_module(self, module):
        module_elem = self.doc.createElement('module')
        module_elem.setAttribute('name', module)
        self.xml_root.appendChild(module_elem)
        self.current_module = module_elem

    ## Handles a new test case.
    # @param module Module's name.
    # @param case TestCase's name.
    def new_case(self, module, case):
        case_elem = self.doc.createElement('case')
        case_elem.setAttribute('name', case)
        self.current_module.appendChild(case_elem)
        self.current_case = case_elem

    ## Stub, does nothing.
    # @param module Module's name.
    # @param case TestCase's name.
    # @param testname Test's name.
    def test_started(self, module, case, testname):
        pass

    ## Creates a 'test' XML element.
    # @param testname Test's name.
    # @param status Test's status.
    # @returns 'test' XML element.
    def _create_test_element(self, testname, status):
        test = self.doc.createElement('test')
        test.setAttribute('name', testname)
        test.setAttribute('status', status)
        self.current_case.appendChild(test)
        return test
    
    ## Creates XML elements for tests that failed/had an error.
    # @param elem_name Element name (error or failure).
    # @param test_elem Test XML element.
    # @param errobj Tuple of error type, error info and error traceback.
    def _test_element_add_error_or_failure(self, elem_name, test_elem, errobj):
        errtype, errstr, errtb = errobj
        elem = self.doc.createElement(elem_name)
        elem.setAttribute('type', str(errtype))
        elem.setAttribute('info', str(errstr))

        tbinfo = traceback.extract_tb(errtb)
        tbelem = self.doc.createElement('traceback')
        elem.appendChild(tbelem)
        for fname, lineno, funcname, text in tbinfo:
            if '/unittest.py' in fname:
                continue
            
            entryelem = self.doc.createElement('entry')
            entryelem.setAttribute('filename', fname)
            entryelem.setAttribute('linenumber', str(lineno))
            entryelem.setAttribute('function', funcname)
            textnode = self.doc.createTextNode(text)
            entryelem.appendChild(textnode)
            tbelem.appendChild(entryelem)
            
        test_elem.appendChild(elem)

    ## Handles result of a test being success.
    # @param module Module's name.
    # @param case TestCase's name.
    # @param testname Test's name.
    def test_success(self, module, case, testname):
        self._create_test_element(testname, 'success')

    ## Handles result of a test being failure.
    # @param module Module's name.
    # @param case TestCase's name.
    # @param testname Test's name.
    # @param errobj Tuple of error type, error info and error traceback.
    def test_failure(self, module, case, testname, errobj):
        test = self._create_test_element(testname, 'failure')
        self._test_element_add_error_or_failure('failure', test, errobj)

    ## Handles result of a test being error.
    # @param module Module's name.
    # @param case TestCase's name.
    # @param testname Test's name.
    # @param errobj Tuple of error type, error info and error traceback.
    def test_error(self, module, case, testname, errobj):
        test = self._create_test_element(testname, 'error')
        self._test_element_add_error_or_failure('error', test, errobj)

    ## Prints info that tests are being prepared and prepares XML document.
    def prepare(self):
        xmldoc = getDOMImplementation()
        self.doc = xmldoc.createDocument('', 'unittest', '')
        self.xml_root = self.doc.firstChild
        self.doc.appendChild(self.xml_root)
        self.xml_root.setAttribute('started', str(datetime.now()))
        self.current_module = None
        self.current_case = None
        print '>> Preparation'

    ## Stub, does nothing.
    def done(self):
        pass

    ## Prints info that cleanup is being done.
    def cleanup(self):
        print '>> Cleanup'

    ## Finished generation of XML document and writes it to file/stderr.
    def after_cleanup(self):
        self.xml_root.setAttribute('finished', str(datetime.now()))
        self.fp.write(self.doc.toprettyxml())
        self.fp.flush()
        if self.fp != sys.stderr:
            print '>> Written results to %s.' % (self.fp.name)
            self.fp.close()

    ## Prints info that tests are being run.
    def run(self):
        print '>> Tests'

## Set to _XMLOutput after checking that xml.dom is available (via HAVE_XML).
XMLOutput = IOutput

if HAVE_XML:
    XMLOutput = _XMLOutput
