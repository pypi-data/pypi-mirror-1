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

latua - latua/_version.py

hold information about latua

"""

__version__ = "$Revision:300 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.2/latua/_version.py $

class _Version(object):
    """Versions information of latua."""
    def __init__(self):
        self.latua_version = "0.2"
        self.year = "2006, 2007"
        self.url = "http://www.petunial.com/latua/"
        self.download_url = "http://www.petunial.com/latua/"
        self.author = "Joerg Zinke, Jonas Weismueller"
        self.email = "team@petunial.com"
        self.copyright = "Copyright (c) %s, %s (%s)" % (self.year,
                                                        self.author,
                                                        self.email)
        self.contributors = []
        self.license = "BSD"
        ## descriptions from website (need to sync manually)
        self.description = """\
latua is a lightweight reusable code library.
        """
        self.long_description = """\
latua library contains modules and wrappers for logging, i18n initialization
and file or system operations.
        """
        self.classifiers = ["Development Status :: 4 - Beta",
                            #"Development Status :: 5 - Production/Stable",
                            "Environment :: Console",
                            "Environment :: Other Environment",
                            "Intended Audience :: Developers",
                            "License :: OSI Approved :: BSD License",
                            "Operating System :: MacOS :: MacOS X",
                            "Operating System :: Microsoft :: Windows",
                            "Operating System :: POSIX",
                            "Programming Language :: Python",
                            "Topic :: Utilities",
                            "Topic :: Software Development :: Libraries :: Python Modules"]

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """
