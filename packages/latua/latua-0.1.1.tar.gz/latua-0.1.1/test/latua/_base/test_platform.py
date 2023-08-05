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

latua - test/latua/_base/test_platform.py

latua test class for platform

"""

__version__ = "$Revision: 219 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1.1/test/latua/_base/test_platform.py $

## standard modules
import os
import unittest

## latua modules
import latua
import latua._context

class PlatformTestCase(unittest.TestCase):
    """Test cases for latuas platform classes."""
    def setUp(self):
        """Set up needed objects."""
        latua._context._platform = {}
        self.__base = latua.Base()

    def test_application(self):
        """Test platform application values."""
        self.assert_(len(self.__base.platform.application_name) > 0,
                     "application name is empty")
        ## application directory should exist (containing test script)
        self.assertEqual(os.path.isdir(self.__base.platform.application_directory),
                         True,
                         "application directory %s does not exists" % (self.__base.platform.application_directory))

    def test_context(self):
        """Test platform context initialization."""
        ## check actual number of platform dependent variables
        self.assertEqual(len(latua._context._platform), 15,
                         "wrong length of platform context")

    def test_dictionary(self):
        """Test platform class dictionary update."""
        platform = getattr(self.__base.platform, "_Platform__platform")
        self.assert_(len(platform) >= 0,
                     "no items found in platform dictionary")
        for item in platform:
            self.assertEqual(platform[item], getattr(self.__base.platform, item),
                             "%s is not updated in class dictionary" % (item))

    def test_directories(self):
        """Test platform directory values."""
        self.assertEqual(os.path.isdir(self.__base.platform.modules_directory),
                         True,
                         "modules directory %s does not exists" % (self.__base.platform.modules_directory))
        self.assertEqual(os.path.isdir(self.__base.platform.home_directory),
                         True,
                         "home directory %s does not exists" % (self.__base.platform.home_directory))
        self.assert_(len(self.__base.platform.data_directory) > 0,
                     "data directory is empty")
        self.assert_(len(self.__base.platform.configuration_directory) > 0,
                     "configuration directory is empty")

    def test_language(self):
        """Test platform language values."""
        self.assert_(len(self.__base.platform.languages) > 0,
                     "languages list is empty")
        ## locales directory should exist on unix
        ## but on other platforms often locales directory does not exists
        ## like on os x where sys-prefix points to python directory, so if no
        ## other python application is installed via distutils locales
        ## directory is not already created
        self.assert_(len(self.__base.platform.locales_directory) > 0,
                     "locales directory is empty")

    def test_logging(self):
        """Test platform logging values."""
        ## logging handler should not be none
        self.assertNotEqual(self.__base.platform.logging_handler, None,
                            "no logging handler set")
        self.assert_(len(self.__base.platform.logging_directory) > 0,
                     "logging directory is empty")

    def test_reinitialization(self):
        """Test platform reinitialization from context."""
        self.__base = None
        ## context should stay after removal of object
        self.assert_(len(latua._context._platform) >= 0,
                     "platform context removed after object removal")
        ## change context
        latua._context._platform["user"] = "latua_test_user"
        ## reinitialize class
        self.__base = latua.Base()
        ## check for changed context
        self.assertEqual(self.__base.platform.user, "latua_test_user",
                         "platform was and not updated from context")

    def test_user(self):
        """Test platform user value."""
        self.assert_(len(self.__base.platform.admin) > 0, "platform admin is empty")
        self.assert_(len(self.__base.platform.user) > 0, "platform user is empty")

    def tearDown(self):
        """Clean up after tests."""
        self.__base = None
        latua._context._platform = {}

if __name__ == "__main__":
    print """
do not run this file directly, use latua test script

    """
