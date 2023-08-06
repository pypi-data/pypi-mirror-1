"""
Project setuptools config...

Oisin Mulvihill
2006-07-10
"""
import sys
import logging
from setuptools import setup
from setuptools import find_packages


# These are where to find the various app and webapp
# packages, along with any other thirdparty stuff.
package_paths = [
    "./lib",
]
sys.path.extend(package_paths)

import testharness
from testharness import utils
utils.log_init(logging.CRITICAL)
#utils.log_init(logging.DEBUG)


Name='testharness'
ProjecUrl="" #"http://www.sourceweaver.com/testharness"
Version='1.0.5'
Author='Oisin Mulvihill'
AuthorEmail='oisin mulvihill at gmail com'
Maintainer=' Oisin Mulvihill'
Summary='This module is intended to be used as a generic functional test framework.'
License='LGPL'
ShortDescription="This is intended to be used as a generic functional test framework."

# Recover the ReStructuredText docs:
fd = file("lib/testharness/doc/TestHarness.txt")
Description=fd.read()
fd.close()


TestSuite = 'testharness.tests'

needed = []


entry_points = {
}

ProjectScripts = [
    'lib/testharness/scripts/goharness',
    'lib/testharness/scripts/goharness.py',
    'lib/testharness/scripts/goharness.bat',
]

PackageData = {
    # If any package contains *.txt or *.rst files, include them:
    '': ['*.txt', '*.rst', 'ini'],
}

EagerResources = [
]

# Make exe versions of the scripts:
EntryPoints = {
}


setup(
#    url=ProjecUrl,
    zip_safe=False,
    name=Name,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    license=License,
    test_suite=TestSuite,
    scripts=ProjectScripts,
    install_requires=needed,
    packages=find_packages('lib'),
    package_data=PackageData,
    package_dir = {'': 'lib'},
    eager_resources = EagerResources,
    entry_points = EntryPoints,
)
