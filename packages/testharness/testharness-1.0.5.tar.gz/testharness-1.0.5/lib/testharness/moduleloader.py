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
import types
from pprint import pprint

from testbase import TestBase

class ModuleLoader:
    """This Class loads only classes derived from TestBase
    into the test harness.
    """
    def load(self, python_module_name):
        """Called to load a module and generate a dictionary
        of all module classes found in it.
        """
        module_dictionary = {}
        # Load the python module file.
        module = __import__(python_module_name)
        # Get a list of items in the module.
        component_name_list = dir(module)

        # Now scan the list and only load classes derived
        # from TestBase (Excluding TestBase itself).
        for component_name in component_name_list:
            component = getattr(module, component_name)
            # python2.4 class or python2.3- class
            if type(component) == type(object) or type(component) == types.ClassType:
                #print "found class: ", component
                if issubclass(component, TestBase) and component != TestBase:
                    #print "it is a TestBase subclass"
                    module_dictionary[component_name] = component
                #else:
                #    print "isn't subclass of TestBase:", component


        # Return what we've found.
        return module_dictionary
