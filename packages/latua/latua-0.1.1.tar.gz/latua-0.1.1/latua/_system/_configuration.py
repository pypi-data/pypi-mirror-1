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

latua - latua/base/_configuration.py

classes for accessing configuration file

"""

__version__ = "$Revision: 132 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1.1/latua/_system/_configuration.py $

## standard modules
import os
import ConfigParser

## latua modules
import latua.error

class _Configuration(ConfigParser.SafeConfigParser):
    """Access configuration file."""
    def __init__(self):
        ConfigParser.SafeConfigParser.__init__(self)

    def __check_dir(self, directory):
        """Check existence of configuration directory."""
        if not os.path.isdir(directory):
            try:
                ## create dir
                os.mkdir(directory)
            except OSError, error:
                ## maybe we are not allowed to create the directory
                raise latua.error.ConfigurationError(directory, "unable to create configuration directory",  error)

    def read_file(self, configuration_file):
        """Read actual configuration file."""
        if os.path.isfile(configuration_file):
            ## configuration file exists
            try:
                self.read(configuration_file)
            except ConfigParser.ParsingError, error:
                ## configuration file exists but is not parseable
                ## there is no way to handle this
                raise latua.error.ConfigurationError(configuration_file, "could not parse configuration file", error)
        else:
            ## configuration file does not exists
            raise latua.error.ConfigurationError(configuration_file, "configuration file does not exist")

    def write_file(self, configuration_file):
        """Write actual configuration to file after checking configuration dir."""
        self.__check_dir(os.path.dirname(configuration_file))
        try:
            ## overwrite existing file
            self.write(open(configuration_file, "w"))
        except IOError, error:
            ## something went wrong maybe not
            ## allowed to create configuration file
            raise latua.error.ConfigurationError(configuration_file, "unable to to write configuration file", error)

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """
