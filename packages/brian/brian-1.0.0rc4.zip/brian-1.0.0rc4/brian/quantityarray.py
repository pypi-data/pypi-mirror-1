# ----------------------------------------------------------------------------------
# Copyright ENS, INRIA, CNRS
# Contributors: Romain Brette (brette@di.ens.fr) and Dan Goodman (goodman@di.ens.fr)
# 
# Brian is a computer program whose purpose is to simulate models
# of biological neural networks.
# 
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use, 
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info". 
# 
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability. 
# 
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security. 
# 
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
# ----------------------------------------------------------------------------------
# 
"""
Module that defines the QuantityArray class
"""

#Things still to do
#------------------
#
#* Improve efficiency (within the confines of the current structure)
#* Implement more ufuncs (see newquantityarray.txt)
#* Check that the n-D stuff works as expected
#* Rewrite the interface
#
#A more long term goal would be to rewrite according to the
#alternative qarray design described in alternative_qarray.txt.

from brian_unit_prefs import bup
import numpy
from numpy import *
from units import *
import unitsafefunctions
from operator import isSequenceType, isNumberType
from __builtin__ import all # note that the NumPy all function doesn't do what you'd expect
import warnings
from log import *
import weakref
from itertools import izip

__all__ = [ 'QuantityArray', 'qarray', 'has_consistent_dimensions', 'safeqarray']

def _define_and_test_interface(self):
    """
    Initialisation
    ~~~~~~~~~~~~~~
    
    A :class:`QuantityArray` can be initialised with a list, tuple, NumPy array,
    numeric type, :class:`Quantity` or :class:`QuantityArray` object. It will initialise
    with values which are not :class:`Quantity` objects or containers of them,
    and should work with these, but this is not guaranteed. At the moment,
    we only guarantee that 1d arrays will work as expected, although
    nd arrays should also work (but may have bugs).
    
    Arithmetical operations
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    All arithmetical operations should work as with NumPy arrays
    except with unit consistency checking.
    
    Casting
    ~~~~~~~
    
    Implicit casting works according to the rule:
    
        :class:`QuantityArray` op other = :class:`QuantityArray`
    
    where other is upcast to :class:`QuantityArray`.
    
    Explicit casting can be done by writing:: 
    
        asarray(x)

    Functions
    ~~~~~~~~~
    
    The following NumPy functions are guaranteed to work as expected:

        mean, std, var, trigonometric functions, sqrt, exp, log
        
    """
    
    import operator
    from utils.approximatecomparisons import is_approx_equal
    
    # check initialisation
    x = QuantityArray([1*second,2*kilogram])
    x = QuantityArray((1*second,2*kilogram))
    x = QuantityArray(array([1*second,2*kilogram],dtype=object))
    x = QuantityArray(array([1*second,2*kilogram]))
    x = QuantityArray(3)
    x = QuantityArray(3*second)
    x = QuantityArray(x)
    
    # check arithmetic
    x = QuantityArray([1*second,2*second])
    y = QuantityArray([3*second,4*second])
    z = QuantityArray([1*second,2*kilogram])
    w = x + y
    w = x - y
    w = x * y
    w = x / y
    w = x ** 2
    self.assertRaises(DimensionMismatchError,operator.add,x,z)
    
    # check casting
    x = QuantityArray([1*second,2*second])
    y = array([3,4])
    z = 5
    w = 5*second
    self.assert_(isinstance(x*y,QuantityArray))
    self.assert_(isinstance(y*x,QuantityArray))
    self.assert_(isinstance(x*z,QuantityArray))
    self.assert_(isinstance(x+w,QuantityArray))
    
    # check functions
    funcs = [ mean, std, var, sin, cos, tan, sqrt, exp, log ]
    x = QuantityArray([1*second,2*second])
    x = x/second
    for f in funcs:
        y = f(x)
    # check that these functions raise expected errors
    x = QuantityArray([1*second,2*kilogram])
    funcs = [ mean, std, var, sin, cos, tan, exp, log ]
    for f in funcs:
        self.assertRaises(DimensionMismatchError,f,x)
        
    # check explicit casting
    x = QuantityArray([1*second,2*kilogram])
    ax = asarray(x)
    for xi, axi in zip(x,ax):
        self.assert_(is_approx_equal(float(xi),axi))

def varobjarray_method(name,nargs,makeview=True):
    '''
    See explanation in varobjarray class
    
    This function factory probably contributes to the inefficiency of the qarray class,
    and when the behaviour is more stable could be replaced with a more efficient version.
    '''
    orig_func = getattr(numpy.ndarray,name)
    def f(self,*args):
        assert len(args)==nargs
        if len(args):
            # functions are called as func(self,...,val) e.g. ...=i,j for setslice
            val = args[-1]
            if not isSequenceType(val):
                val = array([val],dtype=object) # otherwise numpy arrays treat val as a float
            elif isinstance(val,numpy.ndarray):
                val = asarray(val) # derived classes converted back to numpy arrays
            else:
                val = array(val,dtype=object) # val is a container so this is OK
            args = args[:-1] + (val,)
        x = orig_func(asarray(self),*args)
        if makeview: # not every function returns an object of the original type
            x = x.view(self.__class__)
        return x        
    f.__name__ = orig_func.__name__
    f.__doc__ = orig_func.__doc__
    if hasattr(orig_func,'__dict__'):
        f.__dict__.update(orig_func.__dict__)
    return f

class varobjarray(numpy.ndarray):
    '''
    Variant object array, fixes some problems with numpy array of objects derived from float
    
    A numpy array of dtype=object doesn't behave exactly as you'd expect, in particular
    it often treats objects derived from float as if they were just floats. The function
    factory varobjarray_method redefines this behaviour by replacing operations involving
    a scalar with a 1-d array consisting of just that scalar, which fixes this problem.
    '''
    def __new__(cls,data):
        return array(data,dtype=object).view(cls)
    __setslice__ = varobjarray_method('__setslice__',3,makeview=False)
    __setitem__ = varobjarray_method('__setitem__',2,makeview=False)
    __neg__ = varobjarray_method('__neg__',0)    
    __pos__ = varobjarray_method('__pos__',0)
    __abs__ = varobjarray_method('__abs__',0)
    __mul__ = varobjarray_method('__mul__',1)
    __rmul__ = varobjarray_method('__rmul__',1)
    __div__ = varobjarray_method('__div__',1)
    __rdiv__ = varobjarray_method('__rdiv__',1)
    __truediv__ = varobjarray_method('__truediv__',1)
    __rtruediv__ = varobjarray_method('__rtruediv__',1)
    __add__ = varobjarray_method('__add__',1)
    __radd__ = varobjarray_method('__radd__',1)
    __pow__ = varobjarray_method('__pow__',1)
    __rpow__ = varobjarray_method('__rpow__',1)
    __sub__ = varobjarray_method('__sub__',1)
    __rsub__ = varobjarray_method('__rsub__',1)
    __lt__ = varobjarray_method('__lt__',1,makeview=False)
    __le__ = varobjarray_method('__le__',1,makeview=False)
    __gt__ = varobjarray_method('__gt__',1,makeview=False)
    __ge__ = varobjarray_method('__ge__',1,makeview=False)
    __eq__ = varobjarray_method('__eq__',1,makeview=False)
    __ne__ = varobjarray_method('__ne__',1,makeview=False)

class unitarray(varobjarray):
    '''
    Array of differing units
    
    Essentially just an array of dtype=object, with the behaviours defined in
    varobjarray, and some additional ones. At initialisation, numbers are normalised
    (see __new__), setting items and slices differs slightly from the situation in
    varobjarray because setting an element of an array as an array can be done if
    dtype=object (i.e. it points to the array). Actually, not clear that this is
    properly dealt with, but it seems to work (maybe inefficient?). Finally, some
    operations are undefined for unit arrays (such as addition).
    '''
    def __new__(cls,data):
        x = array(data,dtype=object)
        # we normalise (i.e. just take the unit part)
        shape = x.shape
        x = x.flatten()
        for i in xrange(len(x)):
            x[i]=get_unit_fast(x[i])
        x = x.reshape(shape)
        x = x.view(cls)
        return x
    def define_new_shape_parent(self, shape_parent):
        #Just here for compatibility with homog_unitarray
        pass
    def __setitem__(self,i,val):
        if not isSequenceType(val):
            val = array([val],dtype=object)
            val.shape = ()
        elif isinstance(val,homog_unitarray):
            val = asarray(val)
            val.shape = ()
        elif isinstance(val,numpy.ndarray):
            val = asarray(val)
        else:
            val = array(val,dtype=object)
        numpy.ndarray.__setitem__(asarray(self),i,val)        
    def __setslice__(self,i,j,val):
        if not isSequenceType(val):
            val = array([val],dtype=object) # array(val,dtype=object) doesn't work if val derived from float
            val.shape = () # otherwise element = [val] instead of element = val
        elif isinstance(val,homog_unitarray):
            val = asarray(val)
            val.shape = ()
        elif isinstance(val,numpy.ndarray):
            val = asarray(val)
        else:
            val = array(val,dtype=object)
        numpy.ndarray.__setslice__(asarray(self),i,j,val)        
    # The following methods derive their behaviour from varobjarray
    #__mul__, __rmul__
    #__div__, __rdiv__
    #__truediv__, __rtruediv__
    #__pow__, __rpow__
    # The following methods are not meaningful for a unitarray, and
    # so should raise an error
    def __notimplemented(self,*args):
        raise ValueError('Operation not meaningful for unitarray')
    __neg__ = __notimplemented    
    __pos__ = __notimplemented
    __abs__ = __notimplemented
    __add__ = __notimplemented
    __radd__ = __notimplemented
    __sub__ = __notimplemented
    __rsub__ = __notimplemented
    __lt__ = __notimplemented
    __le__ = __notimplemented
    __gt__ = __notimplemented
    __ge__ = __notimplemented
    __eq__ = __notimplemented
    __ne__ = __notimplemented

# TODO: this factory function needs work (docstrings, signature)
def homog_unitarray_method(name):
    '''
    Same as the varobjarray version but we also keep track of the shape_parent
    and the downgradable variable, and we only need to deal with the args=1 case.
    '''
    orig_func = getattr(numpy.ndarray,name)
    def f(self,val):
        if not isSequenceType(val):
            val = array([val],dtype=object)
        if isinstance(val,numpy.ndarray):
            val = asarray(val)
        else:
            val = array(val,dtype=object)
        x = orig_func(asarray(self),val)        
        x = x.view(self.__class__)
        x.shape_parent = self.shape_parent
        x.downgradable = False
        return x        
    return f    

class homog_unitarray(numpy.ndarray):
    '''
    Homogeneous array of units
    
    A simulated array of sorts. It's actually just a 1-d array with dtype=object
    and a single value - this works with the arithmetic operations when combined
    with unitarray. However, it has a 'shape_parent' whose shape it is simulating,
    and when it is downcast to a non-homogeneous unit array, it assumes this shape.
    '''
    def __new__(cls,unit,shape_parent,downgradable=True):
        x = numpy.ndarray.copy(array([unit],dtype=object).view(cls))
        # Note that originally shape_parent was a copy of the parent ndarray object,
        # but this introduced cyclical references and memory leaks, therefore we only
        # store a copy of the shape of the parent now, but this also causes problems
        # because it is non-trivial to work out what the shape of a __getitem__ or
        # __getslice__ object should be.
        # Regarding cyclical references, in principle Python
        # 2.5 handles this OK, but possibly the interaction with NumPy causes problems.
        # reference: http://www.nightmare.com/medusa/memory-leaks.html
        x.shape_parent = shape_parent#weakref.ref(shape_parent)
        x.downgradable = downgradable
        return x
    def define_new_shape_parent(self, shape_parent):
        self.shape_parent = shape_parent
    def copy(self):
        return homog_unitarray(self.get_const(),self.shape_parent,self.downgradable)
    def _convert_to_unitarray(self):
        '''
        Downcast to non-homogeneous unit array if it can be done
        '''
        if not self.downgradable:
            raise ValueError('Cannot downgrade array')
        val = self.get_const()
        shape_parent = self.shape_parent
        self.__class__ = unitarray
        # refcheck=False because otherwise cannot resize data when there
        # are multiple references to same object, here self and the the
        # _units object of the qarray
        self.resize(size(shape_parent),refcheck=False)
        self.fill(val)
        self.shape = shape_parent
    def get_const(self):
        return super(homog_unitarray,self).__getitem__(0)
        #return self.item()
    def asunitarray(self):
        x = numpy.empty(self.shape_parent,dtype=object)
        x.fill(self.get_const())
        return x.view(unitarray)
    def __getitem__(self,i):
        # we don't have to track the shape parent because homog_unitarray.__getitem__ should
        # only ever be called by qarray.__getitem__ which itself calls qarray(x,units=u) where
        # x is the new ndarray, and u is _units[i]. This works because the qarray constructor
        # can handle being passed a Quantity rather than a unitarray as the units.
        return self.get_const()
#        # we have to track the shape parent
#        #item = self.shape_parent[i]
#        u = self.get_const()
#        #if isinstance(item,numpy.ndarray):
#        newitem = homog_unitarray(u,self.shape_parent,downgradable=False) # NOTE: the method that called __getitem__ must upgrade the shape_parent itself
#        if size(newitem)==1:
#            newitem = u
#        return newitem
        
        ##return u
    def __setitem__(self,i,val):
        # do nothing if the new values are consistent with the old
        if consistent(self[i],val):
            return
        # otherwise we have to downgrade
        self._convert_to_unitarray()
        self.__setitem__(i,val)
    # slice behaviour covered by item behaviour
    def __getslice__(self,i,j):
        return self.__getitem__(slice(i,j))
    def __setslice__(self,i,j,val):
        self.__setitem__(slice(i,j),val)
    def reshape(self, *args):
        return self
    def __str__(self):
        return str(self.asunitarray())
    __mul__ = homog_unitarray_method('__mul__')
    __rmul__ = homog_unitarray_method('__rmul__')
    __div__ = homog_unitarray_method('__div__')
    __rdiv__ = homog_unitarray_method('__rdiv__')
    __truediv__ = homog_unitarray_method('__truediv__')
    __rtruediv__ = homog_unitarray_method('__rtruediv__')
    __pow__ = homog_unitarray_method('__pow__')
    __rpow__ = homog_unitarray_method('__rpow__')
    # The following methods are not meaningful for a unitarray, and
    # so should raise an error
    def __notimplemented(self,*args):
        raise ValueError('Operation not meaningful for homog_unitarray')
    __neg__ = __notimplemented    
    __pos__ = __notimplemented
    __abs__ = __notimplemented
    __add__ = __notimplemented
    __radd__ = __notimplemented
    __sub__ = __notimplemented
    __rsub__ = __notimplemented
    __lt__ = __notimplemented
    __le__ = __notimplemented
    __gt__ = __notimplemented
    __ge__ = __notimplemented
    __eq__ = __notimplemented
    __ne__ = __notimplemented


class QuantityArray(numpy.ndarray):
    '''
    Array of quantities with physical dimensions
    
    The implementation and syntax of the :class:`QuantityArray` class are subject to
    change in future releases of Brian. We are planning a new system with
    better and more transparent integration with numpy, and more efficient.
    
    For the moment, initialise a :class:`QuantityArray` as with a numpy array::
    
        QuantityArray(data)
    
    Mostly, a :class:`QuantityArray` object should should just work as you would
    hope:
    
    * Arithmetical operations with other arrays, scalars or :class:`Quantity` objects
    * Numpy functions such as ``var``, ``std``, ``mean``, etc. return arrays
      with the correct units or raise :exc:`DimensionMismatchError` exceptions.
    * Slicing, element setting and extraction, etc. work as you would expect.
    
    One thing to note is that there are two internal representations of a
    :class:`QuantityArray`, with and without homogeneous units. If all quantities
    have the same physical dimensions, just one copy of those dimensions is
    stored and operations are much faster than if different elements of
    the array have different units. In the latter case, the :class:`QuantityArray`
    pretty much just reduces to a numpy array with ``dtype=object`` and is
    horrendously slow for anything other than fairly tiny calculations.
    
    Changing the physical dimensions of an element of an array with homogeneous units
    will transparently change it to an array with nonhomogeneous units, but
    this will signficantly impact performance. If you know that you won't be
    changing units, use the ``safeqarray`` function to create your array
    object instead. The created array will then raise an exception if you
    try to make the units nonhomogeneous.
    '''
    def _units_get(self):
        if not hasattr(self,'_realunits'):
            self._realunits = homog_unitarray(1,self.shape,downgradable=True)
            self._realunits_implied = True
        return self._realunits
    def _units_set(self, u):
        self._realunits = u
    _units = property(fget=_units_get, fset=_units_set)
    def __new__(subtype, arr, units=None, copy=False, allowunitchanges=True):
        x = numpy.array(arr,copy=copy,dtype=float).view(subtype)
        x._allowunitchanges = allowunitchanges
        return x
    def copy(self):
        return qarray(self,copy=True)
    def __init__(self, arr, units=None, copy=False, allowunitchanges=True):
        # first check, are units given?
        if units is not None:
            unitset = unique_units(units)
            if len(unitset)==1:
                units = homog_unitarray(get_unit_fast(unitset[0]),self.shape,downgradable=True)
            else:
                units = unitarray(units)
                if units.shape!=self.shape:
                    raise ValueError('Units array has a different shape to numerical array')
            self._units = units
            return 
        # case 1, arr is a qarray, easy
        if isinstance(arr,QuantityArray):
            if copy:
                self._units = arr._units.copy()
            else:
                self._units = arr._units
            return
        # case 2, arr is is a numpy array
        if isinstance(arr,numpy.ndarray):
            if arr.dtype==object:
                unitset = unique_units(arr)
                if len(unitset)==1:
                    units = homog_unitarray(get_unit_fast(unitset[0]),self.shape,downgradable=True)
                else:
                    units = unitarray(arr)
                self._units = units
            else:
                self._units = homog_unitarray(1.,self.shape,downgradable=True)
            return
        # case 3, arr is a Quantity
        if isinstance(arr,Quantity):
            self._units = homog_unitarray(get_unit_fast(arr),self.shape,downgradable=True)
            return
        # case 4, arr is another scalar type
        if not isSequenceType(arr):
            self._units = homog_unitarray(1.,self.shape,downgradable=True)
        # case 5, arr is another container type (list, tuple)
        unitset = unique_units(arr)
        if len(unitset)==1:
            units = homog_unitarray(get_unit_fast(unitset[0]),self.shape,downgradable=True)
        else:
            units = unitarray(arr)
        self._units = units            
    def __array_wrap__(self,obj,context=None):
        handled = False
        x = numpy.ndarray.__array_wrap__(self,obj,context)
        if not hasattr(x,'_units') or hasattr(x,'_realunits_implied'):
            x._units = self._units
            del x._realunits_implied
        if not hasattr(x,'_allowunitchanges'):
            x._allowunitchanges = self._allowunitchanges
        if context is not None:
            ufunc = context[0]
            args = context[1]
            if ufunc is numpy.multiply:
                handled=True
                x._units = self._otherunits(args[0]) * self._otherunits(args[1])
            elif ufunc in ufuncs_consistent:
                handled = True
                mismatch = False
                if not consistent_dimensions(args[0],args[1]):
                    mismatch = True
                    # Comparisons with 0 or 0. shouldn't check dimensions
                    if ufunc in ufuncs_comparisons:
                        if is_scalar_type(args[0]) and not isinstance(args[0],Quantity) and (args[0]==0 or args[0]==0.):
                            mismatch = False
                        if is_scalar_type(args[1]) and not isinstance(args[1],Quantity) and (args[1]==0 or args[1]==0.):
                            mismatch = False
                if mismatch:
                    raise DimensionMismatchError(ufunc.__name__,*(unique_units(args[0])+unique_units(args[1])))
            elif ufunc is numpy.divide:
                handled=True
                x._units = self._otherunits(args[0]) / self._otherunits(args[1])
            elif ufunc in ufuncs_dimensionless:
                handled=True
                if not consistent(args[0],1.):
                    raise DimensionMismatchError(ufunc.__name__,*unique_units(args[0]._units))
            elif ufunc in ufuncs_passthrough:
                handled=True
            elif ufunc is numpy.sqrt:
                handled=True
                x._units = self._units ** 0.5
            elif ufunc is numpy.square:
                handled=True
                x._units = self._otherunits(args[0]) ** 2
            elif ufunc is numpy.power:
                handled=True
                x._units = self._otherunits(args[0]) ** args[1]
                
            if ufunc in ufuncs_output_notqarray:
                x = obj
        if not handled:
            if context is not None:
                s=context[0].__name__
                #warnings.warn("QuantityArray doesn't know about operation "+s+", units may not work correctly.")
            else:
                s='(no context given)'
                ## currently no warning if no context is given...
            log_warn('brian.qarray', "QuantityArray doesn't know about operation "+s+", units may not work correctly.")
        return x
    def __getitem__(self,i):
        # behaviour defined by numpy array and unit array
        x = numpy.ndarray.__getitem__(self,i)
        u = self._units[i]
        #if not isinstance(u,Quantity):
        #    u.define_new_shape_parent(x.shape)
        # nd getitem can return an array or a value
        if isinstance(x,numpy.ndarray):
            return qarray(x,units=u)
        #if isinstance(u,homog_unitarray):
        #    u = u.get_const()
        return x*u
    def __setitem__(self,i,val):
        if self._allowunitchanges or consistent(self._units[i],val):
            if not isinstance(val,QuantityArray):
                val = qarray(val)
            self._units[i] = val._units
            numpy.ndarray.__setitem__(self,i,val)
        else:
            raise DimensionMismatchError('Attempted to change item to one with inconsistent dimensions',unique_units(self._units[i]),unique_units(val))
    def __getslice__(self,i,j):
        return self[slice(i,j)]
#        # note that numpy.ndarray.__getslice__ returns an object with the same class, presumably
#        # this was done to make subclassing ndarray easier, which is great for us here as it means
#        # we don't have to initialise a whole new object, just add _units to it. Note though that if
#        # we do anything more complicated in __init__ than creating _units then this might need to
#        # change
#        newarr = numpy.ndarray.__getslice__(self,i,j)
#        newarr._units = self._units[i:j]
#        newarr._units.define_new_shape_parent(newarr.shape)
#        newarr._allowunitchanges = self._allowunitchanges
#        return newarr
    def __setslice__(self,i,j,vals):
        # this falls back on the setitem method
        self[slice(i,j)]=vals
    def __str__(self):
        return str(asarray(self,dtype=object)*asarray(self._units,dtype=object))
    def __repr__(self):
        return 'qarray('+str(self)+')'
    def _otherunits(self,other):
        # parsing function creates an appropriate (non)homog_unitarray depending on whether other is
        # a quantityarray, number of numpyarray
        if isinstance(other,QuantityArray): otherunits = other._units
        elif isinstance(other,numpy.ndarray): otherunits = homog_unitarray(1.,other.shape)
        elif not isSequenceType(other): otherunits = homog_unitarray(get_unit_fast(other),(1,))
        else:
            otherunits = qarray(other)._units
        return otherunits
    #### STILL TO IMPLEMENT? ####################################
#    def __eq__(self,other):
#    def __ne__(self,other):
    #### OTHER NUMERICAL METHODS
    def _insist_homogeneous_units(self,name):
        unitset = unique_units(self._units)
        if len(unitset)>1:
            raise DimensionMismatchError(name,*unitset)
        return unitset[0]
    def _give_homogeneous_units(self,y,unit):
        if isinstance(y,numpy.ndarray):
            y = y.view(self.__class__)
            y._units = homog_unitarray(unit,y.shape)
        else:
            y = y * unit
        return y
    def mean(self,*args,**kwds):
        u = self._insist_homogeneous_units('mean')
        y = numpy.ndarray.mean(asarray(self),*args,**kwds)
        return self._give_homogeneous_units(y,u)                
    def std(self,*args,**kwds):
        u = self._insist_homogeneous_units('std')
        y = numpy.ndarray.std(asarray(self),*args,**kwds)
        return self._give_homogeneous_units(y,u)                
    def var(self,*args,**kwds):
        u = self._insist_homogeneous_units('var')
        y = numpy.ndarray.var(asarray(self),*args,**kwds)
        return self._give_homogeneous_units(y,u**2)
    def cumsum(self,*args,**kwds):
        u = self._insist_homogeneous_units('cumsum')
        y = numpy.ndarray.cumsum(asarray(self),*args,**kwds)
        return self._give_homogeneous_units(y,u)
    def sum(self,*args,**kwds):
        u = self._insist_homogeneous_units('sum')
        y = numpy.ndarray.sum(asarray(self),*args,**kwds)
        return self._give_homogeneous_units(y,u)
    def max(self,*args,**kwds):
        u = self._insist_homogeneous_units('max')
        y = numpy.ndarray.max(asarray(self),*args,**kwds)
        return self._give_homogeneous_units(y,u)
    def argmax(self,*args,**kwds):
        u = self._insist_homogeneous_units('argmax')
        y = numpy.ndarray.argmax(asarray(self),*args,**kwds)
        return y
    def argmin(self,*args,**kwds):
        u = self._insist_homogeneous_units('argmin')
        y = numpy.ndarray.argmin(asarray(self),*args,**kwds)
        return y
    def argsort(self,*args,**kwds):
        u = self._insist_homogeneous_units('argsort')
        y = numpy.ndarray.argsort(asarray(self),*args,**kwds)
        return y
    def nonzero(self,*args,**kwds):
        u = self._insist_homogeneous_units('nonzero')
        y = numpy.ndarray.nonzero(asarray(self),*args,**kwds)
        return y
    def transpose(self):
        return qarray(array(self).transpose(), units=self._units.transpose())
    def reshape(self, *args):
        u = self._units.reshape(*args)
        return qarray(array(self).reshape(*args), units=u)
    def _T(self):
        return qarray(array(self).T, units = self._units.T)
    T = property(fget=_T)
    # makes quantityarray picklable
    def __reduce__(self):
        if isinstance(self._units, homog_unitarray):
            return (qarray, (array(self), self._units.get_const(), False, self._allowunitchanges))
        else:
            return (qarray, (array(self), array(self._units,dtype=object), False, self._allowunitchanges))


# TODO: this function is very inefficient
def consistent(*args):
    if len(args)<2:
        return True
    if len(args)==2:
        a, b = args
        nonsequence = True
        # treat array with homogeneous units as scalar
        if isinstance(a,qarray) and isinstance(a._units,homog_unitarray):
            a = a._units.get_const()
        if isinstance(b,qarray) and isinstance(b._units,homog_unitarray):
            b = b._units.get_const()
        if isSequenceType(a):
            if size(a)>1:
                a = qarray(a)
                nonsequence = False
            else:
                try:
                    a = a[0]
                except IndexError:
                    a = a.item()
        if isSequenceType(b):
            if size(b)>1:
                b = qarray(b)
                nonsequence = False
                a, b = b, a # ensure that if either a or b is an array, then a is an array
            else:
                try:
                    b = b[0]
                except IndexError:
                    b = b.item()
        if nonsequence: # both are scalars
            return have_same_dimensions(a,b)
        if not isSequenceType(b): # a sequence type, b scalar
            u = unique_units(a)
            if len(u)==0 or have_same_dimensions(u[0],b):
                return True
            return False
        # otherwise: a, b both sequences, must have same shape (but this will be taken care of by other functions)
        for x, y in izip(a.flat,b.flat):
            if not have_same_dimensions(x,y):
                return False
        return True
    start = args[0]
    for next in args[1:]:
        if not consistent(start,next):
            return False
    return True

# UFUNC SETS: quick way of defining unit behaviours
# Consistent: two argument functions where both sides must be consistent
# Dimensionless: one argument functions which have to be unitless
# Passthrough: default behaviour is fine
# Output not qarray: e.g. x<10 should return array of bools
# NOTE: screwy behaviour of == and !=, they seem to just check
# if the objects are identical, not only that but despite
# passing through __array_wrap__ they seem to cancel out any
# exceptions raised by it!! Why? I have no idea.
# TODO: find out all the other ufuncs and implement them
ufuncs_consistent = set([numpy.add, numpy.subtract, numpy.greater, numpy.equal,
                         numpy.not_equal,numpy.greater_equal,numpy.less,
                         numpy.less_equal])
ufuncs_dimensionless = set([numpy.arccos, numpy.arccosh, numpy.arcsin,
                            numpy.arcsinh, numpy.arctan, numpy.arctanh,
                            numpy.cos, numpy.cosh, numpy.tan, numpy.tanh,
                            numpy.log10, numpy.sin, numpy.sinh, numpy.exp,
                            numpy.log, numpy.ceil, numpy.floor, numpy.rint])
ufuncs_passthrough = set([numpy.abs,numpy.negative,numpy.ones_like, numpy.zeros_like, numpy.empty_like])
ufuncs_output_notqarray = set([numpy.greater,numpy.equal,numpy.not_equal,
                               numpy.greater_equal,numpy.less,numpy.less_equal])
ufuncs_comparisons = set([numpy.greater,numpy.equal,numpy.not_equal,
                               numpy.greater_equal,numpy.less,numpy.less_equal])

known_ufuncs = ufuncs_consistent | ufuncs_dimensionless | ufuncs_passthrough | ufuncs_output_notqarray

consistent_dimensions = consistent
has_consistent_dimensions = consistent_dimensions

qarray=QuantityArray

def safeqarray(*args,**kwds):
    '''
    Return a :class:`QuantityArray` where the units cannot be changed.
    
    Attempts to change the value of an element of the array to one
    with different physical dimensions will raise a
    :exc:`DimensionMismatchError` exception.
    '''
    kw = {'allowunitchanges':False}
    kw.update(kwds)
    return qarray(*args,**kw)

def unique_units(x):
    if isinstance(x,Quantity):
        return [get_unit_fast(x)]
    if isinstance(x,qarray):
        return unique_units(x._units)
    if isinstance(x,numpy.ndarray) and x.dtype==float:
        return [1.]
    x = asarray(x,dtype=object).flatten()
    return [Quantity.with_dimensions(1.,dim) for dim in set(tuple(get_dimensions(_)._dims) for _ in x)]

# Remove all units
if not bup.use_units:
    def QuantityArray(arr, units=None, copy=False, allowunitchanges=True):
        return array(arr,copy=copy)
    qarray = QuantityArray
    safeqarray = qarray
    def consistent(*args):
        return True
    consistent_dimensions = consistent
    has_consistent_dimensions = consistent

if __name__=='__main__':
    def info(x):
        s = '---------- info ----------\n'
        s += str(x)
        if isinstance(x,numpy.ndarray):
            s += '\nUnderlying array:\n'
            s += str(asarray(x))
        s += '\n~~  class = ' + x.__class__.__name__
        if hasattr(x,'_units'):
            s += '\n~~  units type = ' + x._units.__class__.__name__
            if isinstance(x._units,homog_unitarray):
                s += '\n~~  constant unit value = ' + str(x._units.get_const())
        return s
    
    x = qarray([[1,2],[3,4]],kilogram)
    print info(x)
    print info(x.copy())
    x._units._convert_to_unitarray()
    print info(x)
    
    
#    x = qarray([[1,2,3],[-1,-2,-3]],kilogram)
#    print info(x)
#    x[[]]=4*kilogram
#    print info(x)
    
#    w = safeqarray([[1*kilogram,2*kilogram],[3*kilogram,4*kilogram]])
#    print info(w)
#    w[0]=1*second

    # array float = 5.7s
    # array object int = 76s
    # array object Quantity = 7 hours (projected)
    # qarray homog = 74s
    # qarray nonhomog = 7 hours (projected)
    # single quantity = 26s
    # single array object quantity = 37s
    # do nothing class derived from numpy.ndarray, 1000 elems = 10s 
    # do nothing class derived from numpy.ndarray, 1 elem = 7.4s 

    #a = array(range(1000),dtype=float)
    #a = qarray(range(1000),1*kilogram)
    #a._units._convert_to_unitarray()
    #a = array([1*kilogram for _ in range(1000)],dtype=object)
    #print a._units.__class__
    #a = 3*kilogram
    #a = array([3*kilogram],dtype=object)
    
#    class Farray(numpy.ndarray):
#        def __new__(cls,data):
#            return array(data,dtype=float).view(cls)
#    
#    a = Farray(range(1))
#    
#    import time
#    t = time.time()
#    for _ in xrange(1000000):
#        b = a * a
#    print time.time()-t
