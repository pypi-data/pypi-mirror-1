#-----------------------------------------------------------------------------
# Copyright (c) 2005  Raymond L. Buvel
#
# This module installs some extras into the RPN calculator.  This module is
# part of rpncalc.
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
# rpncalc; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#-----------------------------------------------------------------------------
import rpncalc, ratfun
from rpncalc import installHelp

#-----------------------------------------------------------------------------
# The _recurse flag is required to prevent recursive calls of the conversion
# routine.  This is necessary because the number conversion routine is called
# to convert components of a polynomial.
_recurse = False

# Convert notation of the form
# "coef,exp;...;coef,exp;coef|coef,exp;...;coef,exp;coef"
# to a rational function or a polynomial.
def convert_ratfun(s):
    global _recurse

    msg = '%s is not a polynomial or rational function' % s
    if _recurse:
        raise ValueError(msg)
    _recurse = True

    # Use a try,finally block to make sure the _recurse flag always gets
    # cleared.
    try:
        parts = s.split('|')
        n = len(parts)
        if n == 1:
            # If there is only one part, the input must be a polynomial or
            # something that causes an exception.
            poly = _convert_poly(parts[0])
            _recurse = False
            return poly

        elif n == 2:
            # Two parts indicates a rational function or an exception occurs
            # while converting the polynomial parts.
            numer = _convert_poly(parts[0])
            denom = _convert_poly(parts[1])
            _recurse = False
            return ratfun.RationalFunction(numer, denom)

        else:
            raise ValueError(msg)
    finally:
        _recurse = False

#-----------------------------------------------------------------------------
def _convert_poly(s):
    msg = '%s is not a polynomial' % s
    # Accumulate (coefficient,exponent) pairs by parsing the input string.
    pairs = []
    for pair in s.split(';'):
        if pair == '':
            continue

        pair = pair.split(',')
        if len(pair) == 2:
            if pair[1] == '':
                exp = 0
            else:
                exp = int(pair[1])
        elif len(pair) == 1:
            exp = 0
        else:
            raise ValueError(msg)

        # Use the number converter so that all data types are allowed for
        # polynomial coefficients.
        coef = rpncalc.number(pair[0])
        if coef is None:
            raise ValueError(msg)

        pairs.append((coef,exp))

    return ratfun.Polynomial(pairs)

#-----------------------------------------------------------------------------
# Define functions that access the methods of a polynomial or rational
# function.  These are installed so that the operations can be used from the
# RPN interpreter.

def _deriv(a):
    return a.deriv

def _eval(a, x):
    return a(x)

# Convert a polynomial or rational function on the stack into the named
# function in the user vocabulary.
def _to_fun():
    name = rpncalc.getName()
    rpncalc.checkStack(1)
    f = rpncalc.mainStack[-1]

    if not isinstance(f, (ratfun.Polynomial, ratfun.RationalFunction)):
        raise rpncalc.RpncalcError('Not a polynomial or rational function')

    rpncalc.userVoc[name] = rpncalc.parms_1_1(f)
    rpncalc.mainStack.pop()

# Generate a polynomial from the list of roots on the stack.
def _from_roots():
    p = ratfun.polyFromRoots(rpncalc.mainStack)
    del rpncalc.mainStack[:]
    rpncalc.mainStack.append(p)

# Note the following only apply to polynomials.
def _integ(p):
    return p.integ

def _deg(p):
    return p.deg

def _coef(p, n):
    return p.coef(n)

def _roots():
    rpncalc.checkStack(1)
    r = rpncalc.mainStack[-1].roots()
    rpncalc.mainStack.pop()
    rpncalc.mainStack.extend(r)


def _unique_roots():
    rpncalc.checkStack(1)
    r = rpncalc.mainStack[-1].uniqueRoots()
    rpncalc.mainStack.pop()
    rpncalc.mainStack.extend(r)


def _improve_roots():
    rpncalc.checkStack(3)
    eps = rpncalc.mainStack[-1]

    p = rpncalc.mainStack[-2]
    if not isinstance(p, ratfun.Polynomial):
        raise rpncalc.RpncalcError('... poly eps improve_roots')

    r = ratfun.improveRoots(rpncalc.mainStack[:-2], p, eps)
    del rpncalc.mainStack[:]
    rpncalc.mainStack.extend(r)

#-----------------------------------------------------------------------------
# Install the converter and the additional operations.

rpncalc.numberConverters.append(convert_ratfun)
rpncalc.systemVoc['deriv'] = rpncalc.parms_1_1(_deriv)
rpncalc.systemVoc['integ'] = rpncalc.parms_1_1(_integ)
rpncalc.systemVoc['eval'] = rpncalc.parms_2_1(_eval)
rpncalc.systemVoc['to_fun'] = _to_fun
rpncalc.systemVoc['from_roots'] = _from_roots
rpncalc.systemVoc['deg'] = rpncalc.parms_1_1(_deg)
rpncalc.systemVoc['coef'] = rpncalc.parms_2_1(_coef)
rpncalc.systemVoc['gcd'] = rpncalc.parms_2_1(ratfun.gcd)
rpncalc.systemVoc['improve_roots'] = _improve_roots
rpncalc.systemVoc['roots'] = _roots
rpncalc.systemVoc['unique_roots'] = _unique_roots

rpncalc.systemVoc['Pn'] = rpncalc.parms_1_1(ratfun.Pn)
rpncalc.systemVoc['Tn'] = rpncalc.parms_1_1(ratfun.Tn)
rpncalc.systemVoc['Un'] = rpncalc.parms_1_1(ratfun.Un)
rpncalc.systemVoc['Hn'] = rpncalc.parms_1_1(ratfun.Hn)
rpncalc.systemVoc['Ln_s'] = rpncalc.parms_2_1(ratfun.Ln_s)
rpncalc.systemVoc['Jn_pq'] = rpncalc.parms_n_m(ratfun.Jn_pq, 3, 1)

del _deriv, _integ, _eval, _deg, _coef, _to_fun, _from_roots, _improve_roots
del _roots

installHelp('deriv', '(f -- g)',
'Return the derivative of the polynomial or rational function f.')
installHelp('integ', '(p -- q)', 'Return the integral of the polynomial p.')
installHelp('eval', '(f x -- y)',
'y = f(x) evaluate the polynomial or rational function f.')
installHelp('to_fun', '(g (f -- )',
'Install the polynomial or rational function f as the calculator function g.')
installHelp('from_roots', '(r1..rn -- p)',
'Return a polynomial p constructed from the n roots listed on the stack.')
installHelp('deg', '(p -- n)', 'Return the degree of the polynomial p.')
installHelp('coef', '(p n -- y)',
'Return the coefficient of x^n in the polynomial p.')
installHelp('gcd', '(a b -- c)',
'Return the greatest common divisor of a and b.')
installHelp('improve_roots', '(r1..rn p tol -- r1..rn)',
'Improve the n roots of the polynomial p using the specified tolerance.')
installHelp('roots', '(p -- r1..rn)', 'Return the n roots of the polynomial p.')
installHelp('unique_roots', '(p -- r1..rn)',
'Return the n unique roots of the polynomial p.')

installHelp('Pn', '(n -- p)', 'Return the nth Legendre polynomial.')
installHelp('Tn', '(n -- p)', 'Return the nth Chebyshev polynomial.')
installHelp('Un', '(n -- p)',
'Return the nth Chebyshev polynomial of the second kind.')
installHelp('Hn', '(n -- p)', 'Return the nth Hermite polynomial.')

#-----------------------------------------------------------------------------
# This section installs commands to save and restore variables and stacks.
#-----------------------------------------------------------------------------

# The user can modify this directory path.  See example in rpn.py.
saveDirectory = '~/.rpncalc'

# Make these symbols available in the global namespace so that eval can
# correctly reconstruct objects of these types from their representation
# strings.
from clnum import mpq, mpf, cmpf, cmpq
from ratfun import Polynomial, RationalFunction

def _getSavePath():
    import os
    fname = rpncalc.getName() + '.pk'
    dname = os.path.expanduser(saveDirectory)
    dname = os.path.expandvars(dname)
    if not os.path.isdir(dname):
        # Try to create the directory if it doesn't exist.
        os.makedirs(dname, 0755)

    name = os.path.join(dname, fname)
    exists = os.path.isfile(name)
    return exists, name

def _saveList(src):
    dst = []
    for value in src:
        if not isinstance(value, (int, long, float, complex)):
            value = repr(value)
        dst.append(value)
    return dst

def _saveDict(src):
    dst = {}
    for key,value in src.iteritems():
        if not isinstance(value, (int, long, float, complex)):
            value = repr(value)
        dst[key] = value
    return dst

def _save(force):
    def save(force=force):
        exists, name = _getSavePath()
        if exists and not force:
            msg = 'File exists, use fsave to force a save\n%s' % name
            raise rpncalc.RpncalcError(msg)

        from cPickle import dump
        pfile = open(name, 'wb')
        dump(_saveList(rpncalc.mainStack), pfile, -1)
        dump(_saveList(rpncalc.alternateStack), pfile, -1)
        dump(_saveDict(rpncalc.getVariables().__dict__), pfile, -1)
        pfile.close()

    return save

def _restoreList(values):
    lst = []
    for value in values:
        if isinstance(value, basestring):
            try:
                value = eval(value)
            except KeyboardInterrupt:
                raise
            except:
                pass
        lst.append(value)
    return lst

def _restoreDict(src):
    dst = {}
    for key,value in src.iteritems():
        if isinstance(value, basestring):
            try:
                value = eval(value)
            except KeyboardInterrupt:
                raise
            except:
                pass
        dst[key] = value
    return dst

def _restore():
    exists, name = _getSavePath()
    if not exists:
        msg = 'Can\'t find "%s"' % name
        raise rpncalc.RpncalcError(msg)

    from cPickle import load
    pfile = open(name, 'rb')
    rpncalc.mainStack[:] = _restoreList(load(pfile))
    rpncalc.alternateStack[:] = _restoreList(load(pfile))
    vars = rpncalc.getVariables()
    vars.__dict__ = _restoreDict(load(pfile))
    rpncalc.setVariables(vars)
    pfile.close()

rpncalc.systemVoc.update({
'save' : _save(False),
'fsave' : _save(True),
'restore' : _restore,
})

installHelp('save', '(name ( -- )',
'Save the stacks and user defined variables in the file specified by name.')
installHelp('fsave', '(name ( -- )',
'Same as the save command but forces the file to be overwritten.')
installHelp('restore', '(name ( -- )',
'''Restore the stacks and user defined variables from a previous save.
The file is specified by name.''')

#-----------------------------------------------------------------------------
