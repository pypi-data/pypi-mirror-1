"""
Python testharness Module.

The ConfigFileManager class provides the win32 style ini file handling, that
is used in the config files.

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
import string
import StringIO
import ConfigParser

class ConfigFileManager:
	"""
	Current usage:
		self.cm.get('CafeMonitor.uri') returns http://192.168.1.7:8080/test/cafe/
		self.cm.set('CafeMonitor.uri', "http://192.168.1.7:8080/test/cafe/")

	What would I could do if I ever figure out __getattr__():
		self.cm.CafeMonitor.uri  returns "http://192.168.1.7:8080/test/cafe/"
		self.cm.CafeMonitor.uri = "http://192.168.1.7:8080/test/cafe/"
	"""
	def __init__(self, debug = 0):
		self.debug = debug
		self.__parser = ConfigParser.ConfigParser()
		self.__configDictionary = {}

	def read(self, text_data):
		"""Read in the config from the given text string
		"""
		# Parse the config file.
		self.__parser.readfp(StringIO.StringIO(text_data))

		# Now create the dictionary of elements. Start by adding any default section which is just a dictionary.
		if self.debug:
			print 'Defaults:'
		default_dictionary = self.__parser.defaults()
		for default_key in default_dictionary.keys():
			key = 'default.' + default_key
			self.__configDictionary[key] = default_dictionary[default_key]
			if self.debug:
				print '\t%s = %s' % (key, self.__configDictionary[key])

		# Now add the rest of the sections.
		if self.debug:
			print 'Sections:'
		for section in self.__parser.sections():
			for option in self.__parser.options(section):
				key = '%s.%s' % (section, option)
				data = self.__parser.get(section, option)
				self.__configDictionary[key] = data
				if self.debug:
					print '\t%s = %s' % (key, self.__configDictionary[key])

	def write(self):
		"""Create the config text based on the current internal dictionary.

		Return is a string containing the new configuration.
		"""
		default_section = "[DEFAULT]\n"
		named_sections = {}
		other_sections = ""

		for key in self.__configDictionary.keys():
			words = string.split(key, '.')
			text = '%s = %s\n' % (string.join(words[1:]), self.__configDictionary[key])
			if words[0] == 'default':
				default_section = default_section + text
			else:
				try:
					named_sections[words[0]] = named_sections[words[0]] + text
				except KeyError:
					# This is the first time this section has appear to add its first string.
					named_sections[words[0]] = text
		for section_name in named_sections.keys():
			# Convert the named_sections into its final string.
			text = '[%s]\n%s\n' % (section_name, named_sections[section_name])
			other_sections = other_sections + text
		output = default_section + '\n' + other_sections

		if self.debug:
			print 'Write finished. The config is:'
			print output

		return output

	def getConfigDictionary(self):
		"""Return a copy of the internal dictionary.

		This is really only used by the unit test and is not for normal usage.
		"""
		return self.__configDictionary

	def setConfigDictionary(self, config_dict):
		"""
		"""
		self.__configDictionary = config_dict

	def get(self, key):
		"""Try to get a piece of information stored internally.

		Note if this information is not found then the exception KeyError will be raised.
		"""
		return self.__configDictionary[key]

	def set(self, key, data):
		"""Try to set a piece of information stored internally.

		Note if this information is not found then the exception KeyError will be raised.
		"""
		self.__configDictionary[key] = data
