"""Util to test if two floating point numbers are equal

Use these functions for very precise tests of equality:

-- is_equal(x,y), for x=y
-- is_less_than_or_equal(x,y), for x<=y
-- is_greater_than_or_equal(x,y), for x>=y

Use these functions for less precise tests (for example, if you have done some operations on two varaibles):

-- is_approx_equal(x,y), for x=y
-- is_approx_less_than_or_equal(x,y), for x<=y
-- is_approx_greater_than_or_equal(x,y), for x>=y

The underlying mechanism is that the more precise version tests for equality using machine epsilon
precision, that is, x=y if abs(x-y)<abs(x)*epsilon where epsilon is the smallest value such that
1+epsilon>epsilon. The less precise mechanism simply uses 100*epsilon instead of epsilon.

Use this function for testing if you want to specify an absolute tolerance:

-- is_within_absolute_tolerance(x,y[,absolutetolerance])
    The default tolerance is the sqrt of epsilon, or about 1e-8 for a 64 bit float

Note also that you can use the numpy function:

-- allclose(a, b, rtol = 1e-5, atol = 1e-8)
    Where rtol is the relative tolerance, and atol is the absolute tolerance which comes into
    play when the numbers are very close to zero.

Warning: none of these functions can be guaranteed to work in the way you might
expect them to. Errors can accumulate to the point where even 100*epsilon is an inappropriate test
for approximate equality.
"""

import math

# This finds the 'machine epsilon' for the current hardware float type, the
# smallest value of epsilon so that 1+epsilon>1
epsilon = 1.
while 1. + epsilon > 1.:
    epsilon /= 2
epsilon *= 2.
# Result for 32 bit float should be: 1.1929093e-7 
# For 64 bit float should be:        2.220446049250313e-16

# This value can be used for more approximate testing
approxepsilon = epsilon * 10000

# This value is the default tolerance for medium sized numbers (used in the units class)
defaultabsolutetolerance = math.sqrt(epsilon) # 1.4901161193847656e-008 on 64 bit system

def is_equal(x,y):
    if x==y: return True
    return abs(x-y)<abs(x)*epsilon

def is_less_than_or_equal(x,y):
    return x<y or is_equal(x,y)

def is_greater_than_or_equal(x,y):
    return x>y or is_equal(x,y)

def is_approx_equal(x,y):
    if x==y: return True
    return abs(x-y)<abs(x)*approxepsilon

def is_approx_less_than_or_equal(x,y):
    return x<y or is_approx_equal(x,y)

def is_approx_greater_than_or_equal(x,y):
    return x>y or is_approx_equal(x,y)

def is_within_absolute_tolerance(x,y,absolutetolerance=defaultabsolutetolerance):
    return float(abs(x-y))<absolutetolerance
