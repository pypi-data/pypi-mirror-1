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

latua - latua/_base/_platform.py

platform specific variables

the platform class sets all platform specific variables
for the actual correct platform

no need to check the platform again and again in other classes

"""

__version__ = "$Revision: 316 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/latua/_base/_platform.py $

## standard modules
import os
import sys
import stat
import user
import locale
import logging
import logging.handlers

## latua modules
import latua._context
import latua.error

## windows specific modules
if sys.platform == "win32":
    ## these modules are usually
    ## installed by windows users
    try:
        import win32file
        import win32com
        import win32api
    except ImportError, error:
        raise latua.error.PlatformError("windows",
                                        "unable to import windows extensions",
                                        error)

class _Platform(object):
    """Get operating system and associating variables."""
    def __init__(self):
        ## set platform dictionary to context
        self.__platform = latua._context._platform
        if len(self.__platform) == 0:
            ## initialize platform dictionary
            self.__default()
            if sys.platform == "win32":
                ## windows
                self.__windows()
            if sys.platform == "darwin":
                ## mac os x
                self.__darwin()
        ## restore all already initialized variables from
        ## platform dictionary which points to the actual context
        ## the update of the class dictionary appends
        ## all variables as attributes to the object
        self.__dict__.update(self.__platform)

    def __default(self):
        """Initialize default platform settings."""
        ## assume application is started via script
        ## and get name of the script from arguments
        path = os.path.realpath(sys.argv[0])
        if len(sys.argv[0]) == 0:
            ## this should only happen if running via python commandline
            ## interpreter
            path = os.path.realpath("python")
        ## application name
        self.__platform["application_name"] = os.path.basename(path)
        ## application directory
        self.__platform["application_directory"] = os.path.dirname(path)
        ## modules directory
        ## assume this platform module __file__
        ## is installed into the same modules path
        self.__platform["modules_directory"] = os.path.join(os.path.dirname(__file__), os.path.pardir)
        ## users home directory
        self.__platform["home_directory"] = user.home
        ## where to install configuration files
        self.__platform["configuration_directory"] = os.path.join(self.__platform["home_directory"], ".%s" % (self.__platform["application_name"]))
        ## admin user
        self.__platform["admin"] = "root"
        ## username
        self.__platform["user"] = os.getenv("USER")
        if os.name == "posix" and os.getuid() == 0:
            ## after su the user in environment is
            ## set to username instead of root
            ## check against uid
            self.__platform["user"] = self.__platform["admin"]
        if self.__platform["user"] == "root":
            ## use systems configuration directory
            self.__platform["configuration_directory"] = os.path.expanduser(os.path.join(os.path.sep, "etc", self.__platform["application_name"]))
        ## directory for data files
        self.__platform["data_directory"] = os.path.join(sys.prefix, "share", self.__platform["application_name"])
        ## all languages
        self.__platform["languages"] = locale.locale_alias.keys()
        ## locales directory
        self.__platform["locales_directory"] = os.path.join(sys.prefix, "share", "locale")
        if os.path.isdir(os.path.join(self.__platform["application_directory"], "locale")):
            ## application was started from local directory without installation
            self.__platform["locales_directory"] = os.path.join(self.__platform["application_directory"], "locale")
            self.__platform["data_directory"] = self.__platform["application_directory"]
        ## logging handler
        socket = os.path.join(os.path.sep, "dev", "log")
        ## path to socket should exist (not a file)
        if os.path.exists(socket) and stat.S_ISSOCK(os.stat(socket)[stat.ST_MODE]):
            ## unix domain socket
            self.__platform["logging_handler"] = logging.handlers.SysLogHandler(socket)
        else:
            ## try to use default localhost port 514
            self.__platform["logging_handler"] = logging.handlers.SysLogHandler()
        ## logging directory
        self.__platform["logging_directory"] = self.__platform["configuration_directory"]
        if self.__platform["user"] == "root":
            self.__platform["logging_directory"] = os.path.join(os.path.sep, "var", "log")
        ## default logging level
        self.__platform["logging_level"] = logging.INFO
        ## how to start commands with files
        self.__platform["command_file"] = "%s %s"
        ## hidden files
        self.__platform["hidden"] = self.__default_hidden

    def __default_hidden(self, path):
        """Check path for hidden files or directories."""
        path = os.path.realpath(path)
        if os.path.exists(path):
            result = False
            for item in path.split(os.path.sep):
                if len(item) > 0 and item[0] == ".":
                    ## at least one component of path is hidden
                    result = True
            return result
        else:
            raise latua.error.PlatformError("hidden",
                                            "%s does not exist" % (path))

    def __darwin(self):
        """Initialize darwin platform specific settings."""
        ## syslog handler
        self.__platform["logging_handler"] = logging.handlers.SysLogHandler(os.path.join(os.path.sep, "var", "run","syslog"))
        ## mac os x tiger need at least log level warning by default
        self.__platform["logging_level"] = logging.WARNING

    def __windows(self):
        """Initialize windows platform specific settings."""
        id = win32com.shell.shell.SHGetSpecialFolderLocation(0, win32com.shell.shellcon.CSIDL_APPDATA)
        appdata = win32com.shell.shell.SHGetPathFromIDList(id)
        ## get application data folder on windows
        ## environ appdata is not available on unix
        path = os.getenv("APPDATA", appdata)
        ## admin user
        self.__platform["admin"] = "Administrator"
        ## username
        self.__platform["user"] = os.environ["USERNAME"]
        ## application directory
        self.__platform["application_directory"] = path
        ## where to install configuration files
        self.__platform["configuration_directory"] = os.path.join(self.__platform["self.application_directory"], self.__platform["application_name"])
        ## directory for data files
        self.__platform["data_directory"] = self.__platform["configuration_directory"]
        ## all languages
        self.__platform["languages"] = locale.windows_locale.values()
        ## locales directory
        self.__platform["locales_directory"] = os.path.join(self.__platform["self.data_directory"], "locale")
        ## syslog handler
        ## depends on win32 extensions too
        self.__platform["logging_handler"] = logging.handlers.NTEventLogHandler(self.__platform["application_name"], logtype="Application")
        ## default log directory
        self.__platform["logging_directory"] = self.configuration_directory
        ## how to start commands with files
        self.command_file = "%s \"%s\""
        ## hidden files
        self.__platform["hidden"] = self.__windows_hidden

    def __windows_hidden(self, path):
        """Check path for hidden files or directories on windows."""
        path = os.path.realpath(path)
        if os.path.exists(path):
            result = False
            for item in path.split(os.path.sep):
                if len(item) > 0 and win32api.FILE_ATTRIBUTE_HIDDEN in win32file.GetFileAttributes(item):
                    ## at least one component of path is hidden
                    result = True
            return result
        else:
            raise latua.error.PlatformError("hidden",
                                            "%s does not exists" % (path))

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """
