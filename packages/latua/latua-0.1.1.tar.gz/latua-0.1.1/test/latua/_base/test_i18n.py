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

latua - test/latua/_base/test_i18n.py

latua test class for i18n

"""

__version__ = "$Revision: 139 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1.1/test/latua/_base/test_i18n.py $

## standard modules
import unittest

## latua modules
import latua
import latua._context
import latua.error

class I18nTestCase(unittest.TestCase):
    """Test cases for latuas i18n classes."""
    def setUp(self):
        """Set up needed objects."""
        latua._context._languages = []
        self.__base = latua.Base()

    def test_context(self):
        """Test i18n context initialization."""
        ## latua has no translations
        self.assert_(len(latua._context._languages) == 0,
                     "found items in i18n languages")

    def test_initialization(self):
        """Test i18n languages initialization."""
        ## latua has no translations
        self.assertRaises(latua.error.I18nError, self.__base.i18n.install_translation)

    def test_missing(self):
        """Test i18n missing language."""
        latua._context._languages.append("latua_test_language")
        self.assertRaises(latua.error.I18nError, self.__base.i18n.install_translation,
                          "latua_test")

    def test_reinitialization(self):
        """Test i18n reinitialization from context."""
        ## latua has no translations
        latua._context._languages.append("latua_test_language")
        self.__base = None
        ## context should stay after removal of object
        self.assert_(len(latua._context._languages) == 1,
                     "i18n context removed after object removal")
        ## reinitialize class
        self.__base = latua.Base()
        ## check for changed context
        self.assertEqual(self.__base.i18n.languages, ["latua_test_language"],
                         "i18n was and not updated from context")

    def tearDown(self):
        """Clean up after tests."""
        self.__base = None
        latua._context._languages = []

if __name__ == "__main__":
    print """
do not run this file directly, use latua test script

    """
