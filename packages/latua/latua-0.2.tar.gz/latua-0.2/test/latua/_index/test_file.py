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

latua - test/latua/_index/test_file.py

latua test class for index file

"""

__version__ = "$Revision: 302 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/test/latua/_index/test_file.py $

## standard modules
import os
import stat
import unittest

## latua modules
import latua
import latua._context

class FileTestCase(unittest.TestCase):
    """Test for latua index file functions."""
    def setUp(self):
        """Test set up."""
        latua._context._database = None
        self.__index = latua.Index("index.db")
        test_directory = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        self.__test_text = os.path.join(test_directory, "test_files", "test_text.txt")
        self.__test_text_second = os.path.join(test_directory, "test_files", "test_text_second.txt")

    def test_add(self):
        """Test index file add."""
        self.__index.file.add(self.__test_text)
        mtime = os.stat(self.__test_text)[stat.ST_MTIME]
        filesize = os.stat(self.__test_text)[stat.ST_SIZE]
        result = self.__index.database._cursor.execute("select id, filename, filetype, filesize, mtime, lastline from view_files where filename=?", (self.__test_text,))
        result = result.fetchone()
        self.assertEqual(result["id"], 1,
                         "failed to add id to index files table")
        self.assertEqual(result["filename"], self.__test_text,
                         "failed to add filename to index files table")
        self.assertEqual(result["filetype"], "text",
                         "failed to add filetype to index files table")
        self.assertEqual(result["filesize"], filesize,
                         "failed to add filesize to index files table")
        self.assertEqual(result["mtime"], mtime,
                         "failed to add mtime to index files table")
        self.assertEqual(result["lastline"], 3,
                         "failed to add lastline to index files table")

    def test_exists(self):
        """Test index file does not exists exception."""
        self.assertRaises(latua.error.FileError,
                          self.__index.file.add, "")
        self.assertRaises(latua.error.FileError,
                          self.__index.file.update, "")
        self.assertRaises(latua.error.FileError,
                          self.__index.file.meta, "")
        self.assertRaises(latua.error.FileError,
                          self.__index.file.rename, "", "")

    def test_filetype(self):
        """Test index filetype exception."""
        self.assertRaises(latua.error.FileError,
                          self.__index.file.add, self.__test_text, "")

    def test_filename(self):
        """Test index filename exception."""
        self.assertRaises(latua.error.FileError,
                          self.__index.file.update, "test")

    def test_meta(self):
        """Test index file meta."""
        self.__index.file.add(self.__test_text)
        mtime = os.stat(self.__test_text)[stat.ST_MTIME]
        filesize = os.stat(self.__test_text)[stat.ST_SIZE]
        result = self.__index.file.meta(self.__test_text)
        self.assertEqual(result["filename"], self.__test_text,
                         "failed to get filename from files table")
        self.assertEqual(result["filetype"], "text",
                         "failed to get filetype from files table")
        self.assertEqual(result["filesize"], filesize,
                         "failed to get filesize from files table")
        self.assertEqual(result["mtime"], mtime,
                         "failed to get mtime from files table")
        self.assertEqual(result["lastline"], 3,
                         "failed to get linenumber from files table")

    def test_update(self):
        """Test index file update."""
        self.__index.file.add(self.__test_text)
        ## second file contains data of first file twice
        self.__index.file.rename(self.__test_text, self.__test_text_second)
        self.__index.file.update(self.__test_text_second)
        mtime = os.stat(self.__test_text_second)[stat.ST_MTIME]
        filesize = os.stat(self.__test_text_second)[stat.ST_SIZE]
        result = self.__index.database._cursor.execute("select id, filename, filetype, filesize, mtime, lastline from view_files where filename=?", (self.__test_text_second,))
        result = result.fetchone()
        self.assertEqual(result["id"], 1,
                         "failed to update id in index files table")
        self.assertEqual(result["filename"], self.__test_text_second,
                         "failed to update filename in index files table")
        self.assertEqual(result["filetype"], "text",
                         "failed to update filetype in index files table")
        self.assertEqual(result["filesize"], filesize,
                         "failed to update filesize in index files table")
        self.assertEqual(result["mtime"], mtime,
                         "failed to update mtime in index files table")
        self.assertEqual(result["lastline"], 6,
                         "failed to update linenumber in index files table")

    def test_remove(self):
        """Test index file remove."""
        tables = ["files", "lines", "words", "lines_words"]
        self.__index.file.add(self.__test_text)
        ## remove file
        self.__index.file.remove(self.__test_text)
        ## all database tables should be empty after removal
        for item in tables:
            result = self.__index.database._cursor.execute("select count(*) from %s" % (item))
            result = result.fetchone()
            self.assertEqual(result[0], 0,
                             "failed to remove file from database table %s" % (item))

    def test_rename(self):
        """Test index file rename."""
        self.__index.file.add(self.__test_text)
        self.__index.file.rename(self.__test_text, self.__test_text_second)
        result = self.__index.database._cursor.execute("select filename from view_files where filename=?", (self.__test_text_second,))
        result = result.fetchone()
        self.assertEqual(result["filename"], self.__test_text_second,
                         "failed to rename file in files table")

    def test_twice(self):
        """Test index add file twice exception."""
        self.__index.file.add(self.__test_text)
        self.assertRaises(latua.error.FileError,
                          self.__index.file.add, self.__test_text)

    def tearDown(self):
        """Clean up after tests."""
        self.__test_text_second = None
        self.__test_text = None
        self.__index = None
        ## not all tests really commit data
        if os.path.isfile("index.db"):
            os.remove("index.db")

if __name__ == "__main__":
    print """
do not run this file directly, use latua test script

    """
