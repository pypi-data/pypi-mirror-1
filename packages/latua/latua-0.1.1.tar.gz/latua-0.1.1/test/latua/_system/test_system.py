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

latua - test/latua/core/test_system.py

latua test class for system

"""

__version__ = "$Revision: 190 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1.1/test/latua/_system/test_system.py $

## standard modules
import unittest

## latua modules
import latua

class SystemTestCase(unittest.TestCase):
    """Test for latua system functions."""
    def setUp(self):
        """Test set up."""
        self.__system = latua.System()

    def test_sort(self):
        """Test system sorting of a dictionary."""
        dictionary = {"c": 1, "b": 2, "a": 3}
        result = self.__system.sort(dictionary)
        self.assertEqual(result, [3, 2, 1],
                         "sorting of dictionary by key failed")
        result = self.__system.sort(dictionary, values=True)
        self.assertEqual(result, [1, 2, 3],
                         "sorting of dictionary by value failed")

    def test_system(self):
        """Test system items."""
        result = self.__system.system("test")
        self.assertEqual(result, False, "failed to test non-system item")
        result = self.__system.system("_test")
        self.assertEqual(result, True, "failed to test system item")

    def tearDown(self):
        """Clean up after tests."""
        self.__system = None

if __name__ == "__main__":
    print """
do not run this file directly, use latua test script

    """
