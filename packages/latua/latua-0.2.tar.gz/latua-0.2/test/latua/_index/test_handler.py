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

latua - test/latua/_index/test_handler.py

latua test class for index handler

"""

__version__ = "$Revision: 302 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/test/latua/_index/test_handler.py $

## standard modules
import os
import unittest

## latua modules
import latua
import latua._context

class HandlerTestCase(unittest.TestCase):
    """Test for latua handler functions."""
    def setUp(self):
        """Test set up."""
        latua._context._database = None
        self.__index = latua.Index("index.db")
        test_directory = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        self.__test_text = os.path.join(test_directory, "test_files", "test_text.txt")

    def test_html(self):
        """Test index html handler."""
        pass

    def test_lines(self):
        """Test index lines table."""
        self.__index.file.add(self.__test_text)
        result = self.__index.database._cursor.execute("select id from lines")
        result = result.fetchall()
        for key, value in enumerate(result):
            if not key == (len(result) - 1):
                ## lines ids should increment exactly by one
                self.assertEqual(value["id"], (result[(key+1)]["id"] - 1),
                                "failed check ids in lines table")
        result = self.__index.database._cursor.execute("select linenumber, seek, file_id from lines order by linenumber")
        result = result.fetchall()
        for key, value in enumerate(result):
            if not key == (len(result) - 1):
                ## linenumber should increment exactly by one
                self.assertEqual(value["linenumber"], (result[(key+1)]["linenumber"] - 1),
                                "failed to check linenumbers in lines table")
                ## seek points should increment
                self.assert_(value["seek"] < result[(key+1)]["seek"],
                            "failed to check seek points in lines table")
                ## file id
                self.assertEqual(value["file_id"], 1)
        result = self.__index.database._cursor.execute("select filename from view_files where id=?", (1,))
        result = result.fetchone()
        ## file id form lines table should occur in files table
        self.assertEqual(self.__test_text, result["filename"])

    def test_words(self):
        """Test index words table."""
        self.__index.file.add(self.__test_text)
        result = self.__index.database._cursor.execute("select id, word from words")
        word_ids = result.fetchall()
        for item in word_ids:
            result = self.__index.database._cursor.execute("select lines_id from lines_words where words_id=?", (item["id"],))
            result.fetchone()
            self.assertNotEqual(result, None,
                                "failed to find word %s in word_lines table" % (item["word"]))

    def test_mp3(self):
        """Test index mp3 handler."""
        pass

    def test_pdf(self):
        """Test index pdf handler."""
        pass

    def test_text(self):
        """Test index text handler."""
        sql = """\
select filename, linenumber, seek, word from words, lines, lines_words, view_files
where words.word=?
and view_files.filename=?
and words.id = lines_words.words_id
and lines.id = lines_words.lines_id
and view_files.id = lines.file_id
"""
        self.__index.file.add(self.__test_text)
        result = self.__index.database._cursor.execute(sql, ("test", self.__test_text))
        result = result.fetchall()
        for item in result:
            self.assertEqual(item["filename"], self.__test_text,
                             "failed to index text filename")
            self.assert_(item["linenumber"] in [1, 3],
                              "failed to index text linenumbers")
            self.assert_(item["seek"] in [0, 29],
                              "failed to index text seek points")
            self.assertEqual(item["word"], "test",
                             "failed to index text word")

    def test_xml(self):
        """Test index xml handler."""
        pass

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
