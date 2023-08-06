#-----------------------------------------------------------------------------
# Copyright (c) 2005  Raymond L. Buvel
#
# The rpncalc module adds a reverse polish notation interpreter to Python.  The
# primary purpose is to use it as an interactive calculator.
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
import operator, sys, re, keyword, itertools
import clnum
from textwrap import TextWrapper

# Export the public interface
__all__ = '''mainStack alternateStack checkStack altCheckStack
Vocabulary installVocabulary removeVocabulary systemVoc userVoc
installFunctions makeAlias
parms_v_1 parms_0_1 parms_1_0 parms_1_1 parms_2_1 parms_2_2 parms_n_m
getName getVariables setVariables
findToken numberConverters number
parsedTokensList evalRpnString
rpn get push pop prog alias function
lnfactorial stats
installHelp auditHelp dumpHelp
'''.split()

#-----------------------------------------------------------------------------
# This is a two stack calculator.  Most activity takes place on the main stack.
# The alternate stack is a place to store temporary results so they are out of
# the way of the main calculation.
mainStack = []
alternateStack = []

#-----------------------------------------------------------------------------
# A number of vocabularies are searched for commands.  The built-in commands
# are in the system vocabulary.  The user vocabulary provides a place for user
# extensions.  The variable vocabulary is where user created variables are
# stored.  The search order is determined by the search list.
#
# When inserting and removing vocabularies from the search list, use the
# install and remove functions so that the priorities are properly managed.

class Vocabulary(dict):
    # Variable for handling the assignment of default priorities.
    _nextPriority = 1

    # Maintain a list of all the vocabularies that have been defined sorted in
    # priority order.
    _vocList = []

    def __init__(self, name, priority=None):
        self.name = name

        if priority is None:
            priority = Vocabulary._nextPriority
            Vocabulary._nextPriority += 1
        self.priority = priority

        Vocabulary._vocList.append(self)
        _sortVocList(Vocabulary._vocList)

    def __str__(self, _textwrap=TextWrapper(width=79)):
        s = 'Vocabulary %s:\n' % self.name
        keys = self.keys()
        if keys:
            keys.sort()
            lines = _textwrap.wrap(' '.join(keys))
            s += '%s\n' % ('\n'.join(lines))
        else:
            s += '<empty>\n'
        return s

#-----------------------------------------------------------------------------
# Sort a vocabulary list by priority.  Preserve the original ordering for
# duplicate priorities.

def _sortVocList(vocList):
    lst = [(x.priority,i,x) for i,x in enumerate(vocList)]
    lst.sort()
    for i,x in enumerate(lst):
        vocList[i] = x[-1]

#-----------------------------------------------------------------------------
def installVocabulary(voc):
    if voc in searchList:
        return False

    searchList.append(voc)
    _sortVocList(searchList)
    return True

#-----------------------------------------------------------------------------
def removeVocabulary(voc):
    if voc not in searchList:
        return False

    searchList.remove(voc)
    return True

#-----------------------------------------------------------------------------
# The priorities are set up so that the user variables are always searched
# first, then the user vocabulary, and the system vocabulary is always last.

systemVoc = Vocabulary('system', sys.maxint)
userVoc = Vocabulary('user', -sys.maxint+100)
variableVoc = Vocabulary('variable', -sys.maxint)

searchList = [variableVoc, userVoc, systemVoc]

#-----------------------------------------------------------------------------
# Functions for installing and displaying on-line help.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
def installHelp(name, stack, description,
                format=True, voc=None):
    if voc is None:
        voc = systemVoc
    fun = voc[name]
    fun._rpnstack = stack
    if format:
        desc = formatHelp(description)
    else:
        desc = []
        for line in description.split('\n'):
            line = line.rstrip()
            desc.append(line)
        if desc[-1].strip() == '':
            del desc[-1]
    fun._rpndesc = desc

#-----------------------------------------------------------------------------
def formatHelp(desc, wrap=TextWrapper(width=74,fix_sentence_endings=True)):
    desc = wrap.wrap(desc)
    return desc

#-----------------------------------------------------------------------------
def showHelp():
    try:
        name = parsedTokensList[-1].next()
    except StopIteration:
        print _defaultMessage
        return

    fun = findToken(name)

    if fun is None:
        print '"%s" not found' % name
        return

    try:
        stack = fun._rpnstack
        desc = fun._rpndesc
    except AttributeError:
        print 'No help on "%s"' % name
        return

    print '%s %s' % (name, stack)
    for line in desc:
        print '    %s' % line

#-----------------------------------------------------------------------------
def auditHelp():
    _textwrap=TextWrapper(width=79)
    for v in Vocabulary._vocList:
        lst = []
        for fun in v.keys():
            if not hasattr(v[fun],'_rpnstack'):
                lst.append(fun)
        if lst:
            lst.sort()
            print '\nVocabulary %s: no help on' % v.name
            lines = _textwrap.wrap(' '.join(lst))
            print '\n'.join(lines)

#-----------------------------------------------------------------------------
def dumpHelp(out):
    for v in Vocabulary._vocList:
        lst = []
        for fun in v.keys():
            if hasattr(v[fun],'_rpnstack'):
                lst.append(fun)

        if not lst:
            continue

        lst.sort()
        s = 'Vocabulary %s' % v.name
        m = '-'*len(s)
        out.write('\n%s\n%s\n%s\n' % (m,s,m))

        for name in lst:
            fun = v[name]
            try:
                stack = fun._rpnstack
                desc = fun._rpndesc
            except AttributeError:
                # Ignore incomplete help entries
                continue

            out.write('\n%s %s\n' % (name, stack))
            for line in desc:
                out.write('    %s\n' % line)

#-----------------------------------------------------------------------------
_defaultMessage = '''
To get help on a command type:

help name
    or
? name

If you need to exit the calculator use one of the following commands:

py - exit to Python.  If the interpreter is running interactive, this will
    put you at the Python prompt.

bye - completely exit the program.
'''[1:]

#-----------------------------------------------------------------------------
systemVoc['help'] = showHelp
systemVoc['?'] = showHelp

installHelp('help', '(name ( -- )', _defaultMessage, format=False)


#-----------------------------------------------------------------------------
# Exceptions used by the interpreter.
#-----------------------------------------------------------------------------

class RpncalcExit(Exception): pass
class RpncalcToPy(Exception): pass
class RpncalcError(Exception): pass

#-----------------------------------------------------------------------------
# This section contains functions used to wrap a Python function so that it can
# be used from the calculator.
#
# Note: all of these operations are designed so that the stack is preserved if
# the operation fails.  This makes it possible to use the Python interpreter to
# diagnose the problem and perhaps recover without losing any work.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
def _mkCheckStack(stack, name):
    def checkStack(expect, stack=stack, name=name):
        n = len(stack)
        if n >= expect:
            return

        plural = 's'
        if expect == 1:
            plural = ''

        msg = '%sStack Error: expected %d element%s got %d' % (name, expect,
                plural, n)
        raise RpncalcError(msg)

    return checkStack

checkStack = _mkCheckStack(mainStack, '')

altCheckStack = _mkCheckStack(alternateStack, 'Alternate ')

del _mkCheckStack

#-----------------------------------------------------------------------------
def parms_v_1(val):
    def fun(val=val):
        mainStack.append(val)
    return fun

def parms_0_1(op):
    def fun(op=op):
        mainStack.append(op())
    return fun

#-----------------------------------------------------------------------------
def parms_1_0(op):
    return parms_n_m(op, 1, 0)

def parms_1_1(op):
    return parms_n_m(op, 1, 1)

#-----------------------------------------------------------------------------
def parms_2_1(op):
    return parms_n_m(op, 2, 1)

def parms_2_2(op):
    return parms_n_m(op, 2, 2)

#-----------------------------------------------------------------------------
# Return a function wrapping the specified operation with appropriate stack
# manipulation.  Note that the number of returned parameters (m) can be 0, 1,
# or any value greater than 1.  The number of input parameters (n) must be at
# least 1 because in most cases where it is zero, the function does not need to
# be wrapped at all.  In the other cases, specific code can be used to wrap the
# function.

def parms_n_m(op, n, m):
    if n < 1 or m < 0:
        raise ValueError('n < 1 or m < 0')

    if m == 0:
        def fun(op=op, n=n):
            checkStack(n)
            op(*mainStack[-n:])
            del mainStack[-n:]

    elif m == 1:
        def fun(op=op, n=n):
            checkStack(n)
            mainStack[-n:] = (op(*mainStack[-n:]),)

    else:
        def fun(op=op, n=n):
            checkStack(n)
            mainStack[-n:] = op(*mainStack[-n:]) # Result is already a tuple

    return fun

#-----------------------------------------------------------------------------
# Install a set of functions from a module using the specified wrapping
# function.  Note: the module does not have to be a real Python module since
# the only requirement is that the module object respond to get attribute.

def installFunctions(udict, module, wrap, names):
    for name in names:
        udict[name] = wrap(getattr(module, name))

#-----------------------------------------------------------------------------
def makeAlias(udict, aliasList):
    for alias, name in aliasList:
        udict[alias] = udict[name]

#-----------------------------------------------------------------------------
# This section contains some basic operations.
#-----------------------------------------------------------------------------

# If both operands are integers, return a rational.  Otherwise, just perform
# the division operation.

def _div(a,b):
    if isinstance(a, (int,long)) and isinstance(b, (int,long)):
        return clnum.mpq(a,b)
    else:
        return operator.div(a,b)

def _inv(a):
    return _div(1,a)

# Operations on rational numbers.  Other numbers are coerced to rational since
# there is no good reason to generate exceptions.

def _numer(a):
    try:
        return a.numer
    except AttributeError:
        a = clnum.mpq(a)
        return a.numer

def _denom(a):
    try:
        return a.denom
    except AttributeError:
        a = clnum.mpq(a)
        return a.denom

# Operations on complex numbers.  Other numbers are coerced to complex since
# there is no good reason to generate exceptions.

def _real(a):
    try:
        return a.real
    except AttributeError:
        a = clnum.cmpf(a)
        return a.real

def _imag(a):
    try:
        return a.imag
    except AttributeError:
        a = clnum.cmpf(a)
        return a.imag

def _phase(a):
    try:
        return a.phase
    except AttributeError:
        a = clnum.cmpf(a)
        return a.phase

def _conjugate(a):
    try:
        return a.conjugate()
    except AttributeError:
        a = clnum.cmpf(a)
        return a.conjugate()

_prefer_cmpf_flag = True

def _prefer_cmpf():
    global _prefer_cmpf_flag
    _prefer_cmpf_flag = True

def _prefer_cmpq():
    global _prefer_cmpf_flag
    _prefer_cmpf_flag = False

systemVoc.update({
'+' : parms_2_1(operator.add),
'-' : parms_2_1(operator.sub),
'*' : parms_2_1(operator.mul),
'/' : parms_2_1(_div),
'//' : parms_2_1(operator.floordiv),
'1/x' : parms_1_1(_inv),
'%' : parms_2_1(operator.mod),
'**' : parms_2_1(operator.pow),

'>>' : parms_2_1(operator.rshift),
'<<' : parms_2_1(operator.lshift),

'&' : parms_2_1(operator.and_),
'|' : parms_2_1(operator.or_),
'^' : parms_2_1(operator.xor),

'divmod' : parms_2_2(divmod),

'numer' : parms_1_1(_numer),
'denom' : parms_1_1(_denom),

'real' : parms_1_1(_real),
'imag' : parms_1_1(_imag),
'phase' : parms_1_1(_phase),
'conjugate' : parms_1_1(_conjugate),

'prefer_cmpf' : _prefer_cmpf,
'prefer_cmpq' : _prefer_cmpq,

'set_mpf_prec' : parms_1_0(clnum.set_default_precision),
'get_mpf_prec' : parms_0_1(clnum.get_default_precision),

'pi' : parms_0_1(clnum.pi),
'e' : parms_0_1(clnum.exp1),

'ratapx' : parms_2_1(clnum.ratapx),
})

import __builtin__ as _builtin
installFunctions(systemVoc, _builtin, parms_1_1,
    'int long float complex'.split())
installFunctions(systemVoc, _builtin, parms_2_1,
    'max min'.split())
installFunctions(systemVoc, operator, parms_1_1, 'abs neg inv'.split())
installFunctions(systemVoc, clnum, parms_1_1, 'mpf mpq cmpf cmpq'.split())

del _builtin, _real, _imag, _phase, _conjugate, _prefer_cmpf, _prefer_cmpq
del _numer, _denom, _inv

installHelp('+', '(a b -- c)', 'c = a+b')
installHelp('-', '(a b -- c)', 'c = a-b')
installHelp('*', '(a b -- c)', 'c = a*b')
installHelp('/', '(a b -- c)', 'c = a/b')
installHelp('%', '(a b -- c)', 'c = a%b')
installHelp('//', '(a b -- c)', 'c = a//b')
installHelp('**', '(a b -- c)', 'c = a**b')
installHelp('&', '(a b -- c)', 'c = a&b')
installHelp('|', '(a b -- c)', 'c = a|b')
installHelp('^', '(a b -- c)', 'c = a^b')
installHelp('1/x', '(x -- y)', 'y = 1/x')
installHelp('<<', '(i n -- j)', 'j = i<<n')
installHelp('>>', '(i n -- j)', 'j = i>>n')
installHelp('divmod', '(a b -- c d)', 'c,d = divmod(a,b)')

installHelp('int', '(x -- y)', 'Convert to a Python integer.')
installHelp('long', '(x -- y)', 'Convert to a Python long.')
installHelp('float', '(x -- y)', 'Convert to a Python float.')
installHelp('complex', '(x -- y)', 'Convert to a Python complex.')
installHelp('mpf', '(x -- y)', 'Convert to arbitrary precision float.')
installHelp('mpq', '(x -- y)', 'Convert to rational.')
installHelp('cmpf', '(x -- y)', 'Convert to arbitrary precision complex.')
installHelp('cmpq', '(x -- y)', 'Convert to complex rational.')

installHelp('max', '(a b -- c)', 'Return the maximum of a and b.')
installHelp('min', '(a b -- c)', 'Return the minimum of a and b.')

installHelp('abs', '(x -- y)', 'Return the absolute value of x.')
installHelp('neg', '(x -- y)', 'Change the sign of x.')
installHelp('inv', '(x -- y)', 'Return the integer x with all bits inverted.')

installHelp('numer', '(x -- y)',
    'Return the numerator of the rational number or rational function.')
installHelp('denom', '(x -- y)',
    'Return the denominator of the rational number or rational function.')

installHelp('real', '(x -- y)',
    'Return the real part of the complex number x.')
installHelp('imag', '(x -- y)',
    'Return the imaginary part of the complex number x.')
installHelp('phase', '(x -- y)',
    'Return the phase of the complex number x in radians.')
installHelp('conjugate', '(x -- y)',
    'Return the complex conjugate of x.')

installHelp('prefer_cmpf', '( -- )',
    'When converting complex numbers with integer parts, use cmpf.')
installHelp('prefer_cmpq', '( -- )',
    'When converting complex numbers with integer parts, use cmpq.')

installHelp('get_mpf_prec', '( -- n)',
    'Return the number of decimal digits of precision used when converting '
    'to mpf and cmpf.')

installHelp('set_mpf_prec', '(n -- )',
    'Set the number of decimal digits of precision used when converting '
    'to mpf and cmpf.')

installHelp('e', '( -- e)', 'base of the natural logarithms')
installHelp('pi', '( -- pi)', 'mathematical constant pi')

installHelp('ratapx', '(x maxint -- y)',
    'Approximate the value x by a rational number where the numerator and '
    'denominator are constrained to maxint.')

#-----------------------------------------------------------------------------
# Stack manipulation operations
#-----------------------------------------------------------------------------
def _clear():
    del mainStack[:]

def _swap():
    checkStack(2)
    a,b = mainStack[-2:]
    mainStack[-2:] = b,a

def _drop():
    checkStack(1)
    mainStack.pop()

def _2drop():
    checkStack(2)
    del mainStack[-2:]

def _nip():
    checkStack(2)
    del mainStack[-2]

def _dup():
    checkStack(1)
    mainStack.append(mainStack[-1])

def _2dup():
    checkStack(2)
    mainStack.extend(mainStack[-2:])

def _over():
    checkStack(2)
    mainStack.append(mainStack[-2])

def _rot():
    checkStack(3)
    a,b,c = mainStack[-3:]
    mainStack[-3:] = b,c,a

def _toAlt():
    checkStack(1)
    alternateStack.append(mainStack.pop())

def _fromAlt():
    altCheckStack(1)
    mainStack.append(alternateStack.pop())

def _fetchAlt():
    altCheckStack(1)
    mainStack.append(alternateStack[-1])

systemVoc.update({
'clear' : _clear,
'drop' : _drop,
'2drop' : _2drop,
'nip' : _nip,
'dup' : _dup,
'2dup' : _2dup,
'over' : _over,
'rot' : _rot,
'swap' : _swap,

'>a' : _toAlt,
'a>' : _fromAlt,
'a@' : _fetchAlt,
})

# Don't need these operations in the module namespace so delete them.
# Note: if the user needs to access these operations from Python code, just
# index the system vocabulary.
del _swap, _drop, _dup, _rot, _clear, _toAlt, _fromAlt, _fetchAlt, _over
del _2drop, _2dup

installHelp('clear', '(... -- )', 'Clear the stack.')
installHelp('drop', '(a -- )', 'Delete the top of the stack.')
installHelp('nip', '(a b -- b)', 'Delete the next on the stack.')
installHelp('dup', '(a -- a a)', 'Duplicate the top of the stack.')
installHelp('swap', '(a b -- b a)', 'Swap the top two elements on the stack.')
installHelp('over', '(a b -- a b a)', 'Copy next on the stack.')
installHelp('rot', '(a b c -- b c a)',
    'Rotate the third element to the top of the stack.')
installHelp('2drop', '(a b -- )', 'Delete the top two stack elements.')
installHelp('2dup', '(a b -- a b a b)', 'Duplicate the top two stack elements.')
installHelp('>a', '(a -- )', 'Move element to the alternate stack.')
installHelp('a>', '( -- a)', 'Move element from the alternate stack.')
installHelp('a@', '( -- a)',
    'Fetch the top element from the alternate stack without removing it.')

#-----------------------------------------------------------------------------
# This section installs functions from the clnum module.
#-----------------------------------------------------------------------------

# Calculators typically allow the user to select whether the trig functions
# operate with degrees or radians.  The following functions implement this
# feature.
#
# NOTE: the clnum.degrees and clnum.radians functions do not work for complex
# types.  The user must switch to radian mode when working with complex
# numbers.  This is to avoid confusion.  The complex forms are always discussed
# in text books using radian measure.

_trig_deg_mode = False # For backward compatibility, default to radians.

def _use_degrees():
    global _trig_deg_mode
    _trig_deg_mode = True

def _use_radians():
    global _trig_deg_mode
    _trig_deg_mode = False

def _trig(op):
    def fun(op=op):
        checkStack(1)
        a = mainStack[-1]
        if _trig_deg_mode:
            a = clnum.radians(a)
        r = op(a)
        mainStack[-1] = r
    return fun

def _atrig(op):
    def fun(op=op):
        checkStack(1)
        a = mainStack[-1]
        r = op(a)
        if _trig_deg_mode:
            r = clnum.degrees(r)
        mainStack[-1] = r
    return fun

def _atan2():
    checkStack(2)
    a,b = mainStack[-2:]
    r = clnum.atan2(a,b)
    if _trig_deg_mode:
        r = clnum.degrees(r)
    mainStack[-2:] = r,


_trig_list = 'cos sin tan'.split()
_atrig_list = 'acos asin atan'.split()

_math_1_1_list = '''
cosh sinh tanh
acosh asinh atanh
degrees radians
exp log log10
sqrt cis
ceil floor round
'''.split()
_math_2_1_list = 'hypot'.split()

_mathAliasList = [
    ('ln','log'),
]

installFunctions(systemVoc, clnum, parms_1_1, _math_1_1_list)
installFunctions(systemVoc, clnum, parms_2_1, _math_2_1_list)
installFunctions(systemVoc, clnum, _trig, _trig_list)
installFunctions(systemVoc, clnum, _atrig, _atrig_list)
makeAlias(systemVoc, _mathAliasList)

# Make the round and log operations available in two parameter form.
systemVoc['round_n'] = parms_2_1(clnum.round)
systemVoc['logb'] = parms_2_1(clnum.log)


# Note: the built-in sum function does not work for all objects.  In particular
# it does not work with polynomial objects.
def _sum(add=operator.add):
    if len(mainStack) == 0:
        mainStack.append(0)
        return
    s = reduce(add, mainStack)
    del mainStack[:]
    mainStack.append(s)

def _prod(mul=operator.mul):
    if len(mainStack) == 0:
        mainStack.append(0)
        return
    p = reduce(mul, mainStack)
    del mainStack[:]
    mainStack.append(p)

def lnfactorial(n):
    if n < 0:
        raise ValueError('n cannot be negative')
    elif n < 2:
        return 0.0
    return reduce(operator.add, itertools.imap(clnum.log, xrange(2,n+1)) )

def stats(data):
    N = clnum.mpf(len(data))
    if N < 3:
        raise ValueError('Need at least two data points')
    mean = sum(data)/N
    # Note: taking the absolute value makes this work for complex numbers.
    ds = [abs(x-mean)**2 for x in data]
    std = clnum.sqrt(sum(ds)/(N-1))
    return mean, std

def _stats():
    mainStack[:] = stats(mainStack)

def _solve(a, b):
    f = findToken(getName())

    def func(x, fun=f):
        mainStack.append(x)
        fun()
        return mainStack.pop()

    return clnum.find_root(func, a, b, 1e-16, 100)

systemVoc.update({
'sum' : _sum,
'prod' : _prod,
'factorial' : parms_1_1(clnum.factorial),
'doublefactorial' : parms_1_1(clnum.doublefactorial),
'binomial' : parms_2_1(clnum.binomial),
'lnfactorial' : parms_1_1(lnfactorial),
'atan2' : _atan2,
'log2' : parms_1_1(lambda x: clnum.log(x,2)),
'solve' : parms_2_1(_solve),
'stats' : _stats,
'use_degrees' : _use_degrees,
'use_radians' : _use_radians,
})

del _sum, _prod, _solve
del _use_degrees, _use_radians, _trig, _atrig, _atan2, _trig_list, _atrig_list
del _math_1_1_list, _math_2_1_list, _mathAliasList

#-----------------------------------------------------------------------------
# This section installs some display operations.
#-----------------------------------------------------------------------------

def _printBaseValue(n, base):
    n = int(n)

    # Handle the sign
    neg = n < 0
    n = abs(n)

    # Make sure the base is one that is supported by picking up the prefix
    # before attempting the conversion.  Note the algorithm can be extended to
    # support any base but acceptable prefixes need to be defined.
    bases = {16:'0x', 8:'0o', 2:'0b'}
    prefix = bases[base]

    if n == 0:
        print '%s0' % prefix
        return

    digits = '0123456789ABCDEF'
    lst = []
    while n:
        n,m = divmod(n,base)
        lst.append(digits[m])
    lst.append(prefix)
    if neg:
        lst.append('-')
    lst.reverse()
    print ''.join(lst)


# Note: need to capture a reference to _printBaseValue since it is being
# deleted from the global namespace to eliminate clutter.
def _printHexValue(n, pval=_printBaseValue):
    pval(n, 16)

def _printOctalValue(n, pval=_printBaseValue):
    pval(n, 8)

def _printBinaryValue(n, pval=_printBaseValue):
    pval(n, 2)

# The usual calculator display operations don't need a lot of digits.  The
# usual str() representation of a Python float is a better alternative than the
# str() representation of mpf.  The issues are that the representation of
# the exponent is platform dependent and does not match mpf.  Also, the
# exponent range of mpf is much larger than a float.  We will use Python's
# float formatting to get the rounding to work out and substitute the correct
# exponent.
def _round_mpf(x):
    if x == 0:
        return str(x)
    elif x < 0:
        sign = '-'
        x = -x
    else:
        sign = ''

    y = str(x).split('e')
    if len(y) == 1:
        s = str(float(x))
        if 'e' in s:
            y,exp = s.split()
            return '%s%se%s' % (sign,y,int(exp))
        return sign+s

    y,exp = y
    y,e = str(float(y+'e30')).split('e')
    exp = int(exp) + int(e) - 30
    return '%s%se%s' % (sign,y,exp)

def _printValue(n):
    if isinstance(n, clnum.mpf):
        print _round_mpf(n)
        return

    elif isinstance(n, clnum.cmpf):
        x,y = _round_mpf(n.real), _round_mpf(n.imag)
        if y[0] in '+-':
            sign = ''
        else:
            sign = '+'
        print '(%s%s%sj)' % (x,sign,y)
        return

    print n

def _printRepr(n):
    print repr(n)

def _printStack():
    print 'Stack depth:', len(mainStack)
    s = mainStack[-6:]
    s.reverse()
    for n in s:
        _printValue(n)

systemVoc.update({
'.s' : _printStack,
'.' : parms_1_0(_printValue),
'.r' : parms_1_0(_printRepr),
'.x' : parms_1_0(_printHexValue),
'.o' : parms_1_0(_printOctalValue),
'.b' : parms_1_0(_printBinaryValue),
})

del _printStack, _printBaseValue, _printRepr
del _printHexValue, _printOctalValue, _printBinaryValue

installHelp('.', '(x -- )', 'Print the value.')
installHelp('.r', '(x -- )', 'Print the representation of the value.')
installHelp('.x', '(x -- )', 'Print the integer part of value in hex.')
installHelp('.b', '(x -- )', 'Print the integer part of value in binary.')
installHelp('.o', '(x -- )', 'Print the integer part of value in octal.')
installHelp('.s', '(... -- ...)',
    'Print the stack without removing anything.')

#-----------------------------------------------------------------------------
def words():
    for voc in searchList:
        print voc

def words_all():
    for voc in Vocabulary._vocList:
        print voc

def state():
    if _trig_deg_mode:
        print 'Angles in degrees'
    else:
        print 'Angles in radians'

    if _prefer_cmpf_flag:
        print 'Integers in complex input are treated as floating point.'
    else:
        print 'Integers in complex input are treated as rationals.'

systemVoc['words'] = words
systemVoc['words_all'] = words_all
systemVoc['state'] = state

del words, words_all, state

installHelp('words', '( -- )', 
    'Print all the words in the current search order.')

installHelp('words_all', '( -- )', 
    'Print all the words in all vocabularies.')

installHelp('state', '( -- )', 
    'Print the values of some global settings such as the angle mode.')

#-----------------------------------------------------------------------------
# This section installs commands that allow assignment to variables.
#-----------------------------------------------------------------------------

# Validate a name to avoid creating variables that cannot be easily accessed
# from the Python interpreter.  This also avoids the absurdity of redefining
# the meaning of an integer.
_nameRe = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')
def getName():
    try:
        name = parsedTokensList[-1].next()
    except StopIteration:
        raise RpncalcError('Need a name')

    if _nameRe.match(name):
        if not keyword.iskeyword(name):
            return name

    msg = 'Name Error: "%s" is invalid' % name
    raise RpncalcError(msg)

def _assignment():
    name = getName()
    checkStack(1)
    val = mainStack.pop()
    variableVoc[name] = parms_v_1(val)

def _augAssignment(op):
    def fun(op=op):
        name = getName()
        checkStack(1)
        variableVoc[name]()
        val1 = mainStack.pop()
        val2 = mainStack.pop()
        variableVoc[name] = parms_v_1(op(val1,val2))
    return fun

def _printVars():
    print getVariables()

def _delete_variables():
    for name in parsedTokensList[-1]:
        try:
            del variableVoc[name]
        except KeyError:
            raise RpncalcError('"%s" is not a variable' % name)

systemVoc.update({
':=' : _assignment,
'+=' : _augAssignment(operator.add),
'-=' : _augAssignment(operator.sub),
'*=' : _augAssignment(operator.mul),
'/=' : _augAssignment(_div),
'.v' : _printVars,
'delete_variables' : _delete_variables,
})

del _assignment, _augAssignment, _printVars, _delete_variables

installHelp(':=', '(v (x -- )', 
    'Assign the value x to the variable v (creating it if necessary).')

installHelp('+=', '(v (x -- )', 
    'Add the value x to the variable v.')

installHelp('-=', '(v (x -- )', 
    'Subtract the value x from the variable v.')

installHelp('*=', '(v (x -- )', 
    'Multiply the value x into the variable v.')

installHelp('/=', '(v (x -- )', 
    'Divide the value x into the variable v.')

installHelp('.v', '( -- )', 'Print the currently defined variables.')

installHelp('delete_variables', '(... ( -- )', 
    'Delete all of the variables listed.')

#-----------------------------------------------------------------------------
# To interface the variables to Python, use a class and transform the internal
# fuction representation to values the user can access from an instance of the
# class.  Also provide the capability to easily print the values of the
# variables.

class Variables:
    def __str__(self):
        lst = []
        for key,value in self.__dict__.iteritems():
            if key.startswith('__'):
                continue
            lst.append('%s = %s' % (key, value))
        lst.sort()
        return '\n'.join(lst)


def getVariables():
    '''Get the variables defined in the RPN interpreter and return them in an
    instance of the Variables class.  Printing this instance will display all
    of the variables and their values.
    '''
    variables = Variables()
    for key in variableVoc:
        variableVoc[key]()
        value = mainStack.pop()
        setattr(variables, key, value)
    return variables


def setVariables(variables):
    '''Set the variables in the RPN interpreter from the members of the object
    passed in.  This may create new variables or update existing variables.
    '''
    for key,value in variables.__dict__.iteritems():
        if key.startswith('__'):
            continue
        variableVoc[key] = parms_v_1(value)

#-----------------------------------------------------------------------------
# Define simple Python functions and install them into the calculator from the
# RPN environment.

def _def():
    try:
        fun = parsedTokensList[-1].next()
    except StopIteration:
        raise RpncalcError('Need a function declaration')

    dec = list(parsedTokensList[-1])
    name = fun.split('(')[0]

    code = 'def %s: return (%s)' % (fun, ' '.join(dec))
    gbl = sys.modules['__main__'].__dict__
    namespace = {}
    exec code in gbl,namespace
    function(namespace[name])

systemVoc['def'] = _def
del _def

installHelp('def', '(f(...) ... ( -- )', 
    'Define a one-line function (see programming section of user manual).')

#-----------------------------------------------------------------------------
# This section contains functions that parse and evaluate commands.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
def parseTokens(inpstr):
    # Strip off comments
    inpstr = inpstr.split('#')[0]

    # Parse the resulting input by splitting on white space.
    for token in inpstr.split():
        yield token

#-----------------------------------------------------------------------------
def findToken(token):
    for searchVoc in searchList:
        if token in searchVoc:
            return searchVoc[token]
    # Explicitly return None if not found
    return None

#-----------------------------------------------------------------------------
# Users can control what numeric conversions are performed by modifying this
# list.  For example, rational numbers can be used by installing a converter at
# the appropriate place in the list.
#
# NOTE: clnum provides the functionality that was previously handled with a
# number of separate functions.  This implementation remains to support the
# ratfun module.

def _number(s):
    return clnum.number_str(s, prefer_cmpf=_prefer_cmpf_flag)

numberConverters = [_number]

def number(s):
    for converter in numberConverters:
        try:
            n = converter(s)
        except (ValueError,ZeroDivisionError):
            continue
        return n
    # Explicitly return None if can't convert using the currently selected set
    # of converters.
    return None

#-----------------------------------------------------------------------------
# Use a stack of parsed token iterators so that evalRpnString can be called
# recursively.  This allows the user to install functions that execute a string
# of calculator commands.

parsedTokensList = []

def evalRpnString(s):
    '''Evaluate a string of RPN interpreter commands.
    '''
    tokens = parseTokens(s)
    parsedTokensList.append(tokens)

    while True:
        # Get the next token and return if there are no more in the input
        # stream.
        try:
            token = tokens.next()
        except StopIteration:
            parsedTokensList.pop()
            return

        # First try to find a function to execute
        fun = findToken(token)
        if fun is not None:
            try:
                fun()
                continue
            except KeyboardInterrupt:
                # For this case, we want the Python interpreter to handle it.
                raise
            except (RpncalcError,StandardError), msg:
                print "Command '%s'" % token
                print msg
                _clearTokensList()
                return

        # Next try to convert the token to a number and push it on the stack.
        n = number(token)
        if n is not None:
            mainStack.append(n)
        else:
            # Print an error message and stop interpreting the token stream.
            print "Token '%s' not recognized" % token
            _clearTokensList()
            return


def _clearTokensList():
    # If the token list is nested, someone has programmed something
    # incorrectly.  Instead of flushing the token list, leave it alone and
    # raise an exception so the user has a chance to debug the problem.
    if len(parsedTokensList) > 1:
        raise RuntimeError('Nested evaluation')

    parsedTokensList.pop()

#-----------------------------------------------------------------------------
# The following commands allow the user to completely exit the calculator or
# return to the Python interpreter.

def _bye():
    raise RpncalcExit('Exit')

systemVoc['bye'] = _bye
del _bye

def _topython():
    # Flush the input stream and raise the exception that will kick us back
    # into Python.
    del parsedTokensList[:]
    raise RpncalcToPy('Exit to Python')

systemVoc['py'] = _topython
del _topython

installHelp('py', '( -- )', 
'Exit to the Python interpreter.  Return using the rpn() function.')

installHelp('bye', '( -- )', 'Exit the interpreter.')

#-----------------------------------------------------------------------------

installHelp('log10', '(x -- y)', 'base 10 logarithm of x.')
installHelp('log2', '(x -- y)', 'base 2 logarithm of x.')
installHelp('logb', '(x b -- y)', 'base b logarithm of x.')
installHelp('log', '(x -- y)', 'natural logarithm (base e) of x.')
installHelp('ln', '(x -- y)', 'natural logarithm (base e) of x.')
installHelp('sqrt', '(x -- y)', 'square root of x.')
installHelp('exp', '(x -- y)', 'exponential of x.')
installHelp('degrees', '(x -- y)', 'Convert radians to degrees.')
installHelp('radians', '(x -- y)', 'Convert degrees to radians.')

installHelp('ceil', '(x -- y)', 
    'Return the ceiling of x as mpf.  This is the smallest integral value such '
    'that y>=x.')
installHelp('floor', '(x -- y)', 
    'Return the floor of x as mpf.  This is the largest integral value such '
    'that y<=x.')

installHelp('use_degrees', '( -- )', 'Set angle measure to degrees.')
installHelp('use_radians', '( -- )', 'Set angle measure to radians.')

_trig_doc = ''' where %s is measured in radians or degrees depending on the
setting of the angle measure.  Use the state command to determine the
current setting.  If the input is complex, only radians are allowed.'''

installHelp('sin', '(x -- y)', 'y = sin(x)'+(_trig_doc % 'x'))
installHelp('cos', '(x -- y)', 'y = cos(x)'+(_trig_doc % 'x'))
installHelp('tan', '(x -- y)', 'y = tan(x)'+(_trig_doc % 'x'))

installHelp('asin', '(x -- y)', 'y = asin(x)'+(_trig_doc % 'y'))
installHelp('acos', '(x -- y)', 'y = acos(x)'+(_trig_doc % 'y'))
installHelp('atan', '(x -- y)', 'y = atan(x)'+(_trig_doc % 'y'))
installHelp('atan2', '(y x -- z)',
'''z = atan2(y, x) where z is measured in radians or degrees depending on the
setting of the degrees mode flag.  Use the state command to determine the
current setting.  The inputs must be real.''')
del _trig_doc

installHelp('sinh', '(x -- y)', 'y = sinh(x) hyperbolic sine')
installHelp('cosh', '(x -- y)', 'y = cosh(x) hyperbolic cosine')
installHelp('tanh', '(x -- y)', 'y = tanh(x) hyperbolic tangent')

installHelp('asinh', '(x -- y)', 'y = asinh(x) inverse hyperbolic sine')
installHelp('acosh', '(x -- y)', 'y = acosh(x) inverse hyperbolic cosine')
installHelp('atanh', '(x -- y)', 'y = atanh(x) inverse hyperbolic tangent')

installHelp('cis', '(x -- y)',
    'y = cos(x) + 1j*sin(x) where x is measured in radians.')

installHelp('hypot', '(x y -- z)',
    'Return the Euclidian distance, sqrt(x*x + y*y).')

installHelp('sum', '(... -- s)',
    'Return the sum of all the elements on the stack.')

installHelp('prod', '(... -- p)',
    'Return the product of all the elements on the stack.')

installHelp('stats', '(... -- mean std)',
    'Return the mean and standard deviation of all the elements on the stack.')

installHelp('binomial', '(m n -- y)',
    'y = m!/n!(m-n)! where m and n are integers.')
installHelp('factorial', '(n -- y)', 'y = n! where n is an integer.')
installHelp('doublefactorial', '(n -- y)', 'y = n!! where n is an integer.')
installHelp('lnfactorial', '(n -- y)', 'y = ln(n!) where n is an integer.')

installHelp('solve', '(f (x1 x2 -- x)',
'''Solve the equation f(x) = 0.  The parameters x1 and x2 must bound the
solution.  The function f(x) must take a single real input and produce a single
real output.''')

installHelp('round', '(x -- y)', 'Round x to the nearest integer.')
installHelp('round_n', '(x n -- y)',
    'Round x to n digits after the decimal point.')

#-----------------------------------------------------------------------------
# Functions used from the Python interpreter.
#-----------------------------------------------------------------------------

def rpn(prompt='rp> '):
    '''Run the RPN interpreter and terminate on EOF on input.  Any exceptions
    are allowed to propagate to the Python interpreter so the user has a chance
    to debug the calculation (provided the Python interpreter is running
    interactive).
    '''
    # Flush the token list so that there is no possibility to execute some old
    # unprocessed commands.
    del parsedTokensList[:]

    while True:
        try:
            s = raw_input(prompt)
        except EOFError:
            print ''
            sys.exit()

        try:
            evalRpnString(s)
        except RpncalcExit:
            sys.exit()
        except RpncalcToPy:
            return


#-----------------------------------------------------------------------------
def pop(n=1):
    '''Get the specified number of elements from the stack and remove
    them.  Note that a shorter list may be returned if the stack does not
    contain the requested number.
    '''
    r = get(n)
    del mainStack[-n:]
    return r


def get(n=1):
    '''Get the specified number of elements from the stack without removing
    them.  Note that a shorter list may be returned if the stack does not
    contain the requested number.
    '''
    r = mainStack[-n:]
    if not r:
        return None
    if len(r) == 1:
        return r[0]
    return r


def push(*args):
    '''Push a set of values onto the stack.
    '''
    mainStack.extend(args)


#-----------------------------------------------------------------------------
def prog(name, cmdstr, voc=userVoc):
    '''Create a program that executes a string of calculator commands.

    name - the name of the program
    cmdstr - string containing a set of commands that can be executed by the
        RPN interpreter.
    voc - optional vocabulary where the program is installed.
    '''
    if not isinstance(name, basestring):
        raise RpncalcError('name must be a string')

    cmdlst = []
    for line in cmdstr.split('\n'):
        # Strip off comments and extra white space.
        line = line.split('#')[0]
        line = line.strip()

        # Skip blank lines.
        if line:
            cmdlst.append(line)

    def _program(cmdlst=cmdlst):
        for line in cmdlst:
            evalRpnString(line)

    # Install the program.
    voc[name] = _program


#-----------------------------------------------------------------------------
def alias(name, newName, voc=userVoc):
    '''Create an alias of an existing command.

    name - name of the original command.
    newName - name of the alias.
    voc - optional vocabulary where the alias is installed.
    '''
    fun = findToken(name)
    if fun is None:
        raise RpncalcError('"%s" not found' % name)

    if not isinstance(newName, basestring):
        raise RpncalcError('newName must be a string')

    voc[newName] = fun


#-----------------------------------------------------------------------------
def function(func, inp=None, out=1, voc=userVoc, name=None):
    '''Install a function into the calculator.

    func - Python function to install.
    inp - number of input parameters.  If None, the number of parameters is
        determined from the function definition.
    out - number of output values
    voc - optional vocabulary where the function is installed.
    name - optional name for the function in the calculator environment.  If
        not supplied, the original Python function name is used.
    '''
    if inp is None:
        import inspect
        inp = len(inspect.getargspec(func)[0])

    if name is None:
        name = func.__name__

    if inp == 0 and out == 1:
        voc[name] = parms_0_1(func)
    else:
        voc[name] = parms_n_m(func, inp, out)

