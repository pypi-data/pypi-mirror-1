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

latua - test/latua/core/test_crypt.py

latua test class for crypt

"""

__version__ = "$Revision: 177 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1.1/test/latua/_system/test_crypt.py $

## standard modules
import unittest

## latua modules
import latua._system._crypt

class CryptTestCase(unittest.TestCase):
    """Test for encryption and decryption."""
    def setUp(self):
        """Test set up."""
        self.__crypt = latua._system._crypt._Crypt()
        self.__ascii = "".join([chr(i) for i in range(0,255)])

    def test_correct(self):
        """Test crypt encryption."""
        encrypted = self.__crypt.encrypt(self.__ascii)
        result = self.__crypt.check(self.__ascii, encrypted)
        self.assertEqual(result, True, "could not verify encrypted text")

    def test_failure(self):
        """Test crypt failure."""
        encrypted = self.__crypt.encrypt(self.__ascii)
        result = self.__crypt.check("test", encrypted)
        self.assertEqual(result, False, "could not verify encrypted text")

    def test_generate(self):
        """Test crypt generate."""
        result = self.__crypt.generate()
        self.assertEqual(len(result), 8, "generated string has wrong length")
        result = self.__crypt.generate(2, "a")
        self.assertEqual(result, "aa", "generated string does not match")

    def tearDown(self):
        """Clean up after tests."""
        self.__ascii = None
        self.__crypt = None

if __name__ == "__main__":
    print """
do not run this file directly, use latua test script

    """
