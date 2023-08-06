'''
Numpy wrapper functions

To extend the functionality of the units system, this module
wraps any numpy function that hasn't already been defined by
the Brian units system so that it will work with dimensionless
quantity arrays, and will return arrays rather than qarrays.

Both numpy and scipy functions are wrapped, with scipy versions
given preference over numpy versions.
Behaviour defined by Brian comes from the following sources:

* unitsafefunctions module: any names in this are not wrapped
* ufuncs: any known ufunc implemented in quantityarray should not
  be wrapped, this is defined by the variable
  quantityarray.known_ufuncs.
* qarray methods: any method implemented specifically by
  qarray should not be wrapped (e.g. mean, std, var).

In addition, any numpy/scipy function with 'array' in its name
is not wrapped (e.g. array and asarray).
'''

import quantityarray
from numpy import *
from scipy import *
import numpy
from log import *

__all__ = []

unitsafefunctions_ns = {}
exec 'from brian.unitsafefunctions import *' in unitsafefunctions_ns

numpy_scipy_ns = {}
exec 'from numpy import *' in numpy_scipy_ns
exec 'from scipy import *' in numpy_scipy_ns

excluded_set = set()
excluded_set.update(set(unitsafefunctions_ns.keys()))
excluded_set.update(set(f.__name__ for f in quantityarray.known_ufuncs))
excluded_set.update(set(n for n in numpy_scipy_ns.keys() if hasattr(quantityarray.qarray,n) and hasattr(getattr(quantityarray.qarray,n),'im_class') and getattr(quantityarray.qarray,n).im_class is quantityarray.qarray))
excluded_set.update(set(k for k in numpy_scipy_ns.keys() if 'array' in k))

def must_be_unitless(x):
    if isinstance(x,quantityarray.qarray):
        if not quantityarray.has_consistent_dimensions(x,1):
            raise ValueError, 'Numpy wrapped function arguments must be dimensionless'
        log_warn('brian.numpywrappers','Values returned by numpy wrapped functions are arrays not qarrays')
        x = numpy.asarray(x)
    return x

def add_knowledge_of_qarray(f):
    def new_f(*args,**kwds):
        args = [ must_be_unitless(x) for x in args ]
        kwds = dict((k, must_be_unitless(v)) for k, v in kwds)
        return f(*args,**kwds)
    new_f.__name__ = f.__name__
    new_f.__doc__ = f.__doc__
    return new_f

added_knowledge = []
for varname, varval in numpy_scipy_ns.iteritems():
    if callable(varval) and varname not in excluded_set and hasattr(varval,'__name__'):
        exec varname + '=add_knowledge_of_qarray(' + varname+ ')'
        added_knowledge.append(varname)
        __all__.append(varname)

if __name__ == '__main__':
    for k in excluded_set:
        print k