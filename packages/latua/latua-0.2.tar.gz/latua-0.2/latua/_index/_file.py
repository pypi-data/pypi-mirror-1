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

latua - latua/_index/_file.py

latua index file class

"""

__version__ = "$Revision: 323 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/latua/_index/_file.py $

## standard modules
import os
import stat
import string

## latua modules
import latua
import latua.error
import latua._context
import latua._index._connection
import latua._index._handler

class _File(latua._index._connection._Connection):
    """Indexing lines and words from given files."""
    def __init__(self, filename):
        latua._index._connection._Connection.__init__(self, filename)
        self.__handler = latua._index._handler._Handler(filename)

    def meta(self, filename):
        """Meta data for given filename."""
        meta = {}
        filename = os.path.realpath(filename)
        if os.path.isfile(filename):
            ## get meta data
            result = self._cursor.execute("select filename, filetype, filesize, mtime, lastline from view_files where filename=?", (filename,))
            result = result.fetchone()
            if not result == None:
                ## convert result to dict
                meta["filename"]   = result["filename"]
                meta["filetype"]   = result["filetype"]
                meta["filesize"]   = result["filesize"]
                meta["mtime"]      = result["mtime"]
                meta["lastline"]   = result["lastline"]
            else:
                raise latua.error.FileError(filename, "could not get meta data for file from index", "file is not in index")
        else:
            raise latua.error.FileError(filename, "could not get meta data for file from index", "file does not exist")
        return meta

    def rename(self, old_filename, new_filename):
        """Rename a given filename in index."""
        old_filename = os.path.realpath(old_filename)
        new_filename = os.path.realpath(new_filename)
        if os.path.isfile(new_filename):
            ## new file exists
            self._cursor.execute("update files set filename=? where filename=?", (new_filename, old_filename))
            ## commit database changes for this file
            self._connection.commit()
        else:
            raise latua.error.FileError(new_filename, "could not rename to file", "file does not exist")

    def remove(self, filename):
        """Remove a given filename from index."""
        filename = os.path.realpath(filename)
        result = self._cursor.execute("select id from view_files where filename=?", (filename,))
        result = result.fetchone()
        if not result == None:
            ## there is something to delete
            self._cursor.execute("delete from files where id=?", (result["id"],))
            ## commit database changes for this file
            self._connection.commit()
        else:
            raise latua.error.FileError(filename, "could not remove file from index", "file is not in index")

    def update(self, filename):
        """Update file with given filename in index."""
        filename = os.path.realpath(filename)
        if os.path.isfile(filename):
            ## get stats from file
            mtime = os.stat(filename)[stat.ST_MTIME]
            filesize = os.stat(filename)[stat.ST_SIZE]
            ## get meta data
            result = self._cursor.execute("select id, filetype, filesize, mtime, lastline from view_files where filename=?", (filename,))
            result = result.fetchone()
            if not result == None:
                ## worst case not recognized by update: a replaced
                ## single letter/word in the file within one second
                ## results in an unchanged mtime and filesize
                if result["mtime"] < mtime or not result["filesize"] == filesize:
                    ## append new lines to index
                    handler_function = getattr(self.__handler, "_%s" % (result["filetype"]))
                    lastline = handler_function(result["id"], filename, result["lastline"])
                    ## update meta data for filename
                    self._cursor.execute("update files set mtime=?, filesize=?, lastline=? where id=?", (mtime, filesize, lastline, result["id"]))
                    ## commit database changes for this file
                    self._connection.commit()
            else:
                raise latua.error.FileError(filename, "could not update file in index", "file is not in index")
        else:
            raise latua.error.FileError(filename, "could not update file in index", "file does not exist")

    def add(self, filename, filetype="text"):
        """Add file with given filename to index."""
        filename = os.path.realpath(filename)
        if os.path.isfile(filename):
            ## get stats from file
            mtime = os.stat(filename)[stat.ST_MTIME]
            filesize = os.stat(filename)[stat.ST_SIZE]
            if filetype in self.__handler.filetypes:
                ## get meta data
                result = self._cursor.execute("select id from view_files where filename=?", (filename,))
                result = result.fetchone()
                if result == None:
                    ## add meta data for filename
                    self._cursor.execute("insert into files (filename, filetype, filesize, mtime, lastline) values (?,?,?,?,?)", (filename, filetype, filesize, mtime, 0))
                    result = self._cursor.execute("select id from view_files where filename=?", (filename,))
                    result = result.fetchone()
                    ## add file to index
                    handler_function = getattr(self.__handler, "_%s" % (filetype))
                    lastline = handler_function(result["id"], filename, 0)
                    ## update meta data for filename
                    self._cursor.execute("update files set lastline=? where id=?", (lastline, result["id"]))
                    ## commit database changes for this file
                    self._connection.commit()
                else:
                    raise latua.error.FileError(filename, "could not add file to index", "file is already in index")
            else:
                raise latua.error.FileError(filename, "could not add file to index", "filetype is not supported")
        else:
            raise latua.error.FileError(filename, "could not add file to index", "file does not exist")

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """
