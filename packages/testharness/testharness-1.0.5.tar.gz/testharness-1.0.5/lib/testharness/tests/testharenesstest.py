"""
Python testharness Module.

This TestHarness is intended to be used as a generic functional test framework.

Copyright (C) 2001-2006 Oisin Mulvihill.
Email: oisin.mulvihill@gmail.com

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library (see the file LICENSE.TXT); if not,
write to the Free Software Foundation, Inc., 59 Temple Place,
Suite 330, Boston, MA 02111-1307 USA.

"""
import os
import sys
import logging
import tempfile
import unittest
import StringIO


import testharness.testbase as testbase
import testharness.testharness as testharness
import testharness.testharnessconsole as testharnessconsole


test_config = """
[TestHarness]
#If this is yes the test harness will exit after the first failure.
assert_equals_failure_causes_exit = yes

[TheTestConfiguration]
some_uri = http://localhost:12/
value = 12
"""

class TheTest(testbase.TestBase):
    """
    """
    def __init__(self, test_harness):
        testbase.TestBase.__init__(self, test_harness)
        self.params = []

    def myFunction1(self, params):
        """A simple test function which can be called once the module is loaded.
        """
        self.params = params

    def func(self, params):
        return self.getConfig().get("TheTestConfiguration.value", "FAIL")

    def func1(self, params):
        return self.getConfig().get("TheTestConfiguration.some_uri", "FAIL")

    def func2(self, params):
        return 10

    def func3(self, params):
        return "Hello"


class TestHarnessTestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        self.thc = testharnessconsole.TestHarnessCommand(test_config, config_type = "is_text")
        self.tmpDir = tempfile.gettempdir()
        #print "self.tmpDir <%s>" % self.tmpDir

    def tearDown(self):
        self.thc = None


    def testModuleLoading(self):
        """Test the test harness module loading.
        """
        module_text = """
from testharness import testbase

# A test harness module is a python file with classes that are derived
# from test base. Every other class should be ignored. When the class is
# loaded it is instanciated. The loaded classes can be accessed in test
# harness script by the name: module_filename.ClassName

class ThisClassIsIgnored:
  #this class should be ignored as it doesn't derive from TestBase.
  pass


class ThisOneToo(object):
  #this class should be ignored as it doesn't derive from TestBase.
  pass


class MyClass(testbase.TestBase):
  def func(self, params):
    return 10

"""
        testmodfile = "ABC.py"
        tandp = os.path.join(self.tmpDir, testmodfile)
        try:
            os.remove(tandp)
        except OSError, e:
            # ok. not present to remove.
            pass
        try:
            os.remove(tandp+'c')
        except OSError, e:
            # ok. not present to remove.
            pass

        # Test use the temp dir to write modules to, in order to load
        # them the tempdir will need to be in the python path
        sys.path.insert(0, self.tmpDir)
        
        fd = open(tandp, "w")
        fd.write(module_text)
        fd.close()

        # Load the module, you don't need the .py extension
        command = "load %s" % (testmodfile.split('.')[0])
        self.thc.onecmd(command)

##        print "-- 2. here "
##        print os.listdir(self.tmpDir)
##        print


        # Invoke a test harness function and check what is returned:
        command = "%s.MyClass      func" % (testmodfile.split('.')[0])
        self.thc.onecmd(command)

##        print "-- 3. here "
##        print os.listdir(self.tmpDir)
##        print

        command = "assertEquals func should have returned 10. It didn't!, 10"
        self.thc.onecmd(command)

        # Check that the assertEquals function does indeed fail:
        command = "assertEquals func has failed correctly, ab21"
        try:
            self.thc.onecmd(command)
            raise SystemError, "This should have raised AssertEqualsFailure!"

        except testharness.AssertEqualsFailure, error:
            # ok.
            pass

        try:
            os.remove(tandp)
        except OSError, e:
            # ok. not present to remove.
            pass

        # Try loading a module that doesn't exist.
        command = "load testmodule_121212"
        try:
            self.thc.onecmd(command)
            raise SystemError, "This should have raised testmodule_121212"

        except testharness.ModuleNotFound, error:
            pass


    def testModuleLoadingAndScriptExecution(self):
        """Test I can load and that a script will run without errors.
        """
        module_text = """
import testharness.testbase as testbase

# A test harness module is a python file with classes that are derived
# from test base. Every other class should be ignored. When the class is
# loaded it is instanciated. The loaded classes can be accessed in test
# harness script by the name: module_filename.ClassName

class CrazyClass:
    #this class should be ignored as it doesn't derive from TestBase.
    pass


class Live(testbase.TestBase):
    def func(self, params):
        return 10

    def getCustomer(self, params):
        return 'bob'

    def sumValues(self, params):
        # params contents are strings:
        a = int(params[0])
        b = int(params[1])
        message = params[2]
        return '%s: %d' % (message, a + b)

    def add(self, params):
        return int(params[0]) + int(params[1])

"""
        testmodfile = "completerun.py"
        tandp = os.path.join(self.tmpDir, testmodfile)
        try:
            os.remove(tandp)
        except OSError, e:
            # ok. not present to remove.
            pass

        fd = open(tandp, "w")
        fd.write(module_text)
        fd.close()

        test_script = """
rem
rem  This is a test script example. As you can guess lines starting with the 'rem' command will be ignored.
rem

print loading the completerun
load completerun

rem This prints out the modules loaded to debug log level:
list

rem Call out test function and check it what it returns
completerun.Live func
assertEquals this should have returned 10!, 10

rem Try another function:
completerun.Live getCustomer
assertEquals this should have returned bob!, bob

rem Now try a function with arguments:
completerun.Live add 28, 7
assertEquals add failed! 28+7 should be 35!, 35

rem Now try a function with arguments:
completerun.Live sumValues 28, 7, the answer is
assertEquals sumValues failed!, the answer is: 35

"""
        # Run the script file, which should happen without raising any exceptions
        fd = StringIO.StringIO(test_script)
        self.thc.process(fd)
        try:
            os.remove(tandp)
        except OSError, e:
            # ok. not present to remove.
            pass


    def testTestHarnessModulesUsingConfig(self):
        """Test that a test harness module can recover information from a section in the configuration.
        """
        # Pretend that I loaded a module into the test harness:
        my_testbase = TheTest(self.thc.testHarness)
        self.thc.testHarness._addModule("test.TheTest", my_testbase)

        # Now try to use the module.class I "loaded":
        command = "test.TheTest func"
        self.thc.onecmd(command)

        #print "\n-- th " + "-" * 40
        #import pprint
        #pprint.pprint(self.thc.testHarness.getConfig())
        #print

        command = "assertEquals This should be 12, 12"
        self.thc.onecmd(command)

        # Now try to use the module.class I "loaded":
        command = "test.TheTest func1"
        self.thc.onecmd(command)

        command = "assertEquals This should be 12, http://localhost:12/"
        self.thc.onecmd(command)


    def testTestHarnessCommands(self):
        """Test that loaded modules and methods can be called.
        """
        # Pretend that I loaded a module into the test harness:
        my_testbase = TheTest(self.thc.testHarness)
        self.thc.testHarness._addModule("test.TheTest", my_testbase)

        # Now try to use the module.class I "loaded":
        command = "test.TheTest myFunction1 my arg 1, my arg 2, my arg 3"
        self.thc.onecmd(command)
        self.assertEquals(my_testbase.params, ["my arg 1", "my arg 2", "my arg 3",])

        # Invoke a test harness function and check what is returned:
        command = "test.TheTest        func2"
        self.thc.onecmd(command)
        command = "assertEquals func2 should have returned 10. It didn't!, 10"
        self.thc.onecmd(command)

        # Check that the assertEquals function does indeed fail:
        command = "assertEquals func2 has failed correctly, ab21"
        try:
            self.thc.onecmd(command)
            raise SystemError, "This should have raised AssertEqualsFailure!"

        except testharness.AssertEqualsFailure, error:
            # ok.
            pass


        # Invoke a test harness function and check what is returned:
        command = "test.TheTest        func3"
        self.thc.onecmd(command)
        command = "assertEquals func3 should have returned 'Hello'. It didn't!, Hello"
        self.thc.onecmd(command)

        # Check that the assertEquals function does indeed fail:
        command = "assertEquals func3 should have returned 'Hello'. It didn't!, some             text that   1212  was  returned"
        try:
            self.thc.onecmd(command)
            raise SystemError, "This should have raised AssertEqualsFailure!"

        except testharness.AssertEqualsFailure, error:
            # ok.
            pass


    def testTestHarnessInvalidModuleMethodHandling(self):
        """Test that unknown module and method names raise the correct exceptions.
        """
        command = "invalidmodule.invalidclass someCommand"
        try:
            self.thc.onecmd(command)
            raise SystemError, "This should have raised ModuleNotFound!"

        except testharness.ModuleNotFound, error:
            pass




    def testTestHarnessModuleParsing(self):
        """Test that spaces don't through the module invoke....
        """
        correct_dict = {
            'module.class' : "web.Gui",
            'method' : "getMetrics",
            'params' : ["provider", "serverXray", "count", "1", "weeks", "2004-05-05 13:26:45.0", ],
            }

        test_line = "web.Gui         getMetrics provider,serverXray,count,1,weeks,2004-05-05 13:26:45.0"
        results = self.thc.getParseLineText(test_line)

        """
        print
        print "\n-- results " + "-" * 40
        import pprint
        pprint.pprint(results)
        print
        print
        print "\n-- correct_dict " + "-" * 40
        pprint.pprint(correct_dict)
        print
        """
        self.assertEquals(results, correct_dict)

        test_line = "web.Gui getMetrics provider,serverXray,count,1,weeks,2004-05-05 13:26:45.0"
        results = self.thc.getParseLineText(test_line)
        self.assertEquals(results, correct_dict)

        test_line = "web.Gui getMetrics provider,     serverXray,count,     1, weeks,2004-05-05 13:26:45.0"
        results = self.thc.getParseLineText(test_line)
        self.assertEquals(results, correct_dict)

        correct_dict = {
            'module.class' : "web.Gui",
            'method' : "getMetrics",
            'params' : [ ],
            }
        test_line = "web.Gui            getMetrics           "
        results = self.thc.getParseLineText(test_line)
        self.assertEquals(results, correct_dict)

