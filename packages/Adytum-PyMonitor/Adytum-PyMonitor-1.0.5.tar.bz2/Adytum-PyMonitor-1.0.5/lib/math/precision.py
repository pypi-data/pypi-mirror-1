'''
Title: Binary floating point summation accurate to full precision
Submitter: Raymond Hettinger
Last Updated: 2005/04/19
Version no: 1.7
Category: Algorithms
URL: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/393090
 
Description:

Completely eliminates rounding errors and catastophic cancellation during summation by keeping full precision intermediate subtotals. Offers three alternative approaches, each using a different technique to store exact subtotals.
'''

def msum(iterable):
    "Full precision summation using multiple floats for intermediate values"

    partials = []               # sorted, non-overlapping partial sums
    for x in iterable:
        newpartials = []
        for y in partials:
            if abs(x) < abs(y):
                x, y = y, x
            hi = x + y
            lo = y - (hi - x)
            if lo:
                newpartials.append(lo)
            x = hi
        partials = newpartials + [x]
    return sum(partials)


from math import frexp, ldexp
from decimal import getcontext, Decimal, Inexact
getcontext().traps[Inexact] = True

def dsum(iterable):
    "Full precision summation using Decimal objects for intermediate values"

    total = Decimal(0)
    for x in iterable:
        # transform (exactly) a float to m * 2 ** e where m and e are integers
        mant, exp = frexp(x)
        mant, exp = int(mant * 2 ** 53), exp-53

        # Convert (mant, exp) to a Decimal and add to the cumulative sum.
        # If the precision is too small for exact conversion and addition,
        # then retry with a larger precision.
        while 1:
            try:
                newtotal = total + mant * Decimal(2) ** exp
            except Inexact:
                getcontext().prec += 1
            else:
                total = newtotal
                break
    return float(total)


def lsum(iterable):
    "Full precision summation using long integers for intermediate values"

    tmant, texp = 0, 0
    for x in iterable:
        # transform (exactly) a float to m * 2 ** e where m and e are integers
        mant, exp = frexp(x)
        mant, exp = int(mant * 2 ** 53), exp-53
        # adjust (tmant,texp) and (mant,exp) to a common exponent
        if texp < exp:
            mant <<= exp - texp
            exp = texp
        elif texp > exp:
            tmant <<= texp - exp
            texp = exp
        # now with a common exponent, the mantissas can be summed directly
        tmant += mant
    return ldexp(float(str(tmant)), texp)


from random import random, normalvariate, shuffle

def test(nvals):
    for j in xrange(1000):
        vals = [7, 1e100, -7, -1e100, -9e-20, 8e-20] * 10
        vals.extend([random() - 0.49995 for i in xrange(nvals)])        
        vals.extend([normalvariate(0, 1)**7 for i in xrange(nvals)])
        s = sum(vals)
        for i in xrange(nvals):
            v = normalvariate(-s, random())
            s += v
            vals.append(v)
        shuffle(vals)
        assert msum(vals) == dsum(vals) == lsum(vals)
        print '.',
    print 'Tests Passed' 

if __name__ == '__main__':
    test(50)
