# GPGSigVerifier -*- mode: python; coding: utf-8 -*-
# vim:ts=4:sw=4:et:

# A class for verifying signed files

# Copyright (c) 2002 Colin Walters <walters@gnu.org>

# This file is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# Copyright (c) 2005,2006 Alexandr D. Kanevskiy <packages@bifh.org>
#               Rewrite to use python library calls instead of fork/exec

import os, string, commands

class GPGSigVerifierException(Exception):
    def __init__(self, value):
        self._value = value
    def __str__(self):
        return `self._value`

class GPGSigVerificationFailure(Exception):
    def __init__(self, value, output):
        self._value = value
        self._output = output
    def __str__(self):
        return `self._value`

    def getOutput(self):
        return self._output

class GPGSigVerifier:
    def __init__(self, keyrings, gpgv=None):
        self._keyrings = keyrings
        if gpgv is None:
            gpgv = '/usr/bin/gpgv'
        if not os.access(gpgv, os.X_OK):
            raise GPGSigVerifierException("Couldn't execute \"%s\"" % (gpgv,))
        self._gpgv = gpgv

    def verify(self, filename, sigfilename=None):

        args = []
        for keyring in self._keyrings:
            args.append('--keyring')
            args.append(keyring)
        if sigfilename:
            args.append(sigfilename)
        args = [self._gpgv] + args + [filename]

        (status, output) = commands.getstatusoutput(string.join(args))
        if not (status is None or (os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0)):
            if os.WIFEXITED(status):
                msg = "gpgv exited with error code %d" % (os.WEXITSTATUS(status),)
            elif os.WIFSTOPPED(status):
                msg = "gpgv stopped unexpectedly with signal %d" % (os.WSTOPSIG(status),)
            elif os.WIFSIGNALED(status):
                msg = "gpgv died with signal %d" % (os.WTERMSIG(status),)
            raise GPGSigVerificationFailure(msg, output)
        return output.splitlines()
 
