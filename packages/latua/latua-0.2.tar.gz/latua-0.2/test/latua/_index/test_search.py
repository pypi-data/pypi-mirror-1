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

latua - test/latua/_index/test_search.py

latua test class for index search

"""

__version__ = "$Revision: 302 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/test/latua/_index/test_search.py $

## standard modules
import os
import unittest

## latua modules
import latua
import latua._context

class SearchTestCase(unittest.TestCase):
    """Test for latua search functions."""
    def setUp(self):
        """Test set up."""
        latua._context._database = None
        self.__index = latua.Index("index.db")
        test_directory = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        self.__test_text = os.path.join(test_directory, "test_files", "test_text.txt")

    def test_empty(self):
        """Test index search empty exception."""
        self.assertRaises(latua.error.SearchError,
                          self.__index.search.words, "")
        self.assertRaises(latua.error.SearchError,
                          self.__index.search.expression, "")

    def test_words(self):
        """Test index search words."""
        self.__index.file.add(self.__test_text)
        result = self.__index.search.words("es")
        self.assertEqual(len(result), 1,
                        "failed to match len of result")
        self.assertEqual("test" in result, True,
                        "failed to find word test")
        result = self.__index.search.words("bar")
        self.assertEqual(len(result), 2,
                        "failed to match len of result")
        self.assertEqual("bar" in result, True,
                        "failed to find word bar")
        self.assertEqual("foobar" in result, True,
                        "failed to find word foobar")

    def test_expression(self):
        """Test index search regular expression."""
        self.__index.file.add(self.__test_text)
        result = self.__index.search.expression("es")
        for item in result:
            self.assertEqual("test", item["word"],
                            "failed to find keywords line")
            self.assertEqual(item["filename"], self.__test_text,
                            "failed to find keywords filename")
            self.assertEqual(int(item["linenumber"]) in [1, 3], True,
                            "failed to find keywords lineumbers")
            self.assertEqual("test" in item["line"], True,
                            "failed to find keywords line")
        result = self.__index.search.expression("^.es.*$", regular_expression=True)
        for item in result:
            self.assertEqual("test", item["word"],
                            "failed to find keywords line")
            self.assertEqual(item["filename"], self.__test_text,
                            "failed to find keywords filename")
            self.assertEqual(int(item["linenumber"]) in [1, 3], True,
                            "failed to find keywords lineumbers")
            self.assertEqual("test" in item["line"], True,
                            "failed to find keywords line")

    def tearDown(self):
        """Clean up after tests."""
        self.__test_text = None
        self.__index = None
        ## not all tests really commit data
        if os.path.isfile("index.db"):
            os.remove("index.db")

if __name__ == "__main__":
    print """
do not run this file directly, use latua test script

    """
