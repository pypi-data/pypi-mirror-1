#-----------------------------------------------------------------------------
# Copyright (c) 2006  Raymond L. Buvel
#
# Unit test for the ratfun module.
#
# The ratfun module is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option) any
# later version.
#
# The ratfun nodule is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# ratfun; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA  02111-1307  USA
#-----------------------------------------------------------------------------
import sys

# Structure the imports so they work for both a stand-alone module or
# packaged with rpncalc.

try:
    import ratfun
except ImportError:
    from rpncalc import ratfun

import clnum
from clnum import mpq, mpf, cmpq, cos

poly = ratfun.Polynomial
rat = ratfun.RationalFunction

#*****************************************************************************
#                       Polynomial Section
#*****************************************************************************
#-----------------------------------------------------------------------------
# Verify that the zero polynomial is always returned for several variants of
# the input.

assert poly() is poly._zero
assert poly([]) is poly._zero
assert poly(0) is poly._zero
assert poly(0j) is poly._zero
assert poly(0,0) is poly._zero
assert poly([0]*10) is poly._zero
assert poly((0,100),(0,5)) is poly._zero

#-----------------------------------------------------------------------------
# Verify that a polynomial passed in is returned.

p = poly(1,2,3)
assert poly(p) is p
del p

#-----------------------------------------------------------------------------
# Check various forms of the constant polynomial.

assert poly(1)._coef == (1,)
assert poly([1])._coef == (1,)
assert poly(1,0,0)._coef == (1,)
assert poly([1,0,0])._coef == (1,)
assert poly((1,0),(0,100))._coef == (1,)
assert poly(1.1)._coef == (1.1,)
assert poly(1+1j)._coef == (1+1j,)
try:
    # Invalid constants should fail the conversion to complex.
    poly(None)
except TypeError, msg:
    pass
assert str(msg) == 'complex() argument must be a string or a number'

#-----------------------------------------------------------------------------
# Verify that strings fail.

try:
    poly('1.0')
except ValueError, msg:
    pass
assert str(msg) == 'Cannot create a polynomial from a string'
try:
    poly(1,'1.0')
except ValueError, msg:
    pass
assert str(msg) == 'Cannot create coefficients from a string'
try:
    poly([(1,0),('1.0',2)])
except ValueError, msg:
    pass
assert str(msg) == 'Cannot create coefficients from a string'

#-----------------------------------------------------------------------------
# Check various forms of sequences.
assert poly(1,2,3)._coef == (1,2,3)
assert poly([1,2,3])._coef == (1,2,3)
assert poly(xrange(4))._coef == (0,1,2,3)

#-----------------------------------------------------------------------------
# Check mal-formed sequences.
try:
    # Invalid coefficients should fail the conversion to complex.
    poly([1,2,3,None])
except TypeError, msg:
    pass
assert str(msg) == 'complex() argument must be a string or a number'
try:
    poly([1],[2,3])
except ValueError, msg:
    pass
assert str(msg) == 'Invalid coefficient sequence'
try:
    poly(1,[2,3])
except TypeError, msg:
    pass
assert str(msg) == 'complex() argument must be a string or a number'

#-----------------------------------------------------------------------------
# Check various forms of pairs.

assert poly((1,2),(1,0))._coef == (1,0,1)
assert poly([(1,4)])._coef == (0,0,0,0,1)
assert tuple(poly((2,100),(1,0)).coefAsPairs()) == ((1,0),(2,100))

#-----------------------------------------------------------------------------
# Check the compare function by sorting a list of polynomials.

p0 = poly()
p1 = poly(1)
p2 = poly(2)
p3 = poly(2+1j)
p4 = poly([(1,1)])
p5 = poly([(1,100)])
lst = [p5,p3,p1,p4,p2,p0]
lst.sort()
assert lst == [p0,p1,p2,p3,p4,p5]
del lst,p0,p1,p2,p3,p4,p5

#-----------------------------------------------------------------------------
# Check __nonzero__

assert bool(poly()) is False
assert bool(poly(1)) is True
assert bool(poly([(1,100)])) is True

#-----------------------------------------------------------------------------
# Check __pos__

p = poly([(1,100)])
assert (+p) is p
del p

#-----------------------------------------------------------------------------
# Check __neg__

assert tuple(( -poly((2,100),(1,0)) ).coefAsPairs()) == ((-1,0),(-2,100))


#-----------------------------------------------------------------------------
# Define some polynomials for arithmetic tests.

p0 = poly(0)
p1 = poly(1)
p2 = poly([(1,1)])
p3 = poly([(2,2)])
p4 = poly([(3,100)])

#-----------------------------------------------------------------------------
# Check addition and subtraction.

assert 1+p0 == poly(1)
assert 1-p0 == poly(1)
assert p0+1 == poly(1)
assert p0-1 == poly(-1)
assert 1+p4 == poly((3,100),(1,0))
assert 1-p4 == poly((-3,100),(1,0))
assert p4-1 == poly((3,100),(-1,0))
assert p1+p2+p3+p4 == poly((3,100),(2,2),(1,1),(1,0))
assert p1-p2+p3-p4 == poly((-3,100),(2,2),(-1,1),(1,0))

#-----------------------------------------------------------------------------
# Check multiplication

p = p2+1
assert (0*p4) == poly()
assert (p4*0) == poly()
assert (1*p0) == poly()
assert (p0*2) == poly()
assert (p2*10) == poly([(10,1)])
assert (p2*p3) == poly([(2,3)])
assert (p4*p3) == poly([(6,102)])
assert (p4*p3) == poly([(6,102)])
assert (p*p)     == poly(1,2,1)
assert (p*p*p)   == poly(1,3,3,1)
assert (p*p*p*p) == poly(1,4,6,4,1)

del p

#-----------------------------------------------------------------------------
# Check powers

assert p0**100 == poly()
assert p0**0 == poly(1)
assert p4**0 == poly(1)
assert p2**50 == poly([(1,50)])
assert p3**10 == poly([(2**10,20)])
assert poly(1,-1)**5 == poly(1,-5,10,-10,5,-1)

checkExcept = False
try:
    p2**0.5
except TypeError:
    checkExcept = True
assert checkExcept

checkExcept = False
try:
    p2**-1
except TypeError:
    checkExcept = True
assert checkExcept

del p0,p1,p2,p3,p4

#-----------------------------------------------------------------------------
# Check division.  Since the division operators all use divmod, most of the
# test cases are applied to divmod with a number of mixed type cases included.

checkExcept = False
try:
    divmod(1, poly())
except ZeroDivisionError:
    checkExcept = True
assert checkExcept

assert divmod(poly(), 100) == (0,0)
assert divmod(poly(1), 3) == (mpq(1,3), 0)
assert divmod(poly(1,2), 3) == (poly(mpq(1,3),mpq(2,3)), 0)
assert divmod(poly(1,5,10,10,5,1), poly(1,1)) == (poly(1,4,6,4,1), 0)
assert divmod(poly(1,5,10,10,5,1)+1, poly(1,1)) == (poly(1,4,6,4,1), 1)
assert divmod(poly([(1,6)]), poly(1,2,1)) == (poly(5,-4,3,-2,1), poly(-5,-6))

assert poly()/3 == 0
assert poly(1)/3 == poly(mpq(1,3))
assert 2/poly(3) == poly(mpq(2,3))
assert poly(1,2,3,4)/7 == poly(mpq(1,7),mpq(2,7),mpq(3,7),mpq(4,7))

assert poly(1)%3 == 0
assert 2%poly(3) == 0
assert poly([(1,5)])%poly(1,1) == -1

#-----------------------------------------------------------------------------
# Check polynomial evaluation and the sampling method.

p = poly(1,2,1)
assert p(-1) == 0
assert p(0) == 1
assert p(1) == 4
assert p(1.5) == 6.25

assert [(x*(x+2)+1) - y for x,y in p.sample(-2,2,100)] == [0]*100

# If numpy is installed, try evaluating the polynomial using an array.
try:
    import numpy
    x = numpy.array([-1,0,1,1.5])
    y = numpy.array([0,1,4,6.25])
    assert (p(x) == y).all()
except ImportError:
    print 'Compatibility with numpy skipped.'

del x,y,p

#-----------------------------------------------------------------------------
# Check the derivative and integral methods.

assert poly().deriv == poly()
assert poly(1).deriv == poly()
assert poly(10).deriv == poly()
assert poly(1,2,1).deriv == poly(2,2)
assert poly([(1,1)]).deriv == poly(1)
assert poly([(2,2)]).deriv == poly(0,4)
assert poly([(1,100)]).deriv == poly([(100,99)])

assert poly().integ == poly()
assert poly(1).integ == poly(0,1)
assert poly(10).integ == poly(0,10)
assert poly(1,2,1).integ == poly(0,1,1,mpq(1,3))
assert poly([(1,1)]).integ == poly(0,0,mpq(1,2))
assert poly([(2,2)]).integ == poly([(mpq(2,3),3)])
assert poly([(1.0,100)]).integ == poly([(mpf(1.0)/101,101)])

#-----------------------------------------------------------------------------
# Check the root finder.

p = ratfun.polyFromRoots(range(1,21))
assert p.deg == 20
assert p(1) == 0
assert p(20) == 0
r = p.roots()
assert max([abs(a+1-b) for a,b in enumerate(r)]) == 0

p = poly(1,-2,1)
r = p.roots()
assert r[0] == 1 and r[1] == 1

p = poly(1,0,1)
r = (p**10).roots(start=1j)
assert max([abs(a-b) for a,b in zip([-1j]*10 + [1j]*10,r)]) == 0

n = 20
p = ratfun.Tn(n)
r = p.uniqueRoots(start=-1,eps=1e-20)
r.sort()
pi = clnum.pi()
tr = [cos(pi*(k-mpq(1,2))/n) for k in xrange(1,n+1)]
tr.sort()
d = [abs(a-b) for a,b in zip(tr,r)]
assert max(d) < 1e-28

a = poly(1,0,1)
b = poly(mpq(-1,3),1)
c = poly(-1,1)
p = a**10 * b**7 * c**5
assert p.deg == 32
r = p.uniqueRoots()
tr = [cmpq(0,-1), cmpq(0,1), mpq(1,3), 1]
d = [abs(a-b) for a,b in zip(tr,r)]
assert max(d) < 1e-180

#*****************************************************************************
#                       Rational Function Section
#*****************************************************************************
#-----------------------------------------------------------------------------
# Most of the input of rational functions is handled by the polynomial
# constructor.  Just check the variations in the rational function constructor.

assert rat(0) == 0
assert rat(1) == 1

r = rat(1)
assert rat(r) is r

r = rat(1,2)
assert r.numer == mpq(1,2)
assert r.denom == 1
del r

checkExcept = False
try:
    rat(1,0)
except ZeroDivisionError:
    checkExcept = True
assert checkExcept

# Make sure common factors are removed.
assert rat((1,2,1),(1,1)) == poly(1,1)
assert rat((1,2,1),(-1,0,1)).numer == poly(1,1)
assert rat((1,2,1),(-1,0,1)).denom == poly(-1,1)

# Make sure the result is normalized so that the denominator is monic.
assert rat((1,2,1),(1,2,3)).numer == poly(mpq(1,3),mpq(2,3),mpq(1,3))
assert rat((1,2,1),(1,2,3)).denom == poly(mpq(1,3),mpq(2,3),1)

#-----------------------------------------------------------------------------
# Check __neg__

assert ( -rat((1,2,1),(-1,0,1)) ).numer == poly(-1,-1)
assert ( -rat((1,2,1),(-1,0,1)) ).denom == poly(-1,1)

assert ( -rat((-1,-2,-1),(-1,0,1)) ).numer == poly(1,1)
assert ( -rat((-1,-2,-1),(-1,0,1)) ).denom == poly(-1,1)

#-----------------------------------------------------------------------------
# Check addition and subtraction.

assert 1+rat(0) == 1
assert rat(0)-1 == -1
assert rat(1)-mpq(1,2) == rat(1,2)
assert rat((1,1),1) + rat((-1,1),(1,1)) == rat((0,3,1),(1,1))
assert poly(1,1) + rat((-1,1),(1,1)) == rat((0,3,1),(1,1))
assert rat((-1,1),(1,1)) + poly(1,1) == rat((0,3,1),(1,1))
assert rat((1,2,1),(1,-2,1)) - rat((-1,1),(1,1)) == rat((2,0,6),(1,-1,-1,1))
assert rat((1,2,1),(1,-2,1)) + rat((1,1),(-1,1)) == rat((0,2,2),(1,-2,1))
# TODO need some additional test cases where there are common factors

#-----------------------------------------------------------------------------
# Check multiplication and division.

assert 1*rat(0) == 0
assert rat(0)*2 == 0
assert rat(1,2)*2 == 1
assert (rat(1,2)*rat(1,3)).numer == mpq(1,6)
assert (rat(1,2)*rat(1,3)).denom == 1
assert rat((1,2,1),(1,-2,1))*rat((-1,1),(1,1)) == rat((1,1),(-1,1))
assert rat((1,2,1),(1,-2,1))/rat((-1,1),(1,1)) == rat((1,3,3,1),(-1,3,-3,1))
# TODO need some additional test cases where there are common factors

#-----------------------------------------------------------------------------
# Check powers.

checkExcept = False
try:
    rat((1,2,3),(4,5,6))**0.5
except TypeError:
    checkExcept = True
assert checkExcept

assert rat((1,2,3,4),(5,6,7,8))**0 == 1
assert rat((-1,1),(1,1))**2 == rat((1,-2,1),(1,2,1))
assert rat((-1,1),(1,1))**3 == rat((-1,3,-3,1),(1,3,3,1))
assert rat((-1,1),(1,1))**-2 == rat((1,2,1),(1,-2,1))
assert rat((-1,1),(1,1))**-3 == rat((1,3,3,1),(-1,3,-3,1))

#-----------------------------------------------------------------------------
# Check derivative.

assert rat(0,2).deriv == 0
assert rat(1,2).deriv == 0
assert rat((1,1),1).deriv == 1
assert rat((-1,1),(1,1)).deriv == rat(2,(1,2,1))
assert rat((1,-2,1),(1,2,1)).deriv == rat((-4,4),(1,3,3,1))

#-----------------------------------------------------------------------------
# Check evaluation, sampling, and combination with polynomials by computing an
# expansion of the natural log.

from math import log as ln
z = rat((-1,1),(1,1))
p = poly([(mpq(1,n),n) for n in xrange(1,8,2)])
aln = 2*p(z) # Rational function approximating ln

# Compare the resulting approximation with the built-in function.
err = [abs(ln(x)-y) for x,y in aln.float().sample(1,2,100)]
assert len(err) == 100
assert max(err) < 1.25e-5

# check the integer logic.
assert z(4) == mpq(3,5)

# If numpy is installed, try evaluating the function using an array.
try:
    import numpy
    x = numpy.array([0,1,3.0])
    y = numpy.array([-1,0,0.5])
    assert (z(x) == y).all()
except ImportError:
    pass

#-----------------------------------------------------------------------------
print 'All tests PASS'

