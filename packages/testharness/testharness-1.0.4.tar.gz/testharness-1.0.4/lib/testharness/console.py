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
import cmd
import sys
import logging
try:
	import readline
except ImportError:
	pass #print 'No readline support available.'


class Console(cmd.Cmd):
	"""
	"""
	def __init__(self, startup_command = '', script_filename = ''):
		self.log = logging.getLogger("testharness.Console.Console")
		cmd.Cmd.__init__(self)
		self.__startUpCommandLine = startup_command
		self.__scriptFileName = script_filename

	def exit(self, params):
		"""Called by do_exit().

        The user must overide this function if they need any function called at exit
		time.
		"""
		pass

	def preloop(self):
		"""Called once just after the cmdoop() has been called.
		"""
		if not self.__startUpCommandLine == '':
			# A startup command is present. So lets use it.
			self.onecmd(self.__startUpCommandLine)

		# Check if there's a script to run.
		if not self.__scriptFileName == '':
			# Yes, so run it.
			self.processScript(self.__scriptFileName)

	def emptyline(self):
		"""Just ignore empty lines.
		"""
		pass

	def default(self, line):
		"""Called when it doesn't know what to do with something.
		"""
		self.log.error("I don\'t know what to do with - <%s>." % line)


	def processScript(self, script_filename):
		"""Called to process a script file containing test harness commands.
		"""
		self.log.debug("Processing the script file <%s> now." % script_filename)
		fd = open(script_filename)
		try:
			self.process(fd)
		finally:
			fd.close()


	def process(self, fileobject):
		commands = ''
		line_count = 1
		the_line = ""
		try:
			for line in fileobject.readlines():
				the_line = line
				self.onecmd(line)
				line_count = line_count + 1

		except SystemExit, error:
			# Someone else handles this exception raise it again
			raise

		except:
			self.log.exception("Line %d  \"%s\" has caused the exception -" % (line_count, the_line.strip()))
			sys.exit(1)


	def do_exit(self, params):
		"""
		"""
		self.exit(params)
		sys.exit(0)

