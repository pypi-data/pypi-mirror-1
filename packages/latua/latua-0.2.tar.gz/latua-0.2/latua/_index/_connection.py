# -*- coding: utf-8 -*-

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

latua - latua/_index/_connection.py

latua index database connection class

"""

__version__ = "$Revision: 298 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/latua/_index/_connection.py $

## standard modules
import re
import string

## sqlite
try:
    import sqlite3 as database
except ImportError, error:
    from pysqlite2 import dbapi2 as database

## latua modules
import latua._context

class _Connection(object):
    """Index database connection class."""
    def __init__(self, filename):
        self._connection = latua._context._database
        if self._connection == None:
            ## first time initialization
            self.__connect(filename)
        self._cursor = self._connection.cursor()

    def __expression(self, expression, term):
        """Check if term matches the regular expression."""
        if term == None:
            ## workaround for sqlite encoding issues
            return False
        regular_expression = re.compile(expression)
        return regular_expression.match(term) is not None

    def __connect(self, filename):
        """Connect to database."""
        self._connection = database.connect(filename)
        ## save connection back into context
        latua._context._database = self._connection
        self._connection.row_factory = database.Row
        ## create the function "regexp" for the regexp operator of sqlite
        self._connection.create_function("regexp", 2, self.__expression)

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """
