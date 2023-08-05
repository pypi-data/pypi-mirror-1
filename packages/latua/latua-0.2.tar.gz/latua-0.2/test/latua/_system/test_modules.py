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

latua - test/latua/core/test_modules.py

latua test class for modules

"""

__version__ = "$Revision: 306 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/test/latua/_system/test_modules.py $

## standard modules
import os
import sys
import imp
import unittest

## latua modules
import latua
import latua.error

class ModulesTestCase(unittest.TestCase):
    """Test cases for latuas modules class."""
    def setUp(self):
        """Test set up."""
        self.__system = latua.System()
        self.__test_module = imp.new_module("test_module")

    def test_append(self):
        """Test modules modules append."""
        result = self.__system.modules.append(latua, "test_sub.test_module", self.__test_module)
        self.assertEqual(latua.test_sub.test_module, result)
        self.assertEqual(latua.test_sub.test_module, self.__test_module)
        self.assertEqual(sys.modules["latua.test_sub.test_module"], self.__test_module)
        self.assertEqual(latua.test_sub.test_module.__name__, "latua.test_sub.test_module")

    def test_empty(self):
        """Test modules exception."""
        self.assertRaises(latua.error.ModulesError, self.__system.modules.append, latua, "")

    def test_filename(self):
        """Test system filename conversion."""
        result = self.__system.modules.filename_modulename(os.path.join("latua", "test.py"))
        self.assertEqual(result, "latua.test",
                         "conversion of filename to modulename failed")

    def test_import(self):
        """Test modules import."""
        result = self.__system.modules._import("latua._version", "_Version")
        self.assertEqual(result.license, "BSD")

    def test_modulename(self):
        """Test system modulename conversion."""
        result = self.__system.modules.modulename_filename("latua.test")
        self.assertEqual(result, os.path.join("latua", "test%spy" % (os.path.extsep)),
                         "conversion of modulename to filename failed")

    def tearDown(self):
        """Clean up after tests."""
        self.__test_module = None
        self.__system = None

if __name__ == "__main__":
    print """
do not run this file directly, use latua test script

    """
