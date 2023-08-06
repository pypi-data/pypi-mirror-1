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
class TestBase(object):
    """This is a base class that all modules must derive from
    if they want to be loaded into the test harness.
    """
    def __init__(self, test_harness_instance):
        """Given the running testharness instance just store it for future use.
        """
        self.__testHarness = test_harness_instance

    def getConfig(self):
        """Called to return the config dictionary from the test harness.
        """
        return self.__testHarness.getConfig()

    def start(self, params):
        """This is called after the module has been loaded and created.
        """

    def stop(self, params):
        """This is called to stop everything the module is doing and clean up.

        This is called usually when the test harness is being shutdown.
        """

    def inspect(self, params):
        """This is called to return and/or print some usefull
        information about this module.
        """

    def evaluate(self, method, params):
        """This is called do something with the parameter tupple passed in.
        """
        # Attempt to find the function in the instance.
        call = getattr(self, method)
        return call(params)
