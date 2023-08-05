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

latua - latua/_index/_search.py

latua class for searching through index

"""

__version__ = "$Revision: 299 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/latua/_index/_search.py $

## standard modules
import os
import string

## latua modules
import latua._index._connection

class _Search(latua._index._connection._Connection):
    """Search for words in index."""
    def __init__(self, filename):
        latua._index._connection._Connection.__init__(self, filename)

    def words(self, query, maxresults=10):
        """Search for words in index."""
        words = []
        if not len(query) == 0:
            query = query.lower()
            result = self._cursor.execute("select distinct word from words where lower(word) like ? limit ?",  ("%%%s%%" % (query), maxresults))
            result = result.fetchall()
            for item in result:
                words.append(item["word"])
        else:
            raise latua.error.SearchError("None", "could not search for query", "given query is empty")
        return words

    def expression(self, expression, maxresults=10, regular_expression=False):
        """Search for regular expression in word index."""
        lines = []
## todo: optimize this query to use indexes correctly and get rid of the
## nested for-loops below
## this single select query took 6 seconds on a 50 MB index file
## and the nested for-loops below took just 1 second
#        sql = """\
#select filename, linenumber, seek, word from words, lines, lines_words, view_files
#where regexp(?, words.word)
#and words.id = lines_words.words_id
#and lines.id = lines_words.lines_id
#and view_files.id = lines.file_id
#limit ?
#"""
        if not len(expression) == 0:
            if regular_expression:
                result = self._cursor.execute("select id, word from words where regexp(?, words.word) limit ?", (expression, maxresults))
            else:
                result = self._cursor.execute("select id, word from words where lower(word) like ? limit ?",  ("%%%s%%" % (expression), maxresults))
            words = result.fetchall()
            for word in words:
                if len(lines) < maxresults:
                    result = self._cursor.execute("select distinct lines_id from lines_words where words_id=? limit ?", (word["id"], (int(maxresults) - len(lines))))
                    lines_words = result.fetchall()
                    for line_word in lines_words:
                        result = self._cursor.execute("select filename, linenumber, seek from lines, view_files where lines.id=? and lines.file_id=view_files.id", (line_word["lines_id"],))
                        for item in result:
                            ## get line from file
                            filehandle = open(item["filename"], "rb")
                            filehandle.seek(item["seek"])
                            lines.append({"word":       word["word"],
                                          "filename":   item["filename"],
                                          "linenumber": item["linenumber"],
                                          "line":       filehandle.readline()})
                            filehandle.close()
        else:
            raise latua.error.SearchError("None", "could not search for regular expression", "given regular expression is empty")
        return lines


if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """
