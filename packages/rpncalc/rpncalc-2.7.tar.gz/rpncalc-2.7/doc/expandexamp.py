#-----------------------------------------------------------------------------
# This script processes the embedded examples in the user manual.  Processing
# these automatically guarantees that they actually work and makes it is easier
# to add additional examples.
#
# Copyright (c) 2004  Raymond L. Buvel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#-----------------------------------------------------------------------------

from cStringIO import StringIO
import sys

from rpncalc import rpncalc, pop, get, push, prog, function
from rpncalc import getVariables as getv, setVariables as setv
from rpncalc.ratfun import Polynomial as poly, RationalFunction as rat

from clnum import *

import rpncalc.extra

# Perform the module import after the other imports to make sure the module is
# available in the main namespace instead of the package.
from rpncalc import rpncalc


# Disable the following commands so they can be used in the examples without
# causing problems.
def rpn(): pass

def _py(): pass
rpncalc.systemVoc['py'] = _py

# Escape HTML metacharacters
def escape(s):
    s = s.replace('&', '&amp;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    return s

# Transform escaped characters back to their original form.
def unescape(s):
    s = s.replace('&amp;', '&')
    s = s.replace('&lt;', '<')
    s = s.replace('&gt;', '>')
    return s

class Expand:
    def __getitem__(self, inp):
        strout = StringIO()
        sys.stdout = strout
        inp = unescape(inp)

        clear = True
        if inp.endswith('noclear'):
            inp = inp[:-7].rstrip()
            clear = False

        try:
            for line in inp.split('\n'):
                if line.startswith('p:'):
                    line = line[2:]
                    strout.write('>>> %s\n' % line)
                    exec line
                elif line.startswith('h:'):
                    # Perform a hidden operation
                    line = line[2:]
                    rpncalc.evalRpnString(line)
                elif line.startswith('hp:'):
                    # Perform a hidden Python operation
                    line = line[3:]
                    exec line
                else:
                    strout.write('rp> %s\n' % line)
                    rpncalc.evalRpnString(line)
        finally:
            sys.stdout = sys.__stdout__

        if clear:
            del rpncalc.mainStack[:]

        s = escape(strout.getvalue())
        strout.close()
        return s


fname = sys.argv[1]
inFile = open(fname)
outFile = open('_'+fname, 'w')

instr = inFile.read()
inFile.close()

outFile.write(instr % Expand())
outFile.close()

