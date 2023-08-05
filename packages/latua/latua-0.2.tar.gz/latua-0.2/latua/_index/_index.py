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

latua - latua/_index/_index.py

latua index class

sqlite database structure:

    files table:
        - contains files and their meta data recognized in index

        "id" "filename" "filetype" "filesize" "mtime" "lastline"

    lines tables:
        - contains linenumbers and seek points for every line of a file

        "id" "file_id" "linenumber" "seek"

    lines_words table:
        - helper table which contains relationship between words and lines

        "id" "lines_id" "words_id"

    words table:
        - contains all words recognized by index

        "id" "word"

"""

__version__ = "$Revision: 293 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/latua/_index/_index.py $

## standard modules
import os

## latua modules
import latua._index._file
import latua._index._search
import latua._index._database

class _Index(object):
    """Latua index class."""
    def __init__(self, filename="index.db"):
        initialize = False
        if not os.path.isfile(filename):
            initialize = True
        ## index backend object
        self.database = latua._index._database._Database(filename, initialize)
        ## index file object
        self.file = latua._index._file._File(filename)
        ## index search object
        self.search = latua._index._search._Search(filename)

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """
