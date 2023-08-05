# -*- coding:utf-8 -*-

## Copyright (c) 2006, 2007, Joerg Zinke, Jonas Weismueller (team@petunial.com)
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions
## are met:
##
##  * Redistributions of source code must retain the above copyright
##    notice, this list of conditions and the following disclaimer.
##  * Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in
##    the documentation and/or other materials provided with the
##    distribution.
##  * Neither the name of the Petunial Team nor the names of its
##    contributors may be used to endorse or promote products derived
##    from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
## FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
## COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
## INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
## BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
## CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
## LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
## ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
## POSSIBILITY OF SUCH DAMAGE.

"""

latua - test/latua/core/test_configuration.py

latua test class for configuration

"""

__version__ = "$Revision: 302 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/test/latua/_system/test_configuration.py $

## standard modules
import os
import unittest

## latua modules
import latua
import latua.error

class ConfigurationTestCase(unittest.TestCase):
    """Test for saving and loading configuration."""
    def setUp(self):
        """Test set up."""
        self.__base = latua.Base()
        self.__system = latua.System()
        test_directory = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        self.__test_configuration = os.path.join(test_directory, "test_files", "test_configuration.cfg")
        self.__test_configuration_parse = os.path.join(test_directory, "test_files", "test_configuration_parse.cfg")

    def test_directory(self):
        """Test configuration directory exception."""
        self.assertRaises(latua.error.ConfigurationError,
                          self.__system.configuration.write_file, "")

    def test_exists(self):
        """Test configuration file does not exists exception."""
        self.assertRaises(latua.error.ConfigurationError,
                          self.__system.configuration.read_file, "")

    def test_open(self):
        """Test configuration file open exception."""
        os.chmod(self.__test_configuration, 0000)
        ## root and admin are allowed to open everything
        if not self.__base.platform.user == self.__base.platform.admin:
            self.assertRaises(latua.error.ConfigurationError,
                              self.__system.configuration.write_file,
                              self.__test_configuration)
        os.chmod(self.__test_configuration, 0644)

    def test_parse(self):
        """Test configuration parse error."""
        self.assertRaises(latua.error.ConfigurationError,
                          self.__system.configuration.read_file,
                          self.__test_configuration_parse)

    def test_read(self):
        """Test configuration file reading."""
        self.__system.configuration.read_file(self.__test_configuration)
        result = self.__system.configuration.has_section("test_section")
        self.assertEqual(result, True,
                         "failed to read configuration does not contain section")
        result = self.__system.configuration.has_option("test_section",
                                                        "test_option")
        self.assertEqual(result, True,
                         "failed to read configurations does not contain option")
        result = self.__system.configuration.get("test_section",
                                                 "test_option")
        self.assertEqual(result, "test_value",
                         "failed to read configuration option has wrong value")

    def test_write(self):
        """Test configuration file writing."""
        os.remove(self.__test_configuration)
        self.__system.configuration.add_section("test_section")
        result = self.__system.configuration.set("test_section",
                                                 "test_option",
                                                 "test_value")
        ## write configuration
        self.__system.configuration.write_file(self.__test_configuration)
        ## read configuration and check
        self.__system.configuration.read_file(self.__test_configuration)
        result = self.__system.configuration.has_section("test_section")
        self.assertEqual(result, True,
                         "failed to write configuration does not contain section")
        result = self.__system.configuration.has_option("test_section",
                                                        "test_option")
        self.assertEqual(result, True,
                         "failed to write configurations does not contain option")
        result = self.__system.configuration.get("test_section",
                                                 "test_option")
        self.assertEqual(result, "test_value",
                         "failed to write configuration option has wrong value")

    def tearDown(self):
        """Clean up after tests."""
        self.__test_configuration_parse = None
        self.__test_configuration = None
        self.__system = None
        self.__base = None

if __name__ == "__main__":
    print """
do not run this file directly, use latua test script

    """
