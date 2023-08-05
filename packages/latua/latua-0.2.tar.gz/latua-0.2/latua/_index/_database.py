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

latua - latua/_index/_database.py

latua index database backend class

"""

__version__ = "$Revision: 293 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/latua/_index/_database.py $

## latua modules
import latua._index._connection

class _Database(latua._index._connection._Connection):
    """Index Database backend."""
    def __init__(self, filename, initialize=False):
        latua._index._connection._Connection.__init__(self, filename)
        if initialize == True:
            ## database needs initial reset
            self._reset()

    def _reset(self):
        """Reset and initialize database."""
        sql = """\
--
-- tables
--
DROP TABLE IF EXISTS "files";
DROP TABLE IF EXISTS "lines";
DROP TABLE IF EXISTS "words";
DROP TABLE IF EXISTS "lines_words";

CREATE TABLE IF NOT EXISTS "files" (
    "id" integer NOT NULL PRIMARY KEY,
    "filename" text NOT NULL UNIQUE,
    "filetype" text NOT NULL,
    "filesize" integer NOT NULL,
    "mtime" integer NOT NULL,
    "lastline" integer NOT NULL
);

CREATE TABLE IF NOT EXISTS "lines" (
    "id" integer NOT NULL PRIMARY KEY,
    "file_id" integer NOT NULL REFERENCES "files" ("id"),
    "linenumber" integer NOT NULL,
    "seek" integer NOT NULL
);

CREATE TABLE IF NOT EXISTS "words" (
    "id" integer NOT NULL PRIMARY KEY,
    "word" text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS "lines_words" (
    "lines_id" integer NOT NULL,
    "words_id" integer NOT NULL,
    FOREIGN KEY (lines_id) REFERENCES "lines" ("id"),
    FOREIGN KEY (words_id) REFERENCES "words" ("id"),
    UNIQUE ("words_id", "lines_id")
);

--
-- indexes
--
DROP INDEX IF EXISTS "index_files_filename";
DROP INDEX IF EXISTS "index_lines_file_id";
DROP INDEX IF EXISTS "index_lines_linenumber";
DROP INDEX IF EXISTS "index_words_word";
DROP INDEX IF EXISTS "indes_lines_words_lines_id";
DROP INDEX IF EXISTS "indes_lines_words_words_id";

CREATE UNIQUE INDEX IF NOT EXISTS index_files_filename ON "files" ("filename");
CREATE INDEX IF NOT EXISTS index_lines_file_id ON "lines" ("file_id");
CREATE INDEX IF NOT EXISTS index_lines_linenumber ON "lines" ("linenumber");
CREATE UNIQUE INDEX IF NOT EXISTS index_words_word ON "words" ("word");
CREATE UNIQUE INDEX IF NOT EXISTS index_lines_words_lines_id_words_id ON "lines_words" ("lines_id", "words_id");

--
-- analyze indexes
--
ANALYZE;

--
-- triggers
--
DROP TRIGGER IF EXISTS "trigger_delete_files";
DROP TRIGGER IF EXISTS "trigger_delete_lines";
DROP TRIGGER IF EXISTS "trigger_delete_words";
DROP TRIGGER IF EXISTS "trigger_delete_lines_words";

CREATE TRIGGER IF NOT EXISTS trigger_delete_files AFTER DELETE ON files
    BEGIN
        DELETE FROM lines WHERE lines.file_id=old.id;
    END;

CREATE TRIGGER IF NOT EXISTS trigger_delete_lines AFTER DELETE ON lines
    BEGIN
        DELETE FROM lines_words WHERE lines_words.lines_id=old.id;
    END;

CREATE TRIGGER IF NOT EXISTS trigger_delete_words AFTER DELETE ON words
    BEGIN
        DELETE FROM lines_words WHERE lines_words.words_id=old.id;
    END;

CREATE TRIGGER IF NOT EXISTS trigger_delete_lines_words AFTER DELETE on lines_words
    BEGIN
        DELETE FROM words WHERE id=old.words_id and id NOT IN
            (SELECT words_id FROM lines_words WHERE words_id=old.words_id);
    END;

--
-- views
--
DROP VIEW IF EXISTS "view_files";

CREATE VIEW IF NOT EXISTS view_files AS
    SELECT id, filename, filetype, filesize, mtime, lastline
        FROM files
        ORDER BY filename;

"""
        self._cursor.executescript(sql)
        ## commit database changes
        self._connection.commit()
        self.maintenance()

    def maintenance(self):
        """Database maintenance."""
        sql = """\
--
-- tables
--
VACUUM "files";
VACUUM "lines";
VACUUM "words";
VACUUM "lines_words";

--
-- indexes
--
VACUUM "index_files_filename";
VACUUM "index_lines_file_id";
VACUUM "index_lines_linenumber";
VACUUM "index_words_word";
VACUUM "indes_lines_words_lines_id";
VACUUM "indes_lines_words_words_id";

--
-- analyze indexes
--
ANALYZE;

"""
        self._cursor.executescript(sql)
        ## commit database changes
        self._connection.commit()

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """
