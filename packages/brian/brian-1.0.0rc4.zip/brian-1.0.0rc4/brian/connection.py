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
__all__=['Connection','IdentityConnection','MultiConnection']

import copy
from itertools import izip
from random import sample
import bisect
from units import *
import types
import magic
from buganalyser import *
from log import *
from numpy import *
from scipy import sparse,stats,rand,weave,linalg
    
#TODO: connect -> setitem

class ConnectionMatrix(object):
    """
    Connection matrix: a specific type of matrix
    for synaptic connections.
    """
    def add_row(self,i,X):
        X+=self[i] # row should be a view on a vector

    def add_scaled_row(self,i,X,factor):
        X+=factor*self[i]
    
    def set_row(self,i,X):
        self[i]=X
        
    def freeze(self):
        """
        Converts the matrix to a faster structure.
        """
        pass

class DenseConnectionMatrix(ConnectionMatrix,ndarray):
    """
    A dense connection matrix.
    This is the default matrix for plastic synapses.
    """
    def __setitem__(self, index, W):
        # Make it work for sparse matrices
        if isinstance(W,sparse.spmatrix):
            ndarray.__setitem__(self,index,W.todense())
        else:
            ndarray.__setitem__(self,index,W)
    
    def add_row(self,i,X):
        X+=self[i,:] # row should be a view on a vector

    def add_scaled_row(self,i,X,factor):
        X+=factor*self[i,:]
        
    def freeze(self):
        """
        Converts the matrix to a faster structure.
        """
        pass

# TODO: use own structure?
class SparseConnectionMatrix(ConnectionMatrix,sparse.lil_matrix):
    """
    A sparse connection matrix, i.e., zero entries are not stored.
    This is the default matrix for static synapses.
    """
    def __setitem__(self, index, W):
        """
        Speed-up if x is a sparse matrix.
        TODO: checks (first remove the data).
        """
        try:
            i, j = index
        except (ValueError, TypeError):
            raise IndexError, "invalid index"

        if isinstance(i, slice) and isinstance(j,slice) and\
           (i.step is None) and (j.step is None) and\
           (isinstance(W,sparse.lil_matrix) or isinstance(W,ndarray)):
            rows = self.rows[i]
            datas = self.data[i]
            j0=j.start
            if isinstance(W,sparse.lil_matrix):
                for row,data,rowW,dataW in izip(rows,datas,W.rows,W.data):
                    jj=bisect.bisect(row,j0) # Find the insertion point
                    row[jj:jj]=[j0+k for k in rowW]
                    data[jj:jj]=dataW
            elif isinstance(W,ndarray):
                nq=W.shape[1]
                for row,data,rowW in izip(rows,datas,W):
                    jj=bisect.bisect(row,j0) # Find the insertion point
                    row[jj:jj]=range(j0,j0+nq)
                    data[jj:jj]=rowW
        else:
            sparse.lil_matrix.__setitem__(self,index,W)

    def add_row(self,i,X):
        X[self.rows[i]]+=self.data[i]

    def add_scaled_row(self,i,X,factor):
        X[self.rows[i]]+=factor*self.data[i]

    def freeze(self):
        '''
        Converts the connection matrix to a faster structure.
        Replaces array of lists (= lil_matrix) by array of arrays.
        N.B.: that's a hack (many methods will probably not work anymore).
        '''
        for i in range(self.shape[0]):
            self.rows[i]=array(self.rows[i],dtype=int)
            self.data[i]=array(self.data[i])

class ComputedConnectionMatrix(ConnectionMatrix):
    """
    A connection matrix that is computed, i.e., no storing.
    Synaptic plasticity is not possible with these matrices.
    """
    pass
    
#TODO: unit checking for some functions
class Connection(magic.InstanceTracker):
    '''
    Mechanism for propagating spikes from one group to another

    A Connection object declares that when spikes in a source
    group are generated, certain neurons in the target group
    should have a value added to specific states. See
    Tutorial 2: Connections to understand this better.

    **Initialised as:** ::
    
        Connection(source, target[, state=0[, delay=0*ms[, modulation=None]]])
    
    With arguments:
    
    ``source``
        The group from which spikes will be propagated.
    ``target``
        The group to which spikes will be propagated.
    ``state``
        The state variable name or number that spikes will be
        propagated to in the target group.
    ``delay``
        The delay between a spike being generated at the source
        and received at the target. At the moment, the mechanism
        for delays only works for relatively short delays (an
        error will be generated for delays that are too long).
    ``modulation``
        The state variable name from the source group that scales
        the synaptic weights (for short-term synaptic plasticity).
    ``structure``
        Data structure: sparse (default), dense or computed (no storing).
    
    **Methods**
    
    ``connect_random(P,Q,p[,weight=1])``
        Connects each neuron in ``P`` to each neuron in ``Q`` with independent
        probability ``p`` and weight ``weight`` (this is the amount that
        gets added to the target state variable).
    ``connect_full(P,Q[,weight=1])``
        Connect every neuron in ``P`` to every neuron in ``Q`` with the given
        weight.
    ``connect_one_to_one(P,Q)``
        If ``P`` and ``Q`` have the same number of neurons then neuron ``i``
        in ``P`` will be connected to neuron ``i`` in ``Q`` with weight 1.
    ``connect(P,Q,W)``
        You can specify a matrix of weights directly (can be in any format
        recognised by NumPy). Note that due to internal implementation details,
        passing a full matrix rather than a sparse one may slow down your code
        (because zeros will be propagated as well as nonzero values).
        **WARNING:** No unit checking is done at the moment.

    Additionally, you can directly access the matrix of weights by writing::
    
        C = Connection(P,Q)
        print C[i,j]
        C[i,j] = ...
    
    Where here ``i`` is the source neuron and ``j`` is the target neuron.
    Note: if ``C[i,j]`` should be zero, it is more efficient not to write
    ``C[i,j]=0``, if you write this then when neuron ``i`` fires all the
    targets will have the value 0 added to them rather than just the
    nonzero ones.
    **WARNING:** No unit checking is currently done if you use this method.
    Take care to set the right units.
    
    **Advanced information**
    
    The following methods are also defined and used internally, if you are
    writing your own derived connection class you need to understand what
    these do.
    
    ``propagate(spikes)``
        Action to take when source neurons with indices in ``spikes``
        fired.
    ``do_propagate()``
        The method called by the :class:`Network` ``update()`` step,
        typically just propagates the spikes obtained by calling
        the ``get_spikes`` method of the ``source`` :class:`NeuronGroup`.
    '''
    @traceback_info('Exception encountered while creating Connection object.')
    @analyse_bugs
    @check_units(delay=second)
    def __init__(self,source,target,state=0,delay=0*msecond,modulation=None,
                 structure='sparse',**kwds):
        self.source=source # pointer to source group
        self.target=target # pointer to target group
        if type(state)==types.StringType: # named state variable
            self.nstate=target.get_var_index(state)
        else:
            self.nstate=state # target state index
        if type(modulation)==types.StringType: # named state variable
            self._nstate_mod=source.get_var_index(modulation)
        else:
            self._nstate_mod=modulation # source state index
        if isinstance(structure,str):
            structure = {'sparse':SparseConnectionMatrix,
                'dense':DenseConnectionMatrix,
                'computed':ComputedConnectionMatrix
                }[structure]
        self.W=structure((len(source),len(target)),**kwds)
        self.iscompressed=False # True if compress() has been called
        self.delay=int(delay/source.clock.dt) # Synaptic delay in time bins
        if self.delay>source._max_delay:
            raise AttributeError,"Transmission delay is too long."
        
    def reinit(self):
        '''
        Resets the variables.
        '''
        pass
        
    def propagate(self,spikes):
        '''
        Propagates the spikes to the target.
        '''
        #-- Version 1 --
        #for i in spikes.flat:
        #    self.target._S[self.nstate,:]+=self.W[i,:]
        #-- Version 2 --
        #for i in spikes.flat:
        #    self.target._S[self.nstate,self.W.rows[i]]+=self.W.data[i]
        #-- Version 3 --
        #N.B.: not faster to move the state vector to init()
        sv=self.target._S[self.nstate]
        if self._nstate_mod is None:
            for i in spikes:
                self.W.add_row(i,sv)
        else:
            sv_pre=self.source._S[self._nstate_mod]
            for i,x in izip(spikes,sv_pre[spikes]):
                self.W.add_scaled_row(i,sv,x)
    
    def do_propagate(self):
        self.propagate(self.source.get_spikes(self.delay))
    
    def origin(self,P,Q):
        '''
        Returns the starting coordinate of the given groups in
        the connection matrix W.
        '''
        return (P._origin-self.source._origin,Q._origin-self.target._origin)

    def compress(self):
        '''
        Converts the connection matrix to a faster structure.
        Replaces array of lists (= lil_matrix) by array of arrays.
        N.B.: that's a hack (many methods will probably not work anymore).
        '''
        if not self.iscompressed:
            self.W.freeze()
            self.iscompressed=True

    @analyse_bugs
    # TODO change this
    def connect(self,P,Q,W):
        '''
        Connects (sub)groups P and Q with the weight matrix W (any type).
        Internally: inserts W as a submatrix.
        TODO: checks if the submatrix has already been specified.
        '''
        i0,j0=self.origin(P,Q)
        self.W[i0:i0+len(P),j0:j0+len(Q)]=W
        
    @analyse_bugs
    def connect_random(self,P,Q,p,weight=1.):
        '''
        Connects the neurons in group P to neurons in group Q with probability p,
        with given weight (default 1).
        The weight can be a quantity or a function of i (in P) and j (in Q).
        '''
        if type(weight)==types.FunctionType:
            # Check units
            try:
                weight(0,0)+Q._S0[self.nstate]
            except DimensionMismatchError,inst:
                raise DimensionMismatchError("Incorrects unit for the synaptic weights.",*inst._dims)
            self.connect(P,Q,random_matrix(len(P),len(Q),p,value=weight))
        else:
            # Check units
            try:
                weight+Q._S0[self.nstate]
            except DimensionMismatchError,inst:
                raise DimensionMismatchError("Incorrects unit for the synaptic weights.",*inst._dims)
            self.connect(P,Q,random_matrix(len(P),len(Q),p,value=float(weight)))

    @analyse_bugs
    def connect_full(self,P,Q,weight=1.):
        '''
        Connects the neurons in group P to all neurons in group Q,
        with given weight (default 1).
        The weight can be a quantity or a function of i (in P) and j (in Q).
        '''
        # TODO: check units
        if type(weight)==types.FunctionType:
            # Check units
            try:
                weight(0,0)+Q._S0[self.nstate]
            except DimensionMismatchError,inst:
                raise DimensionMismatchError("Incorrects unit for the synaptic weights.",*inst._dims)
            W=zeros((len(P),len(Q)))
            try:
                weight(0,1.*arange(0,len(Q)))
                failed=False
            except:
                failed= True
            if failed: # vector-based not possible
                log_debug('connections','Cannot build the connection matrix by rows')
                for i in range(len(P)):
                    for j in range(len(Q)):
                        W[i,j]=weight(i,j)
            else:
                for i in range(len(P)): # build W row by row
                    W[i,:]=weight(i,1.*arange(0,len(Q)))
            self.connect(P,Q,W)
        else:
            try:
                weight+Q._S0[self.nstate]
            except DimensionMismatchError,inst:
                raise DimensionMismatchError("Incorrect unit for the synaptic weights.",*inst._dims)
            self.connect(P,Q,float(weight)*ones((len(P),len(Q))))

    @analyse_bugs
    def connect_one_to_one(self,P,Q,weight=1):
        '''
        Connects P[i] to Q[i] with weights 1 (or weight).
        '''
        if (len(P)!=len(Q)):
            raise AttributeError,'The connected (sub)groups must have the same size.'
        # TODO: unit checking
        self.connect(P,Q,float(weight)*eye_lil_matrix(len(P)))
        
    def __getitem__(self,i):
        return self.W.__getitem__(i)

    def __setitem__(self,i,x):
        # TODO: unit checking
        self.W.__setitem__(i,x)

class IdentityConnection(Connection):
    '''
    A connection between two (sub)groups of the same size, connecting
    P[i] to Q[i] with given weight (default 1)
    '''
    @check_units(delay=second)
    def __init__(self,source,target,state=0,weight=1,delay=0*msecond):
        if (len(source)!=len(target)):
            raise AttributeError,'The connected (sub)groups must have the same size.'
        self.source=source # pointer to source group
        self.target=target # pointer to target group
        if type(state)==types.StringType: # named state variable
            self.nstate=target.get_var_index(state)
        else:
            self.nstate=state # target state index
        self.W=float(weight) # weight
        self.delay=int(delay/source.clock.dt) # Synaptic delay in time bins
        if self.delay>source._max_delay:
            raise AttributeError,"Transmission delay is too long."
        
    def propagate(self,spikes):
        '''
        Propagates the spikes to the target.
        '''
        self.target._S[self.nstate,spikes]+=self.W
        
    def compress(self):
        pass
    
class MultiConnection(Connection):
    '''
    A hub for multiple connections with a common source group.
    '''
    def __init__(self,source,connections=[]):
        self.source=source
        self.connections=connections
        self.iscompressed=False
        self.delay=int(connections[0].delay/source.clock.dt) # Assuming identical delays
        
    def propagate(self,spikes):
        '''
        Propagates the spikes to the targets.
        '''
        for C in self.connections:
            C.propagate(spikes)
            
    def compress(self):
        if not self.iscompressed:
            for C in self.connections:
                C.compress()
            self.iscompressed=True

# Generation of matrices
# TODO: vectorise
def random_matrix(n,m,p,value=1.):
    '''
    Generates a sparse random matrix with size (n,m).
    Entries are 1 (or optionnally value) with probability p.
    If value is a function, then that function is called for each
    non zero element as value() or value(i,j).
    '''
    W=sparse.lil_matrix((n,m))
    if type(value)==types.FunctionType:
        if value.func_code.co_argcount==0:
            for i in xrange(n):
                k=random.binomial(m,p,1)[0]
                W.rows[i]=sample(xrange(m),k)
                W.data[i]=[value() for _ in xrange(k)]
        elif value.func_code.co_argcount==2:
            for i in xrange(n):
                k=random.binomial(m,p,1)[0]
                W.rows[i]=sample(xrange(m),k)
                W.data[i]=[value(i,j) for j in W.rows[i]]            
        else:
            raise AttributeError,"Bad number of arguments in value function (should be 0 or 2)"
    else:
        for i in xrange(n):
            k=random.binomial(m,p,1)[0]
            # Not significantly faster to generate all random numbers in one pass
            # N.B.: the sample method is implemented in Python and it is not in Scipy
            W.rows[i]=sample(xrange(m),k)
            W.data[i]=[value]*k

    return W

# Generation of matrices row by row
# TODO: vectorise
def random_matrix_row_by_row(n,m,p,value=1.):
    '''
    Generates a sparse random matrix with size (n,m).
    Entries are 1 (or optionnally value) with probability p.
    If value is a function, then that function is called for each
    non zero element as value() or value(i,j).
    '''
    if type(value)==types.FunctionType:
        if value.func_code.co_argcount==0:
            for i in xrange(n):
                k=random.binomial(m,p,1)[0]
                yield sample(xrange(m),k), [value() for _ in xrange(k)]
        elif value.func_code.co_argcount==2:
            for i in xrange(n):
                k=random.binomial(m,p,1)[0]
                yield sample(xrange(m),k), [value(i,j) for j in W.rows[i]]
        else:
            raise AttributeError,"Bad number of arguments in value function (should be 0 or 2)"
    else:
        for i in xrange(n):
            k=random.binomial(m,p,1)[0]
            yield sample(xrange(m),k), value 


def eye_lil_matrix(n):
    '''
    Returns the identity matrix of size n as a lil_matrix
    (sparse matrix).
    '''
    M=sparse.lil_matrix((n,n))
    M.setdiag([1.]*n)
    return M

def _define_and_test_interface(self):
    '''
    :class:`Connection`
    ~~~~~~~~~~~~~~~~~~~
    
    **Initialised as:** ::
    
        Connection(source, target[, state=0[, delay=0*ms]])
    
    With arguments:
    
    ``source``
        The group from which spikes will be propagated.
    ``target``
        The group to which spikes will be propagated.
    ``state``
        The state variable name or number that spikes will be
        propagated to in the target group.
    ``delay``
        The delay between a spike being generated at the source
        and received at the target. At the moment, the mechanism
        for delays only works for relatively short delays (an
        error will be generated for delays that are too long), but
        this is subject to change. The exact behaviour then is
        not part of the assured interface, although it is very
        likely that the syntax will not change (or will at least
        be backwards compatible).
    
    **Methods**
    
    ``connect_random(P,Q,p[,weight=1])``
        Connects each neuron in ``P`` to each neuron in ``Q``.
    ``connect_full(P,Q[,weight=1])``
        Connect every neuron in ``P`` to every neuron in ``Q``.
    ``connect_one_to_one(P,Q)``
        If ``P`` and ``Q`` have the same number of neurons then neuron ``i``
        in ``P`` will be connected to neuron ``i`` in ``Q`` with weight 1.
    
    Additionally, you can directly access the matrix of weights by writing::
    
        C = Connection(P,Q)
        print C[i,j]
        C[i,j] = ...
    
    Where here ``i`` is the source neuron and ``j`` is the target neuron.
    Note: No unit checking is currently done if you use this method,
    but this is subject to change for future releases.

    The behaviour when a list of neuron ``spikes`` is received is to
    add ``W[i,:]`` to the target state variable for each ``i`` in ``spikes``. 
    '''
    
    from directcontrol import SpikeGeneratorGroup
    from neurongroup import NeuronGroup
    from network import Network
    from utils.approximatecomparisons import is_approx_equal
    from clock import reinit_default_clock
    
    # test Connection object
    
    eqs = '''
    da/dt = 0.*hertz : 1.
    db/dt = 0.*hertz : 1.
    '''
    
    spikes = [(0,1*msecond),(1,3*msecond)]
    
    G1 = SpikeGeneratorGroup(2,spikes)
    G2 = NeuronGroup(2,model=eqs,threshold=10.,reset=0.)
    
    # first test the methods
    # connect_full
    C = Connection(G1,G2)
    C.connect_full(G1, G2, weight=2.)
    for i in range(2):
        for j in range(2):
            self.assert_(is_approx_equal(C[i,j],2.))
    # connect_random
    C = Connection(G1,G2)
    C.connect_random(G1, G2, 0.5, weight=2.)
    # can't assert anything about that
    # connect_one_to_one
    C = Connection(G1,G2)
    C.connect_one_to_one(G1, G2)
    for i in range(2):
        for j in range(2):
            if i==j:
                self.assert_(is_approx_equal(C[i,j],1.))
            else:
                self.assert_(is_approx_equal(C[i,j],0.))
    del C
    # and we will use a specific set of connections in the next part
    Ca = Connection(G1,G2,'a')
    Cb = Connection(G1,G2,'b')
    Ca[0,0]=1.
    Ca[0,1]=1.
    Ca[1,0]=1.
    #Ca[1,1]=0 by default
    #Cb[0,0]=0 by default
    Cb[0,1]=1.
    Cb[1,0]=1.
    Cb[1,1]=1.
    net = Network(G1,G2,Ca,Cb)
    net.run(2*msecond)
    # after 2 ms, neuron 0 will have fired, so a 0 and 1 should
    # have increased by 1 to [1,1], and b 1 should have increased
    # by 1 to 1
    self.assert_(is_approx_equal(G2.a[0],1.))
    self.assert_(is_approx_equal(G2.a[1],1.))
    self.assert_(is_approx_equal(G2.b[0],0.))
    self.assert_(is_approx_equal(G2.b[1],1.))
    net.run(2*msecond)
    # after 4 ms, neuron 1 will have fired, so a 0 should have
    # increased by 1 to 2, and b 0 and 1 should have increased
    # by 1 to [1, 2]
    self.assert_(is_approx_equal(G2.a[0],2.))
    self.assert_(is_approx_equal(G2.a[1],1.))
    self.assert_(is_approx_equal(G2.b[0],1.))
    self.assert_(is_approx_equal(G2.b[1],2.))
    
    reinit_default_clock()
