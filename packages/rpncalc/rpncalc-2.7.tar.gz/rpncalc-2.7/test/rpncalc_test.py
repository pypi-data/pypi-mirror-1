#-----------------------------------------------------------------------------
# Unit test for the rpncalc module.
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
import sys
from clnum import mpf,mpq,cmpf,cmpq
import clnum
from rpncalc import rpncalc

#-----------------------------------------------------------------------------
# Check the stack against the arguments passed to this function.  Removes the
# data from the stack if the check succeeds.

def checkStack(*args):
    if len(args) != len(rpncalc.mainStack):
        raise ValueError('Stack length: expected %d, got %d' %
                         (len(args), len(rpncalc.mainStack)))
    stk = rpncalc.mainStack[:]
    stk.reverse()
    args = list(args)
    args.reverse()
    for i,(e,g) in enumerate(zip(args,stk)):
        if e != g:
            raise ValueError('Stack elt %d: expected %s, got %s' %
                             (i, e, g))
    # If the check passes, remove the data from the stack.
    del rpncalc.mainStack[:]

#-----------------------------------------------------------------------------
# Run the input string and check the stack against the expected result.
def case(inp, *rslt):
    global caseCount
    rpncalc.evalRpnString(inp)
    checkStack(*rslt)
    caseCount += 1

#-----------------------------------------------------------------------------
# Capture the output that goes to stdout and verify it against the expected
# result.

def ocase(inp, exp):
    global caseCount
    from cStringIO import StringIO
    strout = StringIO()

    sys.stdout = strout
    rpncalc.evalRpnString(inp)
    sys.stdout = sys.__stdout__

    got = strout.getvalue().strip()
    strout.close()
    if got != exp:
        raise ValueError('Output error: expected %s, got %s' % (exp, got))

    caseCount += 1

#-----------------------------------------------------------------------------
# Each case increments the case count if it passes.  This routine is used to
# verify that the correct number of cases were executed.

caseCount = 0
def checkCaseCount(exp):
    if exp == caseCount:
        print 'All tests PASS'
    else:
        raise ValueError('Case count: expected %d, got %d' %
                         (exp, caseCount))

#-----------------------------------------------------------------------------
# Replace findToken with one that records the tokens that are found.  Verify
# that all of the words in all of the vocabularies have been visited.

# Words in this list are best checked interactively.
ignoreList = '''words words_all help py bye .v .r prefer_cmpf prefer_cmpq
state ?
'''.split()

tokensFound = set(ignoreList)
_findToken_ = rpncalc.findToken

def _findToken(token):
    t = _findToken_(token)
    if t is not None:
        tokensFound.add(token)
    return t

rpncalc.findToken = _findToken

def checkVocabularies():
    notFound = set()
    for voc in rpncalc.Vocabulary._vocList:
        srchSet = set(voc.keys())
        nf = srchSet - tokensFound
        notFound = notFound | nf
    if notFound:
        print 'No test for: %s' % notFound
        raise RuntimeError('Missing test cases')

#-----------------------------------------------------------------------------
# Ckeck the basic operations.
#-----------------------------------------------------------------------------
case('1 2 3', 1,2,3)
case('1 2 +', 3)
case('1 2 -', -1)
case('2 3 *', 6)
case('1 2 /', mpq(1,2))  # Verifies that rational division is used.
case('3 2 //', 1)
case('5 2 %', 1)
case('5 2 divmod', 2,1)
case('2 3 **', 8)
case('256 8 >>', 1)
case('1 7 <<', 128)
case('0xAA55 0x3333 &', 0x2211)
case('0xAA55 0x55AA |', 0xFFFF)
case('0xAA55 0xF5FA ^', 0x5FAF)
case('1.9 int', 1)
case('1.9 long', 1)
case('1 float', 1.0)
case('1 complex', 1.0+0j)
case('1.9 round', 2)
case('1.54 1 round_n', 1.5)
case('1 2 max', 2)
case('1 2 min', 1)
case('-1 abs', 1)
case('1 neg', -1)
case('1 inv', -2)
case('3 1/x', mpq(1,3))
case('def f(x) x*x')
case('2 f', 4)

case('1 real', 1)
case('1 imag', 0)
case('1+1j imag', 1)
case('1+1j conjugate', cmpq(1,-1))

#-----------------------------------------------------------------------------
# Check the stack manipulation operators.
#-----------------------------------------------------------------------------
case('1 2 3 clear')
case('1 2 3 drop', 1,2)
case('1 2 3 2drop', 1)
case('1 2 3 nip', 1,3)
case('1 2 dup', 1,2,2)
case('1 2 2dup', 1,2,1,2)
case('1 2 over', 1,2,1)
case('1 2 3 rot', 2,3,1)
case('1 2 swap', 2,1)
# The following two test cases must be kept together as a pair.
case('1 2 >a', 1)
case('1 a>', 1,2)

case('1 >a a@ 1 + a>', 2,1)
assert len(rpncalc.alternateStack) == 0

#-----------------------------------------------------------------------------
# Check the math operations.
#-----------------------------------------------------------------------------
case('1 2 3 sum', 6)
case('sum', 0)
case('2 3 4 prod', 24)
case('prod', 0)
case('0 factorial', 1)  # Need a number of cases to test all of the boundary
case('1 factorial', 1)  # conditions.
case('2 factorial', 2)
case('3 factorial', 2*3)
case('4 factorial', 2*3*4)
case('0 lnfactorial', 0)
case('1 lnfactorial', 0)
case('2 lnfactorial', clnum.log(2))
case('3 lnfactorial', clnum.log(2*3))
case('4 lnfactorial', clnum.log(2*3)+clnum.log(4))
case('9 doublefactorial', 945)
case('4 2 binomial', 6)
case('pi 32767 ratapx', clnum.mpq(355,113))

case('1 2 3 4 5 stats', 3, clnum.sqrt(clnum.mpf(5)/2))

# Note: only the mapping of Python functions to calculator commands is tested.
# It is assumed that the Python functions are working correctly.
_half = mpf('0.5')
case('pi e', clnum.pi(0),clnum.exp1(0))
case('.5 acos', clnum.acos(_half))
case('.5 asin', clnum.asin(_half))
case('.5 atan', clnum.atan(_half))
case('.5 cos', clnum.cos(_half))
case('.5 sin', clnum.sin(_half))
case('.5 tan', clnum.tan(_half))
case('.5 cosh', clnum.cosh(_half))
case('.5 sinh', clnum.sinh(_half))
case('.5 tanh', clnum.tanh(_half))
case('.5 degrees', clnum.degrees(_half))
case('.5 radians', clnum.radians(_half))
case('.5 exp', clnum.exp(_half))
case('.5 log', clnum.log(_half))
case('.5 ln', clnum.log(_half))
case('.5 log10', clnum.log10(_half))
case('.5 log2', clnum.log(_half,2))
case('.5 3 logb', clnum.log(_half,3))
case('.5 sqrt', clnum.sqrt(_half))
case('.5 ceil', clnum.ceil(_half))
case('.5 floor', clnum.floor(_half))
case('1 2 atan2', clnum.atan2(1,2))
case('1 2 hypot', clnum.hypot(1,2))

case('use_degrees')
case('30 cos', clnum.cos(clnum.radians(30)))
case('30 sin', clnum.sin(clnum.radians(30)))
case('30 tan', clnum.tan(clnum.radians(30)))
case('.5 acos', clnum.degrees(clnum.acos(_half)))
case('.5 asin', clnum.degrees(clnum.asin(_half)))
case('.5 atan', clnum.degrees(clnum.atan(_half)))
case('1 2 atan2', clnum.degrees(clnum.atan2(1,2)))
case('use_radians')

#-----------------------------------------------------------------------------
_ihalf = cmpf('0.5j')
case('.5j acos', clnum.acos(_ihalf))
case('.5j asin', clnum.asin(_ihalf))
case('.5j atan', clnum.atan(_ihalf))
case('.5j acosh', clnum.acosh(_ihalf))
case('.5j asinh', clnum.asinh(_ihalf))
case('.5j atanh', clnum.atanh(_ihalf))
case('.5j cos', clnum.cos(_ihalf))
case('.5j sin', clnum.sin(_ihalf))
case('.5j tan', clnum.tan(_ihalf))
case('.5j cosh', clnum.cosh(_ihalf))
case('.5j sinh', clnum.sinh(_ihalf))
case('.5j tanh', clnum.tanh(_ihalf))
case('.5j exp', clnum.exp(_ihalf))
case('.5j log', clnum.log(_ihalf))
case('.5j ln', clnum.log(_ihalf))
case('.5j log10', clnum.log10(_ihalf))
case('.5j 10 logb', clnum.log10(_ihalf))
case('.5j sqrt', clnum.sqrt(_ihalf))
case('.5 cis', clnum.cis(_half))
case('1+2j phase', clnum.cmpf(1,2).phase)

#-----------------------------------------------------------------------------
# Check operations on variables.
#-----------------------------------------------------------------------------
case('1 := a 2 := b 3 := c 4 := d')
x = rpncalc.getVariables()
assert x.a == 1
assert x.b == 2
assert x.c == 3
assert x.d == 4

case('1 += a a', 2)
case('1 -= b b', 1)
case('2 *= c c', 6)
case('3 /= d d', mpq(4,3))

# Verify that a new variable can be added with setVariables and variables not
# in the input are not disturbed.  Also verifies that variables have precidence
# over built-in operations.
del x.a, x.b, x.c, x.d
x.e = 0
rpncalc.setVariables(x)
case('e', 0)
case('delete_variables e')
case('e', clnum.exp1(0))

x = rpncalc.getVariables()
assert x.a == 2
assert x.b == 1
assert x.c == 6
assert x.d == mpq(4,3)

#-----------------------------------------------------------------------------
# Check special cases in the integer conversion routine.
#-----------------------------------------------------------------------------
# Note: the other test cases in this unit test verify the other types of input.
# The integer converter has a lot of special logic that needs to be checked.

case('0x0',0)
case('0o0',0)
case('0b0',0)
case('-0x0',0)
case('-0o0',0)
case('-0b0',0)
case('+0x1',1)
case('+0o1',1)
case('+0b1',1)
case('-0x1',-1)
case('-0o1',-1)
case('-0b1',-1)
case('0xA5', 10*16+5)
case('0o13', 8+3)
case('0b0101', 5)

# Make sure the long suffix is supported and that leading zeros do not imply
# octal notation.
case('0098L', 98)
case('+0098L', 98)
case('-0098L', -98)
case('0098', 98)
case('+0098', 98)
case('-0098', -98)

#-----------------------------------------------------------------------------
# Check output conversions.
#-----------------------------------------------------------------------------

ocase('0 .x', '0x0')
ocase('0 .o', '0o0')
ocase('0 .b', '0b0')

ocase('-1 .x', '-0x1')
ocase('-1 .o', '-0o1')
ocase('-1 .b', '-0b1')

ocase('255 .x', '0xFF')
ocase('255 .o', '0o377')
ocase('255 .b', '0b11111111')

ocase('.5 .', '0.5')
ocase('1e-6 .', '1e-6')
ocase('5L .', '5')
ocase('1+1/2j .', '(1+1/2j)')
ocase('1+1.0j .', '(1.0+1.0j)')

ocase('.s', 'Stack depth: 0')
ocase('1 2 3 .s', 'Stack depth: 3\n3\n2\n1')
case('clear') # Dump the stack from the previous test case

#-----------------------------------------------------------------------------
# Check recursive use of the evaluation function.
#-----------------------------------------------------------------------------

rpncalc.prog('recurse', '2 +')

case('1 recurse 3 +', 6)

#-----------------------------------------------------------------------------
case('1/2', mpq(1,2))
case('.5 mpq', mpq(1,2))
case('1/2 1/3 +', mpq(5,6))
case('1/2 1/3 -', mpq(1,6))
case('1/3 3 *', 1)
case('1 mpq 3 /', mpq(1,3))  # Verifies the exception case in _div
case('1/2 8 **', mpq(1,256))
ocase('1 mpq 3 / .', '1/3')
ocase('1 cmpq 3 / .', '(1/3+0j)')

# Make sure augmented division handles rationals.
case('1 mpq := a  3 /= a a', mpq(1,3))
case('1 cmpq := a  3 /= a a', cmpq('1/3+0j'))

case('1/2 numer', 1)
case('1/2 denom', 2)
case('987654321987654321/2 numer', 987654321987654321)
case('1/987654321987654321 denom', 987654321987654321)

case('1.5 mpf', mpf(1.5))
case('1 cmpf', cmpf(1))

case('30 set_mpf_prec')
case('get_mpf_prec', 36)
case('1.1', mpf('1.1',36))

#-----------------------------------------------------------------------------
# Misc
#-----------------------------------------------------------------------------

def f(x):
    return x*x-2

rpncalc.function(f)

case('1 2 solve f', clnum.find_root(f, 1, 2, 1e-16))

#-----------------------------------------------------------------------------
checkVocabularies()
checkCaseCount(182)
