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

latua - test/latua/_index/test_connection.py

latua test class for index database connection

"""

__version__ = "$Revision: 293 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/test/latua/_index/test_connection.py $

## standard modules
import os
import string
import unittest

## latua modules
import latua
import latua._context
import latua._index._connection

class ConnectionTestCase(unittest.TestCase):
    """Test for latua index database functions."""
    def setUp(self):
        """Test set up."""
        latua._context._database = None
        self.__index = latua.Index("index.db")

    def test_connection(self):
        """Test index database connection."""
        self.assertNotEqual(self.__index.database._connection, None,
                            "failed to connect to database")
        self.assertNotEqual(self.__index.database._cursor, None,
                            "failed to get cursor from database connection")
        self.assertNotEqual(self.__index.database._connection.row_factory, None,
                            "failed to get row factory for database connection")

    def test_context(self):
        """Test index database context initialization."""
        self.assertNotEqual(latua._context._database, None,
                            "database context not set")

    def test_create(self):
        """Test index database create regular expression function."""
        result = self.__index.database._cursor.execute("select name from sqlite_master where regexp(?,name)", ("^files$",))
        result = result.fetchone()
        self.assertEqual(result["name"], "files",
                         "failed to use regular expression function")

    def test_expression(self):
        """Test index database regular expression function."""
        expression = "^.es.*$"
        regular_expression_function = getattr(self.__index.database, "_Connection__expression")
        self.assertEqual(regular_expression_function(expression, "test"), True,
                         "failed to test regular expression does not match")
        self.assertEqual(regular_expression_function(expression, "False"), False,
                         "failed to test regular expression matched")

    def test_reinitialization(self):
        """Test index database connection reinitialization."""
        test_database = latua._index._connection._Connection("index.db")
        self.assertEqual(id(self.__index.database._connection), id(test_database._connection),
                         "database connection id does not match")

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
