#-----------------------------------------------------------------------------
# Copyright (c) 2005  Raymond L. Buvel
#
# The chebyshev module is used to create Chebyshev approximations to functions.
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
import clnum, sys

class Chebyshev(object):

    def __new__(cls, fun, a, b, order, prec=0):
        if order < 3:
            raise ValueError('The order must be at least 3')

        if a == b:
            raise ValueError('Need an interval')

        mpf = clnum.mpf
        cos = clnum.cos
        pi = clnum.pi(prec)

        # Force a standard order.
        a = mpf(a, prec)
        b = mpf(b, prec)
        if a > b:
            a,b = b,a

        # Compute the value of the function at the zeros of the highest order
        # Chebyshev polynomial.

        N = mpf(order, prec)
        bma = (b-a)/2
        bpa = (b+a)/2
        half = 1/mpf(2, prec)

        f = [fun(cos(pi*(k+half)/N)*bma + bpa) for k in xrange(order)]

        # Compute the coefficients.
        c = []
        for j in xrange(order):
            x = [f[k]*cos(pi*j*(k+half)/N) for k in xrange(order)]
            c.append(2*sum(x)/N)

        self = object.__new__(cls)
        self.coef = tuple(c)
        self.interval = a,b
        return self


    # Return the order of the approximation.
    def __len__(self):
        return len(self.coef)


    def __call__(self, x):
        '''Evaluate the function at the point x.
        '''

        a,b = self.interval

        if (x-a)*(x-b) > 0:
            raise ValueError('x not in range')

        # Change variable to range [-1..1]
        y = (2*x-(b+a))/(b-a)
        y2 = 2*y

        # Evaluate Clenshaw's recurrence.  Optimize the first two terms.
        c = self.coef
        dd = c[-1]
        d = y2*dd + c[-2]
        j = len(c) - 3
        while j >= 1:
            d, dd = y2*d-dd+c[j], d
            j -= 1

        return y*d - dd + c[0]/2

    def generate_code(self, name):
        a,b = self.interval
        c = self.coef
        lst = []
        add = lst.append
        add('double %s(double x)\n{' % name)
        add('    double const a = %r;' % float(a))
        add('    double const b = %r;' % float(b))
        add('    double y = (2*x-(b+a))/(b-a);')
        add('    double y2 = 2*y;')
        add('    double dd = %r;' % float(c[-1]))
        cj = float(c[-2])
        if cj:
            add('    double d = y2*dd + %r;' % cj)
        else:
            add('    double d = y2*dd;')
        add('    double tmp;')
        add('')
        j = len(c) - 3
        while j >= 1:
            cj = float(c[j])
            if cj:
                add('    tmp = y2*d - dd + %r;' % cj)
            else:
                add('    tmp = y2*d - dd;')
            add('    dd = d;')
            add('    d = tmp;')
            j -= 1

        cj = float(c[0])/2
        if cj:
            add('    return y*d - dd + %r;\n}\n' % cj)
        else:
            add('    return y*d - dd;\n}\n')
            
        return '\n'.join(lst)


    def edit(self, zero_band, max_order=sys.maxint):
        '''Edit the coefficients so that anything with absolute value less than
        or equal to the zero_band is set to zero.  The max_order parameter can
        be used to limit the order of the approximation.  A new instance is
        returned that contains the edited coefficients.
        '''
        order = min(max_order, len(self.coef))
        if order < 3:
            raise ValueError('The order must be at least 3')

        # Set all of the coefficients to zero that are within the specified
        # zero band.
        c = list(self.coef)
        for i,x in enumerate(c):
            if abs(x) <= zero_band:
                c[i] = 0

        # Reduce the order by removing all high order entries that are zero.
        while order > 3:
            if c[order-1]:
                break
            order -= 1

        new = object.__new__(Chebyshev)
        new.coef = tuple(c[:order])
        new.interval = self.interval
        return new


    def float(self):
        '''Return a version where all of the coefficients are floats.
        '''
        new = object.__new__(Chebyshev)
        new.coef = tuple([float(c) for c in self.coef])
        new.interval = float(self.interval[0]), float(self.interval[1])
        return new


    def sample(self, a, b, n):
        '''Evaluate the function at n sample points.

        The samples are evenly spaced in the interval [a..b]
        '''
        if n < 2 or a == b:
            raise ValueError('Call the function if you only want one sample')

        if isinstance(a, (int,long)) and isinstance(b, (int,long)):
            # Force float only in cases where both endpoints are integers.
            # Other data types are expected to handle fractional values.
            b = float(b)

        d = (b-a)/(n-1)
        for i in xrange(n):
            x = a + i*d
            yield x, self(x)

