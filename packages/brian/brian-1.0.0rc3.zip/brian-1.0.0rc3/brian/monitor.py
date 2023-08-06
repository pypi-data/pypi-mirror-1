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
'''
Monitors (spikes and state variables).
* Tip: Spike monitors should have non significant impact on simulation time
if properly coded.
'''

__all__ = ['SpikeMonitor', 'PopulationSpikeCounter', 'SpikeCounter','FileSpikeMonitor','StateMonitor','ISIHistogramMonitor',\
           'PopulationRateMonitor']

from units import *
from connection import Connection
from numpy import array, zeros, histogram, copy, ones, exp, arange, convolve
from itertools import repeat
from clock import guess_clock
from network import NetworkOperation
from quantityarray import *
from utils.docobj import *
import types

# defines and tests the interface, the docstring is considered part of the definition
def _define_and_test_interface(self):
    '''
    :class:`SpikeMonitor`
    ~~~~~~~~~~~~~~~~~~~~~
    
    Records spikes from a :class:`NeuronGroup`. Initialised as one of::
    
        SpikeMonitor(source(,record=True))
        SpikeMonitor(source,function=function)
    
    Where:
    
    source
        A :class:`NeuronGroup` to record from
    record
        True or False to record all the spikes or just summary
        statistics.
    function
        A function f(spikes) which is passed the array of spikes
        numbers that have fired called each step, to define
        custom spike monitoring.
    
    Has two attributes:
    
    nspikes
        The number of recorded spikes
    spikes
        A time ordered list of pairs (i,t) where neuron i fired
        at time t.
    
    :class:`StateMonitor`
    ~~~~~~~~~~~~~~~~~~~~~
    
    Records the values of a state variable from a :class:`NeuronGroup`.
    Initialise as::
    
        StateMonitor(P,varname(,record=False)
            (,when='end)(,timestep=1)(,clock=clock))
    
    Where:
    
    P
        The group to be recorded from
    varname
        The state variable name or number to be recorded
    record
        What to record. The default value is False and the monitor will
        only record summary statistics for the variable. You can choose
        record=integer to record every value of the neuron with that
        number, record=list of integers to record every value of each of
        those neurons, or record=True to record every value of every
        neuron (although beware that this may use a lot of memory).
    when
        When the recording should be made in the :class:`Network` update, possible
        values are any of the strings: 'start', 'before_groups', 'after_groups',
        'before_connections', 'after_connections', 'before_resets',
        'after_resets', 'end' (in order of when they are run).
    timestep
        A recording will be made each timestep clock updates (so timestep
        should be an integer).
    clock
        A clock for the update schedule, use this if you have specified a
        clock other than the default one in your network, or to update at a
        lower frequency than the update cycle. Note though that if the clock
        here is different from the main clock, the when parameter will not
        be taken into account, as network updates are done clock by clock.
        Use the timestep parameter if you need recordings to be made at a
        precise point in the network update step.

    The :class:`StateMonitor` object has the following properties (where names
    without an underscore return :class:`QuantityArray` objects with appropriate
    units and names with an underscore return array objects without
    units):

    times, times_
        The times at which recordings were made
    mean, mean_
        The mean value of the state variable for every neuron in the
        group (not just the ones specified in the record keyword)
    var, var_
        The unbiased estimate of the variances, as in mean
    std, std_
        The square root of var, as in mean
        
    In addition, if M is a :class:`StateMonitor` object, you write::
    
        M[i]
    
    for the recorded values of neuron i (if it was specified with the
    record keyword). It returns a :class:`QuantityArray` object with units. Downcast
    to an array without units by writing asarray(M[i]).
    
    Others
    ~~~~~~
    
    The following monitors also exist, but are not part of the
    assured interface because their syntax is subject to change. See the documentation
    for each class for more details.
    
    * :class:`Monitor` (base class)
    * :class:`ISIHistogramMonitor`
    * :class:`FileSpikeMonitor`
    * :class:`PopulationRateMonitor`
    '''
    
    from directcontrol import SpikeGeneratorGroup
    from network import Network, network_operation
    from stdunits import ms, Hz
    from utils.approximatecomparisons import is_approx_equal, is_within_absolute_tolerance
    from clock import reinit_default_clock, get_default_clock, Clock
    from neurongroup import NeuronGroup
    from numpy import diff, var, std, mean
    
    # test that SpikeMonitor retrieves the spikes generator by SpikeGeneratorGroup

    spikes = [(0,3*ms),(1,4*ms),(0,7*ms)]
    
    G = SpikeGeneratorGroup(2,spikes)
    M = SpikeMonitor(G)
    net = Network(G,M)
    net.run(10*ms)
    
    self.assert_(M.nspikes==3)
    for (mi, mt), (i, t) in zip(M.spikes,spikes):
        self.assert_(mi==i)
        self.assert_(is_approx_equal(mt,t))
    
    # test that SpikeMonitor function calling usage does what you'd expect    
    
    f_spikes = []
    
    def f(spikes):
        if len(spikes):
            f_spikes.extend(spikes)
    
    G = SpikeGeneratorGroup(2,spikes)
    M = SpikeMonitor(G,function=f)
    net = Network(G,M)
    reinit_default_clock()
    net.run(10*ms)
    self.assert_(f_spikes==[0,1,0])
    
    # test interface for StateMonitor object
    
    dV = 'dV/dt = 0*Hz : 1.'
    G = NeuronGroup(3,model=dV,reset=0.,threshold=10.)
    @network_operation(when='start')
    def f(clock):
        if clock.t>=1*ms:
            G.V = [1.,2.,3.]
    M1 = StateMonitor(G,'V')
    M2 = StateMonitor(G,'V',record=0)
    M3 = StateMonitor(G,'V',record=[0,1])
    M4 = StateMonitor(G,'V',record=True)
    reinit_default_clock()
    net = Network(G,f,M1,M2,M3,M4)
    net.run(2*ms)
    self.assert_(is_within_absolute_tolerance(M2[0][0],0.))
    self.assert_(is_within_absolute_tolerance(M2[0][-1],1.))
    self.assert_(is_within_absolute_tolerance(M3[1][0],0.))
    self.assert_(is_within_absolute_tolerance(M3[1][-1],2.))
    self.assert_(is_within_absolute_tolerance(M4[2][0],0.))
    self.assert_(is_within_absolute_tolerance(M4[2][-1],3.))
    self.assertRaises(IndexError,M1.__getitem__,0)
    self.assertRaises(IndexError,M2.__getitem__,1)
    self.assertRaises(IndexError,M3.__getitem__,2)
    self.assertRaises(IndexError,M4.__getitem__,3)
    for M in [M3, M4]:
        self.assert_(is_within_absolute_tolerance(max(abs(M.times-M2.times)),0*ms))
        self.assert_(is_within_absolute_tolerance(max(abs(M.times_-M2.times_)),0.))
    for M in [M2, M3, M4]:
        self.assert_(is_within_absolute_tolerance(max(abs(M.mean-M1.mean)),0.))
        self.assert_(is_within_absolute_tolerance(max(abs(M.var-M1.var)),0.))
        self.assert_(is_within_absolute_tolerance(max(abs(M.std-M1.std)),0.))
        self.assert_(is_within_absolute_tolerance(max(abs(M.mean_-M1.mean_)),0.))
        self.assert_(is_within_absolute_tolerance(max(abs(M.var_-M1.var_)),0.))
        self.assert_(is_within_absolute_tolerance(max(abs(M.std_-M1.std_)),0.))
    self.assert_(is_within_absolute_tolerance(M2.times[0],0*ms))
    d = diff(M2.times)
    self.assert_(is_within_absolute_tolerance(max(d),min(d)))
    self.assert_(is_within_absolute_tolerance(max(d),get_default_clock().dt))
    # construct unbiased estimator from variances of recorded arrays
    v = qarray([ var(M4[0]), var(M4[1]), var(M4[2]) ]) * float(len(M4[0])) / float(len(M4[0])-1)
    m = qarray([0.5, 1.0, 1.5])
    self.assert_(is_within_absolute_tolerance(abs(max(M1.mean-m)),0.))
    self.assert_(is_within_absolute_tolerance(abs(max(M1.var-v)),0.))
    self.assert_(is_within_absolute_tolerance(abs(max(M1.std-v**0.5)),0.))
    
    # test when, timestep, clock for StateMonitor
    c = Clock(dt=0.1*ms)
    cslow = Clock(dt=0.2*ms)
    dV = 'dV/dt = 0*Hz : 1.'
    G = NeuronGroup(1,model=dV,reset=0.,threshold=1.,clock=c)
    @network_operation(when='start',clock=c)
    def f():
        G.V = 2.
    M1 = StateMonitor(G,'V',record=True,clock=cslow)
    M2 = StateMonitor(G,'V',record=True,timestep=2,clock=c)
    M3 = StateMonitor(G,'V',record=True,when='before_groups',clock=c)
    net = Network(G,f,M1,M2,M3,M4)
    net.run(2*ms)
    self.assert_(2*len(M1[0])==len(M3[0]))
    self.assert_(len(M1[0])==len(M2[0]))
    for i in range(len(M1[0])):
        self.assert_(is_within_absolute_tolerance(M1[0][i],M2[0][i]))
        self.assert_(is_within_absolute_tolerance(M1[0][i],0.))
    for x in M3[0]:
        self.assert_(is_within_absolute_tolerance(x,2.))
        
    reinit_default_clock() # for next test
        
class Monitor(object):
    pass

documented_objects.append('SpikeMonitor')
class SpikeMonitor(Connection,Monitor):
    '''
    Counts or records spikes from a :class:`NeuronGroup`

    Initialised as one of::
    
        SpikeMonitor(source(,record=True))
        SpikeMonitor(source,function=function)
    
    Where:
    
    ``source``
        A :class:`NeuronGroup` to record from
    ``record``
        ``True`` or ``False`` to record all the spikes or just summary
        statistics.
    ``function``
        A function ``f(spikes)`` which is passed the array of neuron
        numbers that have fired called each step, to define
        custom spike monitoring.
    
    Has two attributes:
    
    ``nspikes``
        The number of recorded spikes
    ``spikes``
        A time ordered list of pairs ``(i,t)`` where neuron ``i`` fired
        at time ``t``.

    Notes:

    :class:`SpikeMonitor` is subclassed from :class:`Connection`.
    To define a custom monitor, either define a subclass and
    rewrite the ``propagate`` method, or pass the monitoring function
    as an argument (``function=myfunction``, with ``def myfunction(spikes):...``)
    '''
    def __init__(self,source,record=True,delay=0,function=None):
        # recordspikes > record?
        self.source=source # pointer to source group
        self.target=None
        self.nspikes=0
        self.spikes=[]
        self.record = record
        self.W=None # should we just remove this variable?
        self.delay=delay
        if function!=None:
            self.propagate=function
        
    def reinit(self):
        """
        Clears all monitored spikes
        """
        self.nspikes=0
        self.spikes=[]
        
    def propagate(self,spikes):
        '''
        Deals with the spikes.
        Overload this function to store or process spikes.
        Default: counts the spikes (variable nspikes)
        '''
        self.nspikes+=len(spikes)
        if self.record:
            self.spikes+=zip(spikes,repeat(self.source.clock.t))
            
    def origin(self,P,Q):
        '''
        Returns the starting coordinate of the given groups in
        the connection matrix W.
        '''
        return (P.origin-self.source.origin,0)

    def compress(self):
        pass

documented_objects.append('PopulationSpikeCounter')
class PopulationSpikeCounter(SpikeMonitor):
    '''
    Counts spikes from a :class:`NeuronGroup`

    Initialised as::
    
        PopulationSpikeCounter(source)
    
    With argument:
    
    ``source``
        A :class:`NeuronGroup` to record from
    
    Has one attribute:
    
    ``nspikes``
        The number of recorded spikes
    '''
    def __init__(self, source, delay=0):
        SpikeMonitor.__init__(self,source,record=False,delay=delay)

documented_objects.append('SpikeCounter')
class SpikeCounter(PopulationSpikeCounter):
    '''
    Counts spikes from a :class:`NeuronGroup`

    Initialised as::
    
        SpikeCounter(source)
    
    With argument:
    
    ``source``
        A :class:`NeuronGroup` to record from
    
    Has two attributes:
    
    ``nspikes``
        The number of recorded spikes
    ``count``
        An array of spike counts for each neuron
    
    For a :class:`SpikeCounter` ``M`` you can also write ``M[i]`` for the
    number of spikes counted for neuron ``i``.
    '''
    def __init__(self, source):
        PopulationSpikeCounter.__init__(self, source)
        self.count = zeros(len(source),dtype=int)
    def __getitem__(self, i):
        return self.count[i]
    def propagate(self, spikes):
        PopulationSpikeCounter.propagate(self, spikes)
        self.count[spikes]+=1

class HistogramMonitorBase(SpikeMonitor):
    pass

documented_objects.append('ISIHistogramMonitor')
class ISIHistogramMonitor(HistogramMonitorBase):
    '''
    Records the interspike interval histograms of a group.
    
    Initialised as::
    
        ISIHistogramMonitor(source, bins)
    
    ``source``
        The source group to record from.
    ``bins``
        The lower bounds for each bin, so that e.g.
        ``bins = [0*ms, 10*ms, 20*ms]`` would correspond to
        bins with intervals 0-10ms, 10-20ms and
        20+ms.
        
    Has properties:
    
    ``bins``
        The ``bins`` array passed at initialisation.
    ``count``
        An array of length ``len(bins)`` counting how many ISIs
        were in each bin.
    
    This object can be passed directly to the plotting function
    :func:`hist_plot`.
    '''
    def __init__(self,source,bins,delay=0):
        SpikeMonitor.__init__(self,source,delay)
        self.bins = array(bins)
        self.reinit()
    def reinit(self):
        super(ISIHistogramMonitor,self).reinit()
        self.count = zeros(len(self.bins))
        self.LS = 1000*second*ones(len(self.source))
    def propagate(self,spikes):
        super(ISIHistogramMonitor,self).propagate(spikes)
        isi = self.source.clock.t-self.LS[spikes]
        self.LS[spikes]=self.source.clock.t
        #print isi
        h,a = histogram(isi,self.bins)
        self.count = self.count + h

documented_objects.append('FileSpikeMonitor')
class FileSpikeMonitor(SpikeMonitor):
    """Records spikes to a file

    Initialised as::
    
        FileSpikeMonitor(source, filename[, record=False])
    
    Does everything that a :class:`SpikeMonitor` does except also records
    the spikes to the named file. note that spikes are recorded
    as an ASCII file of lines each of the form:
    
        ``i, t``
    
    Where ``i`` is the neuron that fired, and ``t`` is the time in seconds.
    
    Has one additional method:
    
    ``close_file()``
        Closes the file manually (will happen automatically when
        the program ends).
    """
    def __init__(self,source,filename,record=False,delay=0):
        super(FileSpikeMonitor,self).__init__(source,record,delay)
        self.filename = filename
        self.f = open(filename,'w')
    def reinit(self):
        self.close_file()
        self.f = open(self.filename,'w')
    def propagate(self,spikes):
        super(FileSpikeMonitor,self).propagate(spikes)
        for i in spikes:
            self.f.write(str(i)+", "+str(float(self.source.clock.t))+"\n")
    def close_file(self):
        self.f.close()

documented_objects.append('PopulationRateMonitor')
class PopulationRateMonitor(SpikeMonitor):
    '''
    Monitors and stores the (time-varying) population rate
    
    Initialised as::
    
        PopulationRateMonitor(source,bin)
    
    Records the average activity of the group for every bin.
    
    Properties:
    
    ``rate``, ``rate_``
        A :class:`qarray` of the rates in Hz.    
    ``times``, ``times_``
        The times of the bins.
    ``bin``
        The duration of a bin (in second).
    '''
    times  = property(fget=lambda self:qarray(self._times)*second)
    times_ = property(fget=lambda self:array(self._times))
    rate  = property(fget=lambda self:qarray(self._rate)*hertz)
    rate_ = property(fget=lambda self:array(self._rate))

    def __init__(self,source,bin=None):
        SpikeMonitor.__init__(self,source)
        if bin:
            self._bin=int(bin/source.clock.dt)
        else:
            self._bin=1 # bin size in number
        self._rate=[]
        self._times=[]
        self._curstep=0
        self._clock=source.clock
        self._factor=1./float(self._bin*source.clock.dt*len(source))    
       
    def reinit(self):
        SpikeMonitor.reinit()
        self._rate=[]
        self._times=[]
        self._curstep=0
        
    def propagate(self,spikes):
        if self._curstep==0:
            self._rate.append(0.)
            self._times.append(self._clock._t) # +.5*bin?
            self._curstep=self._bin
        self._rate[-1]+=len(spikes)*self._factor
        self._curstep-=1
        
    def smooth_rate(self,width=1*msecond,filter='gaussian'):
        """
        Returns a smoothed version of the vector of rates,
        convolving the rates with a filter (gaussian or flat)
        with the given width.
        """
        width_dt=int(width/(self._bin*self._clock.dt))
        window={'gaussian': exp(-arange(-2*width_dt,2*width_dt+1)**2*1./(2*(width_dt)**2)),
                'flat': ones(width_dt)}[filter]
        return qarray(convolve(self.rate_,window*1./sum(window),mode='same'))*hertz
    
documented_objects.append('StateMonitor')
class StateMonitor(NetworkOperation,Monitor):
    '''
    Records the values of a state variable from a :class:`NeuronGroup`.

    Initialise as::
    
        StateMonitor(P,varname(,record=False)
            (,when='end)(,timestep=1)(,clock=clock))
    
    Where:
    
    ``P``
        The group to be recorded from
    ``varname``
        The state variable name or number to be recorded
    ``record``
        What to record. The default value is ``False`` and the monitor will
        only record summary statistics for the variable. You can choose
        ``record=integer`` to record every value of the neuron with that
        number, ``record=``list of integers to record every value of each of
        those neurons, or ``record=True`` to record every value of every
        neuron (although beware that this may use a lot of memory).
    ``when``
        When the recording should be made in the network update, possible
        values are any of the strings: ``'start'``, ``'before_groups'``, ``'after_groups'``,
        ``'before_connections'``, ``'after_connections'``, ``'before_resets'``,
        ``'after_resets'``, ``'end'`` (in order of when they are run).
    ``timestep``
        A recording will be made each timestep clock updates (so ``timestep``
        should be an integer).
    ``clock``
        A clock for the update schedule, use this if you have specified a
        clock other than the default one in your network, or to update at a
        lower frequency than the update cycle. Note though that if the clock
        here is different from the main clock, the when parameter will not
        be taken into account, as network updates are done clock by clock.
        Use the ``timestep`` parameter if you need recordings to be made at a
        precise point in the network update step.

    The :class:`StateMonitor` object has the following properties (where names
    without an underscore return :class:`QuantityArray` objects with appropriate
    units and names with an underscore return ``array`` objects without
    units):

    ``times``, ``times_``
        The times at which recordings were made
    ``mean``, ``mean_``
        The mean value of the state variable for every neuron in the
        group (not just the ones specified in the ``record`` keyword)
    ``var``, ``var_``
        The unbiased estimate of the variances, as in ``mean``
    ``std``, ``std_``
        The square root of ``var``, as in ``mean``
        
    In addition, if :class:`M`` is a :class:`StateMonitor` object, you write::
    
        M[i]
    
    for the recorded values of neuron ``i`` (if it was specified with the
    ``record`` keyword). It returns a :class:`QuantityArray` object with units. Downcast
    to an array without units by writing ``asarray(M[i])``.
    '''
    times  = property(fget=lambda self:QuantityArray(self._times))
    mean   = property(fget=lambda self:self.unit*QuantityArray(self._mu/self.N))
    _mean  = property(fget=lambda self:self._mu/self.N)
    var    = property(fget=lambda self:(self.unit*self.unit*QuantityArray(self._sqr-self.N*self._mean**2)/(self.N-1)))
    std    = property(fget=lambda self:self.var**.5)
    mean_  = _mean
    var_   = property(fget=lambda self:(self._sqr-self.N*self.mean_**2)/(self.N-1))
    std_   = property(fget=lambda self:self.var_**.5)
    times_ = property(fget=lambda self:array(self._times))
    
    def __init__(self,P,varname,clock=None,record=False,timestep=1,when='end'):
        '''
        -- P is the neuron group
        -- varname is the variable name
        -- record can be one of:
           - an integer, in which case the value of the state of the corresponding
           neuron will be recorded in the list self.values
           - an array or list of integers, in which case the value of the states
           of the corresponding neurons will be recorded and can be individually
           accessed by calling self[i] where i is the neuron number
           - True, in which case the state of all neurons is recorded, and can be
           individually accessed by calling self[i]
        -- timestep defines how often a recording is made (e.g. if you have a very
           small dt, you might not want to record every value of the variable), it
           is an integer (multiple of the clock dt)
        '''
        NetworkOperation.__init__(self,None,clock=clock,when=when)
        self.record = record
        self.clock = guess_clock(clock)
        if record is not False:
            if record is not True and not isinstance(record,int):
                self.recordindex = dict((i,j) for i,j in zip(self.record,range(len(self.record))))
        self.timestep = timestep
        self.curtimestep = timestep
        self.values = None
        self.P=P
        self.varname=varname
        self.N=0 # number of steps
        self._recordstep = 0
        self._mu=zeros(len(P)) # sum
        self._sqr=zeros(len(P)) # sum of squares
        self.unit = 1.0*P.unit(varname)
        
    def __call__(self):
        '''
        This function is called every time step.
        '''
        V=self.P.state_(self.varname)
        self._mu+=V
        self._sqr+=V*V
        if self.record is not False and self.curtimestep==self.timestep:
            i = self._recordstep
            if self.values is None:
                #numrecord = len(self.get_record_indices())
                #numtimesteps = (int(self.clock.get_duration()/self.clock.dt))/self.timestep + 1
                self.values = []#zeros((numtimesteps,numrecord))
                self._times = []#QuantityArray(zeros(numtimesteps))
            if type(self.record)!=types.BooleanType:
                self.values.append(V[self.record])
            elif self.record is True:
                self.values.append(V.copy())
            self._times.append(self.clock.t)
            self._recordstep += 1
        self.curtimestep-=1
        if self.curtimestep==0: self.curtimestep=self.timestep
        self.N+=1
    
    def __getitem__(self,i):
        """Returns the recorded values of the state of neuron i as a QuantityArray
        """
        if self.record is False:
            raise IndexError('Neuron ' + str(i) + ' was not recorded.')
        if self.record is not True:
            if isinstance(self.record,int) and self.record!=i or (not isinstance(self.record,int) and i not in self.record):
                raise IndexError('Neuron ' + str(i) + ' was not recorded.')
            try:
                #return QuantityArray(self.values[:self._recordstep,self.recordindex[i]])*self.unit
                return QuantityArray(array(self.values)[:,self.recordindex[i]])*self.unit
            except:
                if i==self.record:
                    return QuantityArray(self.values)*self.unit
                else:
                    raise
        elif self.record is True:
            return QuantityArray(array(self.values)[:,i])*self.unit
    
    def reinit(self):
        self.values = None
        self.N=0
        self._recordstep = 0
        self._mu=zeros(len(self.P))
        self._sqr=zeros(len(self.P))
        
    def get_record_indices(self):
        """Returns the list of neuron numbers which were recorded.
        """
        if self.record is False:
            return []
        elif self.record is True:
            return range(len(self.P))
        elif isinstance(self.record,int):
            return [self.record]
        else:
            return self.record