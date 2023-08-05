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

latua - test/latua/test_singleton.py

latua test class for singleton

"""

__version__ = "$Revision: 139 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1/test/latua/test_singleton.py $

## standard modules
import unittest

## latua modules
import latua.singleton

class SingletonTestCase(unittest.TestCase):
    """Test cases for latuas singleton and borg pattern."""
    def setUp(self):
        """Set up needed objects."""
        self.__borg_a = latua.singleton.Borg()
        self.__borg_b = latua.singleton.Borg()
        self.__singleton_a = latua.singleton.Singleton()
        self.__singleton_b = latua.singleton.Singleton()

    def test_object(self):
        """Test singleton and borg object ids."""
        self.assertNotEqual(id(self.__borg_a), id(self.__borg_b), "borgs does not have different object ids")
        self.assertEqual(id(self.__singleton_a), id(self.__singleton_b), "singletons does not have the same id")

    def test_shared(self):
        """Test singleton borg shared state."""
        self.__borg_a.attribute = "test"
        self.assertEqual(self.__borg_b.attribute, "test", "borg does not get shared state")
        ## and the other way around
        self.__borg_b.attribute = "test_attribute"
        self.assertEqual(self.__borg_a.attribute, "test_attribute", "borg does not share state")
        self.assertEqual(self.__borg_a.attribute, self.__borg_b.attribute, "borg does not share state")

    def test_singleton(self):
        """Test singleton state."""
        self.__singleton_a.attribute = "test"
        self.assertEqual(self.__singleton_b.attribute, "test", "singleton does not get shared state")
        ## and the other way around
        self.__singleton_b.attribute = "test_attribute"
        self.assertEqual(self.__singleton_a.attribute, "test_attribute", "singleton does not share state")
        self.assertEqual(self.__singleton_a.attribute, self.__singleton_b.attribute, "singleton does not share state")

    def tearDown(self):
        """Clean up after tests."""
        self.__borg_a = None
        self.__borg_b = None

if __name__ == "__main__":
    print """
do not run this file directly, use latua test script

    """
