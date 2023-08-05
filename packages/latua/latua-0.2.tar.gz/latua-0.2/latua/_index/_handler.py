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

latua - latua/_index/_handler.py

latua index file handler class

"""

__version__ = "$Revision: 293 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/latua/_index/_handler.py $

## standard modules
import os
import sets

## latua modules
import latua._index._connection

class _Handler(latua._index._connection._Connection):
    """Handler used to index words from different filetypes."""
    def __init__(self, filename):
        latua._index._connection._Connection.__init__(self, filename)
        ## supported filetypes
        self.filetypes = ["text"]#, "html", "xml", "pdf", "mp3"]

    def __words_lines(self, lines, words, lines_words):
        """Append words and linenumbers to database."""
        ## insert linenumbers and seek points into database
        self._cursor.executemany("insert or replace into lines (file_id, linenumber, seek) values (?,?,?)", lines)
        ## insert words into database table
        self._cursor.executemany("insert or replace into words (word) values (?)", words)
        ## insert words and lines relations
        self._cursor.executemany("insert or replace into lines_words (lines_id, words_id) values ((select id from lines where file_id=? and linenumber=?), (select id from words where word=?))", lines_words)
        ## commit database changes for this file
        self._connection.commit()

    def _text(self, fileid, filename, linenumber):
        """Handle plain text files."""
        seek = 0
        ## open file
        filehandle = open(filename, "rb")
        if linenumber > 0:
            ## get last known seek point
            result = self._cursor.execute("select seek from lines where file_id=? and linenumber=?", (fileid, linenumber))
            result = result.fetchone()
            seek = result["seek"]
            filehandle.seek(seek)
            ## this line is already recognized
            ## start with the next new line
            line = filehandle.next()
            ## get seek for starting line
            seek = seek + len(line)
        ## instead of using sets it wpuld be possible to use nested dicts too
        ## like this {word1: {linenumber1: none, linenumber2: none},
        ##            word2: {linenumber1: none, linenumber2: none}
        ## and then use iteritems and itervalues on executemany insert
        ## this should be tested maybe it has a better performance
        ## but for now use unique data sets
        data_lines = sets.Set()
        data_words = sets.Set()
        data_lines_words = sets.Set()
        ## using file iterator is fastest known way to iterate
        ## over the lines of big files which not fit into
        ## memory (faster then readline!?)
        ## internally it uses next and a lookahead buffer
        for line in filehandle:
            ## count linenumbers
            linenumber = linenumber + 1
            ## split line into words
            words = line.split()
            for word in words:
                ## ignore date in word index
                if not word == "":
                    ## unique words
                    data_words.add((word,))
                    ## keep relation of words and lines unique per single line
                    data_lines_words.add((fileid, linenumber, word))
            ## unique lines too
            data_lines.add((fileid, linenumber, seek))
            ## the next read-ahead buffer makes it impossible to use
            ## tell so calculate the len of line manually
            seek = seek + len(line)
            ## insert data into database
            if linenumber % 10000 == 0:
                ## convert sets to lists
                self.__words_lines(list(data_lines), list(data_words), list(data_lines_words))
                ## reset actual data sets
                data_lines.clear()
                data_words.clear()
                data_lines_words.clear()
        ## convert sets to lists
        self.__words_lines(list(data_lines), list(data_words), list(data_lines_words))
        filehandle.close()
        return linenumber

    def _html(self, fileid, filename, linenumber):
        """Handle html files."""
        pass

    def _xml(self, fileid, filename, linenumber):
        """Handle xml files."""
        pass

    def _pdf(self, fileid, filename, linenumber):
        """Handle pdf files."""
        pass

    def _mp3(self, fileid, filename, linenumber):
        """Handle mp3 id3 tags."""
        pass

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """
