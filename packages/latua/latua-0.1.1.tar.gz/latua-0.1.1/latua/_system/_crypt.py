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

latua - latua/_system/_crypt.py

latua crypt classes

"""

__version__ = "$Revision: 137 $"
# $URL: http://www.petunial.de/svn/latua/tags/0.1.1/latua/_system/_crypt.py $

## standard modules
import os
import md5
import sha
import string

class _Crypt(object):
    """Crypt texts with md5 or sha1."""
    def __init__(self):
        ## signs between salt and hash
        self.__cutter = "#*$*#"
        ## supported crypt algorithm
        self._supported = ["md5", "sha1"]

    def generate(self, length=8, characters=None):
        """Generates a random text with given length from given chars."""
        if characters == None:
            characters = "%s%s" % (string.letters, string.digits)
        text = []
        ## urandom is unpredictable enough and
        ## more secure then random.random()
        data = os.urandom(length)
        for item in range(len(data)):
            ## append every letter
            text.append(characters[ord(data[item]) % len(characters)])
        return "".join(text)

    def encrypt(self, text, algorithm="md5"):
        """Encrypt a given text."""
        crypted_text = None
        if algorithm not in self._supported:
            ## actual algorithm is not suppoerted
            raise ValueError, "unsupported crypt alogrithm: %s" % (algorithm)
        if algorithm == "sha1":
            ## use sha-1
            salt = sha.new(str(os.urandom(32))).hexdigest()[:5]
            hash_value = sha.new("%s%s" % (salt, text)).hexdigest()
            crypted_text = "%s%s%s%s%s" % (algorithm, self.__cutter, salt, self.__cutter, hash_value)
        else:
            ## use md5
            salt = md5.new(str(os.urandom(32))).hexdigest()[:5]
            hash_value = md5.new("%s%s" % (salt, text)).hexdigest()
            crypted_text = "%s%s%s%s%s" % (algorithm, self.__cutter, salt, self.__cutter, hash_value)
        return crypted_text

    def check(self, text, crypted_text):
        """Check a text against encrypted."""
        result = False
        algorithm, salt, hash_value = crypted_text.split(self.__cutter)
        if algorithm == "sha1":
            ## use sha-1
            if hash_value == sha.new("%s%s" % (salt, text)).hexdigest():
                result = True
        else:
            ## use md5
            if hash_value == md5.new("%s%s" % (salt, text)).hexdigest():
                result = True
        return result

if __name__ == "__main__":
    print """
do not run this file directly, use latua classes

    """
