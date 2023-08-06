#-----------------------------------------------------------------------------
# Copyright (c) 2005  Raymond L. Buvel
#
# Unit test for the chebyshev module.
#
# The chebyshev module is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option) any
# later version.
#
# The chebyshev nodule is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# chebyshev; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#-----------------------------------------------------------------------------
import sys

# Structure the imports so they work for both a stand-alone module or
# packaged with rpncalc.

try:
    import chebyshev
except ImportError:
    from rpncalc import chebyshev

import clnum
from clnum import sin, cos

pi = clnum.pi(20)

sinx = chebyshev.Chebyshev(sin, -pi/2, pi/2, 20, 20)
cosx = chebyshev.Chebyshev(cos, -pi/2, pi/2, 20, 20)

assert len(sinx) == 20
assert len(cosx) == 20

err = [abs(y-sin(x)) for x,y in sinx.sample(-pi/2, pi/2, 1000)]
assert len(err) == 1000
assert max(err) < 1e-20
 
err = [abs(y-cos(x)) for x,y in cosx.sample(-pi/2, pi/2, 1000)]
assert len(err) == 1000
assert max(err) < 1e-20
 
sinx = sinx.edit(1e-16)
cosx = cosx.edit(1e-16)

err = [abs(y-sin(x)) for x,y in sinx.sample(-pi/2, pi/2, 1000)]
assert len(err) == 1000
assert max(err) < 1e-16
assert sinx.coef[::2] == (0,0,0,0,0,0,0,0)
 
err = [abs(y-cos(x)) for x,y in cosx.sample(-pi/2, pi/2, 1000)]
assert len(err) == 1000
assert max(err) < 1e-16
assert cosx.coef[1::2] == (0,0,0,0,0,0,0,0)

fd = open('sin.c', 'w')
fd.write(sinx.generate_code('sin'))
fd.close()

print 'All tests PASS'

# Generate an error curve that can be displayed if matplotlib is installed.
err = [(x, y-sin(x)) for x,y in sinx.sample(-pi/2, pi/2, 1000)]
x = [float(i[0]) for i in err]
y = [float(i[1]) for i in err]

try:
    from pylab import *
except ImportError:
    sys.exit()

plot(x,y)
show()
