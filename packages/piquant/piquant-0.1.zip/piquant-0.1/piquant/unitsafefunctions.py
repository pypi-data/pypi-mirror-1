"""
Functions which check the dimensions of their arguments, etc.

Functions updated to provide Quantity functionality
---------------------------------------------------

With any dimensions:

* sqrt

Dimensionless:

* log, exp
* sin, cos, tan
* arcsin, arccos, arctan
* sinh, cosh, tanh
* arcsinh, arccosh, arctanh

With homogeneous dimensions:

* dot

Functions updated to return QuantityArray instead of numpy array
----------------------------------------------------------------

* ones, zeros, empty, tri, eye, identity
* linspace, logspace
* arange
* beta, random_sample, uniform, standard_normal
* rand, randn, vonmises, weibull, gumbel
"""

from piquant_unit_prefs import bup
from units import *
import quantityarray
import numpy, math, scipy
from numpy import *
from numpy.random import *
import inspect

def _define_and_test_interface(self):
    """
    Each of the following functions f(x) should use units if they are passed a
    :class:`Quantity` or :class:`QuantityArray` object or fall back on their numpy versions
    otherwise.
    
        sqrt, log, exp, sin, cos, tan, arcsin, arccos, arctan,
        sinh, cosh, tanh, arcsinh, arccosh, arctanh
    
    Each of these numpy functions should return a :class:`qarray` formed from the
    numpy original:

    * ones, ones_like, zeros, zeros_like, empty, empty_like
    * linspace, logspace
    * arange
    * beta, random_sample, uniform, standard_normal
    * rand, randn, vonmises, weibull, gumbel

    """
    from quantityarray import QuantityArray
    
    # check sqrt behaves as expected
    x = 3*second
    y = QuantityArray([3*second,2*second])
    z = numpy.array([3.,2.])
    self.assert_(have_same_dimensions(sqrt(x),second**0.5))
    self.assert_(isinstance(sqrt(y),QuantityArray))
    self.assert_(have_same_dimensions(sqrt(y)[0],second**0.5))
    self.assert_(isinstance(sqrt(z),numpy.ndarray))
    
    # check the return types are right for all other functions
    x = 0.5*second/second
    y = QuantityArray([0.5*second,0.4*second])/second
    funcs = [
        sqrt, log, exp, sin, cos, tan, arcsin, arccos, arctan,
        sinh, cosh, tanh, arcsinh, arccosh, arctanh
            ]
    for f in funcs:
        self.assert_(isinstance(f(x),Quantity))
        self.assert_(isinstance(f(y),QuantityArray))
        self.assert_(isinstance(f(z),numpy.ndarray))

    # check that attempting to use these functions on something with units fails
    funcs = [
        log, exp, sin, cos, tan, arcsin, arccos, arctan,
        sinh, cosh, tanh, arcsinh, arccosh, arctanh
            ]
    x = 3*second
    y = QuantityArray([3*second,2*second])
    for f in funcs:
        self.assertRaises(DimensionMismatchError,f,x)
        self.assertRaises(DimensionMismatchError,f,y)

    funcs_and_args = [
             ((ones,zeros,empty,arange,random_sample,rand,randn,standard_normal,identity),(2,),QuantityArray),
             ((linspace,logspace),(1,2),QuantityArray),
             ((beta,uniform,vonmises,gumbel),(1,2),float),
             ((weibull,),(1,),float),
             ((eye,tri),(2,3,1),QuantityArray)
            ]
    for funcs, args, returntype in funcs_and_args:
        for func in funcs:
            self.assert_(isinstance(func(*args),returntype))

__all__ = []

#def must_be_unitless(x):
#    if isinstance(x,quantityarray.qarray) and not quantityarray.has_consistent_dimensions(x,1):
#        raise ValueError, 'Arguments must be dimensionless'
#    return x
#
#def add_knowledge_of_qarray(f):
#    def new_f(*args,**kwds):
#        args = [ must_be_unitless(x) for x in args ]
#        kwds = dict((k, must_be_unitless(v)) for k, v in kwds)
#        return f(*args,**kwds)
#    return new_f
#
#added_knowledge = []
#ns = {}
#exec 'from numpy import *' in ns
#for varname, varval in ns.iteritems():
#    if callable(varval):
#        exec varname + '=add_knowledge_of_qarray(' + varname+ ')'
#        added_knowledge.append(varname)
#        __all__.append(varname)

# these functions are the ones that will work with the template immediately below, and
# extend the numpy functions to know about Quantity objects (qarray dealt with automatically) 
quantity_versions = [
         'sqrt',
         'log','exp',
         'sin','cos','tan',
         'arcsin','arccos','arctan',
         'sinh','cosh','tanh',
         'arcsinh','arccosh','arctanh'
         ]

def make_quantity_version(func):
    funcname = func.__name__
    def f(x):
        if isinstance(x,Quantity):
            return getattr(x,funcname)()
        return func(x)
    f.__name__ = func.__name__
    f.__doc__ = func.__doc__
    if hasattr(func,'__dict__'):
        f.__dict__.update(func.__dict__)
    return f

for name in quantity_versions:
    if bup.use_units:
        exec name + '=make_quantity_version(' + name + ')'
    __all__.append(name)

def makeqarray_version(func):
    def f(*args,**kwds):
        x = func(*args,**kwds)
        if isinstance(x,numpy.ndarray):
            return quantityarray.qarray(x)
        return x
    f.__name__ = func.__name__
    f.__doc__ = func.__doc__
    if hasattr(func,'__dict__'):
        f.__dict__.update(func.__dict__)
    return f

numpy_to_qarray_version_functions = [
        'ones', 'zeros', 'empty', 'tri',
        'linspace', 'logspace',
        'arange',
        'beta', 'random_sample', 'uniform', 'standard_normal',
        'rand', 'randn', 'vonmises', 'weibull', 'gumbel',
        'eye', 'identity'
        ]
# not included because they return integers: binomial, poisson

for name in numpy_to_qarray_version_functions:
    if bup.use_units:
        exec name + '=makeqarray_version(' + name + ')'
    __all__.append(name)

def linspace(start, stop, num=50, endpoint=True, retstep=False):
    u = get_unit_fast(start-stop)
    return quantityarray.qarray(numpy.linspace(start, stop, num=num, endpoint=endpoint, retstep=retstep))*u

def logspace(start, stop, num=50, endpoint=True, base=10.0):
    u = get_unit_fast(start-stop)
    return quantityarray.qarray(numpy.logspace(start, stop, num=num, endpoint=endpoint, base=base))*u

def uniform(low=0.0, high=1.0, size=None):
    u = get_unit_fast(high-low)
    a = numpy.random.uniform(low, high, size=size)
    if isinstance(a,numpy.ndarray):
        a = qarray(a)
    return a * u

# TODO: support for non-homogeneous units?
__all__.append('dot')
def dot(a,b):
    if not isinstance(a,quantityarray.QuantityArray) and not isinstance(b,quantityarray.QuantityArray):
        return numpy.dot(a,b)
    if isinstance(a,quantityarray.QuantityArray):
        ua = a._insist_homogeneous_units('dot first argument must have homogeneous units')
    else:
        ua = 1.
    if isinstance(b,quantityarray.QuantityArray):
        ub = b._insist_homogeneous_units('dot second argument must have homogeneous units')
    else:
        ub = 1.
    return quantityarray.qarray(numpy.dot(array(a),array(b)))*ua*ub

if __name__=='__main__':
    print triu(zeros((3,3))).__class__