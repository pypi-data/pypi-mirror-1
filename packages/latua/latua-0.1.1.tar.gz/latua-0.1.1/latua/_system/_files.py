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

latua - latua/_system/_files.py

files class for working on files and directories

"""

__version__ = "$Revision: 176 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1.1/latua/_system/_files.py $

## standard modules
import os
import stat

class _Files(object):
    """Files class for working on files and directories."""
    def __init__(self):
        pass

    def __rwx(self, read_bit, write_bit, execute_bit):
        """Format three permission bits."""
        read = "-"
        write = "-"
        execute = "-"
        if not read_bit == 0:
            read = "r"
        if not write_bit == 0:
            write = "w"
        if not execute_bit == 0:
            execute = "x"
        return "%s%s%s" % (read, write, execute)

    def permission(self, path):
        """Check permissions."""
        stats = os.stat(path)
        mode = stats[stat.ST_MODE]
        ## format permissions
        owner = self.__rwx(mode & stat.S_IRUSR,
                           mode & stat.S_IWUSR,
                           mode & stat.S_IXUSR)
        group = self.__rwx(mode & stat.S_IRGRP,
                           mode & stat.S_IWGRP,
                           mode & stat.S_IXGRP)
        other = self.__rwx(mode & stat.S_IROTH,
                           mode & stat.S_IWOTH,
                           mode & stat.S_IXOTH)
        return (owner, group, other)

    def integrity(self, path, files):
        """Check for integrity of files in a directory."""
        missing_files = []
        for item in files:
            ## check for existence of all files
            if not os.path.isfile(os.path.join(path, item)):
                missing_files.append(item)
        return missing_files

    def search(self, path, type="", extension="", absolute=True):
        """Lists all files or directories with given extension from path."""
        result = []
        if absolute==True:
            ## use absolute path
            path = os.path.abspath(path)
        ## find all files
        for root, directories, files in os.walk(path):
            if type == "file" or type == "":
                for item in files:
                    ## check extension of all files
                    file_extension = os.path.splitext(os.path.join(root, item))[1].lower()
                    if extension == file_extension or extension == "":
                        ## extension matches or no extension given
                        result.append(os.path.join(root, item))
            elif type == "directory" or type == "":
                for item in directories:
                    ## append file
                    result.append(os.path.join(root, item))
            else:
                ## add support for more file types like:
                ##
                ## block device
                ## character device
                ## (symbolic) link
                ## fifo
                ## socket
                ##
                ## actual file type is not supported
                raise ValueError, "unsupported file type: %s" % (type)
        return result

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """
