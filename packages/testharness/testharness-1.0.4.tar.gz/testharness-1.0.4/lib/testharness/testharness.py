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
import sys
import types
import string
import logging

from moduleloader import ModuleLoader
from configfilemanager import ConfigFileManager


class AssertEqualsFailure(Exception):
    """Raised when assert equals fails.
    """


class ModuleNotFound(Exception):
    """Raised when a module that has not been loaded has been used.
    """


class ModuleError(Exception):
    """
    """



class MethodNotFound(Exception):
    """Raised when a method used in the script was not found in the specified module.
    """


class TestHarness:
    """
    """
    def __init__(self, command_console, config_file_text):
        """
        """
        self.log = logging.getLogger("testharness.testharness.TestHarness")

        # Read the test harness config and setup the config dictionary.
        self.configManager = ConfigFileManager()
        self.configManager.read(config_file_text)

        self.configDict = self.configManager.getConfigDictionary()

        #Get test harness settings.
        self.assertEqualsCausesExit = self.configDict.get("TestHarness.assert_equals_failure_causes_exit", "yes")

        # Set up the rest of the parts.
        self.__moduleLoader = ModuleLoader()
        self.__moduleDictionary = {}
        self.__commandConsole = command_console
        self.__assertArgument = None


    def getAssertEqualsCausesExit(self):
        """Returns 'yes' if assert equals should cause test harness to exit
        if it fails, and 'no' if the test harness should continue going.
        """
        return self.assertEqualsCausesExit

    def getConfig(self):
        """Called by modules to get the config dictionary created from test.ini
        config file.
        """
        return self.configManager.getConfigDictionary()


    def getAssertValue(self):
        """Called to return the first string argument that assertEquals
        will compare to.
        """
        return self.__assertArgument


    def setAssertValue(self, value):
        """Called to set the next argument assertEquals will used
        to be compared against. All values are converted to
        strings for comparison with the string arg obtained from
        the script file.
        """
        if types.StringType == type(value):
            self.__assertArgument = value

        else:
            self.__assertArgument = str(value)



    def assertEquals(self, error_message, compare_value):
        """Called to check a string argument against what
        getReturnInfo() returns.

        Returned
            0: assertEquals ok.
            1: assertEquals failed.

        """
        arg1 = string.strip(compare_value)
        arg2 = string.strip(self.getAssertValue())
        #print "string.strip(compare_value) - <%s>." % arg1, compare_value
        #print "string.strip(self.getAssertValue()) - <%s>." % arg2
        if arg1 != arg2:
            message = "assertEquals: %s. script value <%s> is not equal to what was returned <%s>" % (error_message, arg1, arg2)
            self.log.error(message)
            raise AssertEqualsFailure, message


    def fail(self, params):
        """Called to fail the current test.
        """
        self.log.error("fail: This test has been failed manually.")
        sys.exit(1)


    def _addModule(self, module_name, module):
        """Called to add a module to the module dictionary.

        This function is used for testing.
        """
        self.__moduleDictionary[module_name] = module


    def load(self, python_module_name):
        """Called to load a module into the test harness.
        """
        # Attempt to load the module.
        try:
            module_dictionary = self.__moduleLoader.load(python_module_name)
        except ImportError, error:
            raise ModuleNotFound, "Error loading module '%s': %s" % (python_module_name, sys.exc_value)

        # Check if anything was loaded.
        if not module_dictionary == {}:
            # Now go through the dictionary creating and starting each loaded module.
            mod_name_list = module_dictionary.keys()
            for mod_name in mod_name_list:
                mod = module_dictionary[mod_name]
                mod_instance = mod(self)
                #
                # I'm not going to start the module here. I'll leave that to the user.
                # mod_instance.start(self)
                #
                # Finally store the module in the test harness module dictionary.
                key = python_module_name + '.' + mod_name
                self._addModule(key, mod_instance)

        else:
            msg="load <%s> contains no TestBase children!" % (python_module_name)
            self.log.error(msg)
            raise ModuleError, msg


    def start(self, module_class):
        """Call the given modules start() method.
        """
        try:
            return self.__moduleDictionary[module_class].start('')
        except KeyError:
            self.log.error("start: module <%s> not found!" % (str(module_class)))


    def stop(self, module_class):
        """Call the given modules stop() method.

        dict = {
            'module.class' : '...',
            'method' : '...',
            'params' : [...],
            }
        """
        try:
            return self.__moduleDictionary[module_class].stop('')
        except KeyError:
            self.log.error("stop: module <%s> not found!" % (str(module_class)))


    def moduleList(self):
        """Called to view all loaded test harness modules.
        """
        module_name_list = self.__moduleDictionary.keys()
        if not module_name_list == []:
            self.log.info("Modules currently loaded - <%s>" % str(module_name_list))
        else:
            self.log.info("No Modules currently loaded.")


    def inspect(self, module_class):
        """Called to view information about a loaded module.
        """
        try:
            return self.__moduleDictionary[module_class].inspect(module_class)
        except KeyError:
            self.log.error("inspect: module <%s> not found!" % (str(module_class)))


    def evaluate(self, dict):
        """Called to invoke a modules method and pass a set of parameters to it.

        dict = {
            'module.class' : '...',
            'method' : '...',
            'params' : [...],
            }
        """
        the_module = self.__moduleDictionary.get(dict['module.class'])
        if not the_module:
            raise ModuleNotFound, "The module '%s' was not found in the loaded modules." % dict['module.class']

        the_method = dict['method']
        returned = the_module.evaluate(the_method, dict['params'])

        self.setAssertValue(returned)
        #print "%s.%s returned" % (dict['module.class'], dict['method'])
        #print self.getAssertValue()


    def shutdown(self):
        """Shuts down all modules.
        """
        module_name_list = self.__moduleDictionary.keys()
        for module_name in module_name_list:
            #print 'Stopping -', module_name
            try:
                self.__moduleDictionary[module_name].stop('')
            except:
                self.log.error("Failed to stop <%s> exception <%s: %s>." % (module_name, sys.exc_type, sys.exc_value))


    def __del__(self):
        try:
            self.shutdown()
        except:
            pass




