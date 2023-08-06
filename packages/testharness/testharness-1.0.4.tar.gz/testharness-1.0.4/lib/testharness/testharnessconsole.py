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
import time
import pprint
import string
import logging

from console import Console
from testbase import TestBase
from testharness import TestHarness


class MethodNotFoundException(Exception):
	"""Raised when no method was found in a line of text read from the script file.
	"""


class TestHarnessCommand(Console):
	"""
	"""
	def __init__(self, config, config_type = "is_file_name", startup_command = '', script_filename = ''):
		"""
		"""
		self.log = logging.getLogger("testharness.testharnesscommand.TestHarnessCommand")

		Console.__init__(self, startup_command, script_filename)

		# Get the config file for the test harness.
		if config_type == 'is_file_name':
			config_file_text = open(config, 'r').read()
		elif config_type == 'is_text':
			config_file_text = config
		else:
			raise SystemError, 'I don\'t know what to do with config type %s' % config_type

		self.prompt = 'TestHarnessConsole> '
		self.intro = 'Type help or ? for help.'
		self.testHarness = TestHarness(self, config_file_text)


	def getConfig(self):
		"""Called to return the test harness configuration dictionary.
		"""
		return self.testHarness.getConfig()


	def getParseLineText(self, line_text):
		"""Called to parse the line of text given and recover the module.class, method
		and any arguments.

		returns:
				dict = {
					'module.class' : '...',
					'method' : '...',
					'params' : [...],
					}
		"""
		dict = {
			'module.class' : None,
			'method' : None,
			'params' : None,
			}

		# Recover the module.class as this should be the first thing,
		# stripped on extra whitespace:
		words = string.split(line_text, ' ')
		dict['module.class'] = words[0].strip() # module.class

		# Recover the method call stripping extra whitespace:
		index = 1
		args = []
		for w in words[index:]:
			w = w.strip()
			if w == '':
				index = index + 1
				continue
			else:
				# Found the method call:
				dict['method'] = w

				# The next position should be the begining of args:
				params = string.join(words[index+1:], ' ')
				params.strip()
				args = params.split(",")
				break

		# Finally find the begining of the arguments the recover
		# them stripping extra white spaces.
		index = 0
		dict['params'] = []
		for a in args:
			a = a.strip()
			if a != '':
				#print "a:",a
				# Found the method call:
				dict['params'].append(a)

		#print "\n-- dict " + "-" * 40
		#import pprint
		#pprint.pprint(dict)
		#print

		return dict


	def default(self, line_text):
		"""By default attempt to evaluate line_text string.
		"""
		self.onecmd('evaluate ' +  line_text)


	def do_assertEquals(self, line_text):
		"""Called to check a string argument against what
		getReturnInfo() returns. If the result isn't equal
		then an error is printed and SystemExit is raised.

		If the SystemError occurs the exit() method will be
		called to do whatever clean up is needed.
		"""
		params = string.split(line_text, ',')
		try:
			error_message = params[0]
			compare_value = params[1]
		except IndexError:
			raise SystemError, "TestHarnessConsole.do_assertEquals(): not enough arguments provided! args:", params

		if self.testHarness.assertEquals(error_message, compare_value):
			raise AssertEqualsFailure, ""

			# Assert equals failed.
			if self.testHarness.getAssertEqualsCausesExit() == "yes":
				self.exit()

	def do_fail(self, line_text):
		"""Called to fail the current test.
		"""
		params = string.split(line_text, ' ')
		return self.testHarness.fail(params[0])

	def do_sleep(self, line_text):
		"""Called to sleep for a certain amount of time
		"""
		params = string.split(line_text, ' ')
		if len(params) < 1:
			raise KeyError, "do_sleep: No sleep time was provided!"
		time.sleep(int(params[0]))

	def do_rem(self, line):
		"""Called when a comment is found. Just Ignore the line.
		"""
		pass

	def do_print(self, line):
		"""Called to print out to the console.
		"""
		self.log.info(line)

	def do_start(self, line_text):
		"""Called to start a loaded module.
		"""
		params = string.split(line_text, ' ')
		if len(params) < 1:
			raise KeyError, "do_start: No module class name provided!"
		return self.testHarness.start(params[0])

	def do_stop(self, line_text):
		"""Called to stop a loaded module.
		"""
		params = string.split(line_text, ' ')
		if len(params) < 1:
			raise KeyError, "do_stop: No module class name provided!"

		return self.testHarness.stop(params[0])

	def do_load(self, line_text):
		"""Called to load a module into the test harness.
		"""
		params = string.split(line_text, ' ')
		if len(params) < 1:
			raise KeyError, "do_load: No module class name provided!"
		return self.testHarness.load(params[0])

	def do_list(self, line_text):
		"""Called to view all loaded test harness modules.
		"""
		return self.testHarness.moduleList()

	def do_inspect(self, line_text):
		"""Called to view all commands in a loaded module.
		"""
		params = string.split(line_text, ' ')
		if len(params) < 1:
			raise KeyError, "do_inspect: No module class name provided!"
		return self.testHarness.inspect(params[0])

	def do_evaluate(self, line_text):
		"""Called to run a command in a loaded module.
		"""
		dict = self.getParseLineText(line_text)
		return self.testHarness.evaluate(dict)

	def do_shutdown(self, line_text=None):
		"""Called to shutdown a loaded module.
		"""
		self.testHarness.shutdown()

	def exit(self, params):
		"""Quits the test harness.
		"""
		self.testHarness.shutdown()



