#-----------------------------------------------------------------------------
# Copyright (c) 2005  Raymond L. Buvel
#
# This script is a starting point for using the RPN calculator.
#
# The rpncalc module is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option) any
# later version.
#
# The rpncalc nodule is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# rpncalc; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA  02111-1307  USA
#-----------------------------------------------------------------------------

# Import some convenience functions that can be used from the Python
# interactive prompt.
from rpncalc import rpn, pop, get, push, prog, alias, function, stats
from rpncalc import getVariables as getv, setVariables as setv
import rpncalc
from rpncalc.ratfun import Polynomial as poly, RationalFunction as rat
from clnum import *
from rpncalc.chebyshev import Chebyshev as cheby

from pprint import pprint as pp

# Install the extra module which brings in polynomials and rational functions.
import rpncalc.extra

# If you need to change the save/restore directory, do that here.
rpncalc.extra.saveDirectory = '~/.rpncalc'

# Install the constant module.
import rpncalc.const

# Get the number converter so that it can be used from the Python interpreter.
# This makes it possible to use the polynomial and rational function notation
# instead of calling the constructors directly.
num = rpncalc.number

# Uncomment the following line if you want the trig functions to default to the
# degrees mode instead of radians.
#rpncalc.systemVoc['use_degrees']()

# Alias some commands
alias('factorial', '!', rpncalc.systemVoc)
alias('doublefactorial', '!!', rpncalc.systemVoc)
alias('lnfactorial', 'ln!', rpncalc.systemVoc)

# Run the RPN interpreter.
rpn()

