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

latua - test/latua/_index/test_database.py

latua test class for index database

"""

__version__ = "$Revision: 293 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/test/latua/_index/test_database.py $

## standard modules
import os
import string
import unittest

## latua modules
import latua
import latua._context

class DatabaseTestCase(unittest.TestCase):
    """Test for latua index database functions."""
    def setUp(self):
        """Test set up."""
        latua._context._database = None
        self.__index = latua.Index("index.db")

    def test_indexes(self):
        """Test index database indexes initialization."""
        indexes = ["index_files_filename",
                   "index_lines_file_id",
                   "index_lines_linenumber",
                   "index_words_word",
                   "index_lines_words_lines_id_words_id"]
        for item in indexes:
            result = self.__index.database._cursor.execute("select count(name) from sqlite_master where name=?", (item,))
            result = result.fetchone()
            self.assertEqual(result[0], 1,
                             "failed to create %s database index" % (item))

    def test_maintenance(self):
        """Test index database maintenance."""
        self.__index.database.maintenance()
        database = ["files", "lines", "words", "lines_words",
                    "index_files_filename",
                    "index_lines_file_id",
                    "index_lines_linenumber",
                    "index_words_word",
                    "index_lines_words_lines_id_words_id"]
        ## all database items should exist after maintenance
        for item in database:
            result = self.__index.database._cursor.execute("select count(name) from sqlite_master where name=?", (item,))
            result = result.fetchone()
            self.assertEqual(result[0], 1,
                             "failed to find %s database item after maintenance" % (item))

    def test_reset(self):
        """Test index database reset."""
        self.__index.database._reset()
        database = ["files", "lines", "words", "lines_words"]
        ## all database items should be empty after reset
        for item in database:
            result = self.__index.database._cursor.execute("select count(*) from %s" % (item))
            result = result.fetchone()
            self.assertEqual(result[0], 0,
                             "failed to reset database item %s" % (item))

    def test_tables(self):
        """Test index database tables initialization."""
        tables = ["files", "lines", "words", "lines_words"]
        for item in tables:
            result = self.__index.database._cursor.execute("select count(name) from sqlite_master where name=?", (item,))
            result = result.fetchone()
            self.assertEqual(result[0], 1,
                             "failed to create %s database table" % (item))

    def test_triggers(self):
        """Test index database triggers initialization."""
        triggers = ["trigger_delete_files",
                    "trigger_delete_lines",
                    "trigger_delete_words",
                    "trigger_delete_lines_words"]
        for item in triggers:
            result = self.__index.database._cursor.execute("select count(name) from sqlite_master where name=?", (item,))
            result = result.fetchone()
            self.assertEqual(result[0], 1,
                             "failed to create %s database trigger" % (item))

    def test_views(self):
        """Test index database views initialization."""
        views = ["view_files"]
        for item in views:
            result = self.__index.database._cursor.execute("select count(name) from sqlite_master where name=?", (item,))
            result = result.fetchone()
            self.assertEqual(result[0], 1,
                             "failed to create %s database view" % (item))

    def tearDown(self):
        """Clean up after tests."""
        self.__index = None
        ## not all tests really commit data
        if os.path.isfile("index.db"):
            os.remove("index.db")

if __name__ == "__main__":
    print """
do not run this file directly, use latua test script

    """
