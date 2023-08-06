#!/usr/bin/env python
"""
Python testharness Module.

Start the testharness and get its running tests.

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
import time
import string
import logging
import logging.config

from optparse import OptionParser

import utils
import config
import testharness
import testharnessconsole


def get_log():
    return logging.getLogger("testharness.main")


    

class TestScripts:
    """This is an iterator used to return the next script file
    to test, from a given list of script files.
    """
    def __init__(self, test_scripts, log):
        self.postion = 0
        self.log = log
        self.max = len(test_scripts)
        self.scripts= test_scripts
        self.loopCount = 0

    def __iter__(self):
        return self

    def next(self):
        """Called to return the next test script to test.
        """
        if self.postion >= self.max:
            raise StopIteration

        test_script = self.scripts[self.postion]
        self.postion = self.postion + 1
        return test_script


def run_scripts(options, test_harness):
    """Called to run the scripts listed in the tester ini file.
    """
    log = get_log()

    if options.script_filename:
        test_script = options.script_filename
        log.info("Running script <%s>" % test_script)
        try:
            test_harness.processScript(options.script_filename)

        except SystemExit, e:
            if e.code == 0:
                log.info("<%s> PASS" % test_script)
            else:
                log.error("<%s> FAIL" % test_script)

        except KeyboardInterrupt, e:
            log.info("Control-C caught. Exiting.")

        except:
            log.exception("test script <%s> failed! - " % test_script)


        # Done. Exit:
        log.info("Done.")
        return

    # Start processing test scripts:
    tests = test_harness.getConfig().get('TestHarness.tests', None)
    tests = string.split(tests, " ")

    # Make sure there are some scripts to run:
    if not tests[0]:
        log.error("No test scripts are listed in the config file!?")
        return

    log.info("Test scripts found <%s>" % tests)
    while 1:
        the_tests = TestScripts(tests, log)
        for test_script in the_tests:
            log.info("Running script <%s> here <%s>" % (test_script, options.test_path))
            test_script = os.path.join(options.test_path, test_script)
            try:
                test_harness.processScript(test_script)

            except SystemExit, e:
                if e.code == 0:
                    log.info("<%s> PASS" % test_script)
                else:
                    log.error("<%s> FAIL" % test_script)

            except KeyboardInterrupt, e:
                log.info("Control-C caught. Exiting.")
                break

            except:
                log.exception("test script <%s> failed! - " % test_script)

        if not options.repeat_test:
            # We're done, exit.
            break

        else:
            # Wait so we don't load the machine 100%
            time.sleep(0.1)


def main():
    """
    """
    parser = OptionParser()
    parser.add_option("-c", "--config", action="store", dest="config_filename", default=config.filename,
        help="This is the config file to be used.")
    parser.add_option("-l", "--logconfig", action="store", dest="logconfig_filename", default="log.ini",
        help="This is the config file to be used by the logging module.")
    parser.add_option("-i", "--interactive", action="store_true", dest="interactive_mode", default=False,
        help="Run the test harness in manual command entry mode.")
    parser.add_option("-f", "--file", action="store", dest="script_filename",
        help="This runs a specific test script.")
    parser.add_option("--loop", action="store_true", dest="repeat_test", default=False,
        help="Loop running the tests forever.")
    parser.add_option("--testpath", action="store", dest="test_path", default='acceptance',
        help="This is the config file to be used by the logging module.")
    (options, args) = parser.parse_args()


    # Set up python logging if a config file is given:
    if os.path.isfile(options.logconfig_filename):
        logging.config.fileConfig(options.logconfig_filename)

    log = get_log()

    if not os.path.isfile(options.config_filename):
        # No config given and the default doesn't exist, try creating it:
        pwd = os.path.abspath(os.curdir)
        thefile = os.path.join(pwd, config.filename)
        try:
            fd = file(thefile,"wb")
            fd.write(config.default)
            fd.close()
            log.debug("main: Created default config <%s>." % (thefile))
        except OSError, e:
            log.warn("main: I was unable to create the default testharness config <%s>." % (thefile))
            raise

    # Put the test scripts directory into the path so any code can be imported from it.
    if options.test_path:
        sys.path.append(options.test_path)


    test_harness = testharnessconsole.TestHarnessCommand(options.config_filename)
    if options.interactive_mode:
        # Run the command console:
        test_harness.cmdloop()

    else:
        # Run the scripts mentioned in the tester ini config file:
        run_scripts(options, test_harness)

    log.debug("Testing complete.")


if __name__ == '__main__':
    """Run the test harness"""
    main()

