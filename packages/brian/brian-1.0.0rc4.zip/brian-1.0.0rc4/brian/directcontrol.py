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
"""Direct controlling mechanisms

NeuronGroups and callable objects which allow direct
control over the behaviour of neurons.
"""

__all__ = ['MultipleSpikeGeneratorGroup','SpikeGeneratorGroup','PulsePacket']

from neurongroup import *
from threshold import *
from stateupdater import *
from units import *
import random as pyrandom
from numpy import where, array, zeros
from copy import copy
from clock import guess_clock
from utils.approximatecomparisons import *
import warnings
from operator import itemgetter
from log import *

# defines and tests the interface, the docstring is considered part of the definition
def _define_and_test_interface(self):
    """
    Spike containers
    ~~~~~~~~~~~~~~~~
    
    A spike container is either an iterable object or a callable object which
    returns an iterable object. For example, a list is a spike container, as
    is a generator, as is a function which returns a list, or a generator
    function.
    
    :class:`MultipleSpikeGeneratorGroup`
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Called as::
    
        MultipleSpikeGeneratorGroup(spiketimes[,clock])
        
    spiketimes is a list of spike containers, one for each neuron in the group.
    The elements of the spike containers are spike times. Callable spike
    containers are called when the group is reinitialised. If you provide
    a generator rather than a callable object, reinitialising the group will
    not reinitialise the generator.
    
    So for example, the following will correspond to a group of 2 neurons, where
    the first fires at times 0ms, 2ms and 5ms, and the second fires at times
    1ms and 3ms::
    
        spiketimes = [[0*msecond, 2*msecond, 5*msecond],
                      [1*msecond, 3*msecond]]
        G = MultipleSpikeGeneratorGroup(spiketimes)
    
    You could do the same thing with generator functions (rather perversely in
    this case)::
    
        def st1():
            yield 0*msecond
            yield 2*msecond
            yield 5*msecond
        def st2():
            yield 1*msecond
            yield 3*msecond
        G = MultipleSpikeGeneratorGroup([st1(), st2()])

    Note that if two or more spike times fall within the same dt, spikes will stack up
    and come out one per dt until the stack is exhausted. A warning will be generated
    if this happens.
    
    If a clock is provided, updates of the group will be synchronised with
    that clock, otherwise the standard clock guessing procedure will be used
    (see :func:`~brian.clock.guess_clock` in the :mod:`~brian.clock` module).
    
    :class:`SpikeGeneratorGroup`
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Called as::
    
        SpikeGeneratorGroup(N,spiketimes[,clock])
    
    where N is the number of neurons in the group, and spiketimes is a spike
    container, whose elements are tuples (i,t) meaning neuron i fires at
    time t. Pairs (i,t) need to be sorted in time unless spiketimes is a tuple
    or list. For example::
    
        from math import random
        def spikefirer(N,lower,upper):
            nexttime = random.uniform(lower,upper)
            while True:
                yield (random.randint(0,N-1),nexttime)
                nexttime = nexttime + random.uniform(lower,upper)
        G = SpikeGeneratorGroup(10,uniform_isi(10,0*msecond,10*msecond))
    
    would give a neuron group P with 10 neurons, where a random one of the neurons fires 
    with an interval between spikes which is uniform in (0ms, 10ms). If spiketimes is
    callable, it will be called when the group is reinitialised. If you provide
    a generator rather than a callable object, reinitialising the group will
    not reinitialise the generator.
    
    Note that if a neuron fires more than one spike in a given interval dt, additional
    spikes will be discarded.
    
    If a clock is provided, updates of the group will be synchronised with
    that clock, otherwise the standard clock guessing procedure will be used
    (see :func:`~brian.clock.guess_clock` in the :mod:`~brian.clock` module).
    
    :class:`PulsePacket`
    ~~~~~~~~~~~~~~~~~~~~
    
    Fires a Gaussian distributed packet of n spikes with given spread, called as::
    
        PulsePacket(t,n,sigma[,clock])
        
    You can change the parameters by calling the method ``generate(t,n,sigma)``.
    
    If a clock is provided, updates of the group will be synchronised with
    that clock, otherwise the standard clock guessing procedure will be used
    (see :func:`~brian.clock.guess_clock` in the :mod:`~brian.clock` module).
    """
    
    from network import Network
    from monitor import SpikeMonitor
    from clock import reinit_default_clock,Clock
    
    # helper function for running a simple network
    def mininet(grouptype,*args,**kwds):
        reinit_default_clock()
        G = grouptype(*args,**kwds)
        M = SpikeMonitor(G,True)
        net = Network(G,M)
        net.run(5*msecond)
        reinit_default_clock()
        return M.spikes

    # run mininet twice to see if it handles reinit() correctly
    def mininet2(grouptype,*args,**kwds):
        reinit_default_clock()
        G = grouptype(*args,**kwds)
        M = SpikeMonitor(G,True)
        net = Network(G,M)
        net.run(5*msecond)
        spikes1 = M.spikes
        net.reinit()
        net.run(5*msecond)
        spikes2 = M.spikes
        reinit_default_clock()
        return (spikes1,spikes2)
    
    # check multiple spike generator group with lists
    spiketimes = [[0*msecond, 2*msecond, 4*msecond],
                  [1*msecond, 3*msecond]]
    spikes = mininet(MultipleSpikeGeneratorGroup,spiketimes)
    def test1(spikes):
        self.assert_(len(spikes)==5)
        i,t = zip(*spikes) # zip(*...) is the inverse of zip, so i is the ordered list of neurons that fired, and t is the ordered list of times
        self.assert_(i==(0,1,0,1,0)) # check that the order of neuron firings is correct
        for s1,s2 in enumerate(t):
            self.assert_(is_approx_equal(s1*msecond,s2)) # the firing times are (0,1,2,3,4)ms
    test1(spikes)
    
    # check that given a different clock it works as expected, wrap in a function to stop magic functions from
    # picking up the clock objects we define here
    def testwithclock():
        spikes = mininet(MultipleSpikeGeneratorGroup,spiketimes,clock=Clock(dt=0.1*msecond))
        test1(spikes)
        spikes = mininet(MultipleSpikeGeneratorGroup,spiketimes,clock=Clock(dt=2*msecond))
        self.assert_(len(spikes)==5)
        i,t = zip(*spikes) # zip(*...) is the inverse of zip, so i is the ordered list of neurons that fired, and t is the ordered list of times
        for s1,s2 in zip([0,2,2,4,4],t):
            self.assert_(is_approx_equal(s1*msecond,s2)) # the firing times are (0,2,2,4,4)ms
    testwithclock()
        
    # check multiple spike generator group with generators
    def st1():
        yield 0*msecond
        yield 2*msecond
        yield 4*msecond
    def st2():
        yield 1*msecond
        yield 3*msecond
    spikes = mininet(MultipleSpikeGeneratorGroup,[st1(),st2()])
    test1(spikes)
    
    # check reinit
    spikes1, spikes2 = mininet2(MultipleSpikeGeneratorGroup,[st1,st2])
    test1(spikes1)
    test1(spikes2)
    
    # spike generator with list
    spiketimes = [(0,0*msecond),(1,1*msecond),(0,2*msecond),(1,3*msecond),(0,4*msecond) ]
    spikes = mininet(SpikeGeneratorGroup,2,spiketimes)
    test1(spikes)
    
    # check that it works with a clock
    def testwithclock():
        spikes = mininet(SpikeGeneratorGroup,2,spiketimes,clock=Clock(dt=0.1*msecond))
        test1(spikes)
        spikes = mininet(SpikeGeneratorGroup,2,spiketimes,clock=Clock(dt=2*msecond))
        self.assert_(len(spikes)==5)
        i,t = zip(*spikes) # zip(*...) is the inverse of zip, so i is the ordered list of neurons that fired, and t is the ordered list of times
        for s1,s2 in zip([0,2,2,4,4],t):
            self.assert_(is_approx_equal(s1*msecond,s2)) # the firing times are (0,2,2,4,4)ms
    testwithclock()
    
    # spike generator with generator
    def sg():
        yield (0,0*msecond)
        yield (1,1*msecond)
        yield (0,2*msecond)
        yield (1,3*msecond)
        yield (0,4*msecond)
    spikes = mininet(SpikeGeneratorGroup,2,sg())
    test1(spikes)
    
    # spike generator reinit
    spikes1, spikes2 = mininet2(SpikeGeneratorGroup,2,sg)
    test1(spikes1)
    test1(spikes2)
    
    # pulse packet with 0 spread
    spikes = mininet(PulsePacket,2.5*msecond,10,0*msecond)
    self.assert_(len(spikes)==10)
    i,t = zip(*spikes)
    for s in t:
        self.assert_(is_approx_equal(2.5*msecond,s))
    # do not attempt to verify the behaviour of PulsePacket here, this is
    # an interface test only

class MultipleSpikeGeneratorGroup(NeuronGroup):
    """Emits spikes at given times
    
    **Initialised as:** ::
    
        MultipleSpikeGeneratorGroup(spiketimes[,clock])
    
    where 
    ``spiketimes`` is a list of spike time containers, one for each neuron in the group,
    although note that elements of ``spiketimes`` can also be callable objects which
    return spike time containers if you want to be able to reinitialise (see below).
    At it's simplest, ``spiketimes`` could be a list of lists, where ``spiketimes[0]`` contains
    the firing times for neuron 0, ``spiketimes[1]`` for neuron 1, etc. But, any iterable
    object can be passed, so ``spiketimes[0]`` could be a generator for example. Each
    spike time container should be sorted in time.
    
    Note that if two or more spike times fall within the same ``dt``, spikes will stack up
    and come out one per dt until the stack is exhausted. A warning will be generated
    if this happens.

    Also note that if you pass a generator, then reinitialising the group will not have the
    expected effect because a generator object cannot be reinitialised. Instead, you should
    pass a callable object which returns a generator, this will be called each time the
    object is reinitialised by calling the ``reinit()`` method.
        
    **Sample usage:** ::
    
        spiketimes = [[1*msecond, 2*msecond]]
        P = MultipleSpikeGeneratorGroup(spiketimes)
    """
    def __init__(self,spiketimes,clock=None):
        """Pass spiketimes
        
        spiketimes is a list of lists, one list for each neuron
        in the group. Each sublist consists of the spike times.
        """
        clock = guess_clock(clock)
        thresh = MultipleSpikeGeneratorThreshold(spiketimes)
        NeuronGroup.__init__(self,len(spiketimes),model=LazyStateUpdater(),threshold=thresh,clock=clock)
    def reinit(self):
        super(MultipleSpikeGeneratorGroup,self).reinit()
        self._threshold.reinit()        
    def __repr__(self):
        return "MultipleSpikeGeneratorGroup"

class MultipleSpikeGeneratorThreshold(Threshold):
    def __init__(self,spiketimes):
        self.set_spike_times(spiketimes)
    def reinit(self):
        # spiketimes is a container where each element is an iterable container of spike times for
        # each neuron. We store the iterator for each neuron, and the next spike time if it exists
        # or None if there are no spikes or no more spikes
        def makeiter(obj):
            if callable(obj): return iter(obj())
            return iter(obj)
        self.spiketimeiter = [makeiter(st) for st in self.spiketimes]
        self.nextspiketime = [None for st in self.spiketimes]
        for i in range(len(self.spiketimes)):
            try:
                self.nextspiketime[i] = self.spiketimeiter[i].next()
            except StopIteration:
                pass
    def set_spike_times(self,spiketimes):
        self.spiketimes = spiketimes
        self.reinit()
    def __call__(self,P):
        firing = zeros(len(self.spiketimes))
        # it is the iterator for neuron i, and nextspiketime is the stored time of the next spike
        for it, nextspiketime, i in zip(self.spiketimeiter,self.nextspiketime,range(len(self.spiketimes))):
            # Note we use approximate equality testing because the clock t+=dt mechanism accumulates errors
            if nextspiketime is not None and is_approx_less_than_or_equal(nextspiketime,P.clock.t):
                firing[i]=1
                try:
                    nextspiketime = it.next()
                    if is_approx_less_than_or_equal(nextspiketime,P.clock.t):
                        log_warn('brian.MultipleSpikeGeneratorThreshold', 'Stacking multiple firing times')
                except StopIteration:
                    nextspiketime = None
                self.nextspiketime[i] = nextspiketime
        return where(firing)[0]

class SpikeGeneratorGroup(NeuronGroup):
    """Emits spikes at given times
    
    Initialised as::
    
        SpikeGeneratorGroup(N,spiketimes[,clock])
    
    with arguments:
    
    ``N``
        The number of neurons in the group.
    ``spiketimes``
        An object specifying which neurons should fire and when. It can be a container
        such as a ``list``, containing tuples ``(i,t)`` meaning neuron ``i`` fires at
        time ``t``, or a callable object which returns such a container (which
        allows you to use generator objects, see below). If ``spiketimes`` is not
        a list or tuple, the pairs ``(i,t)`` need to be sorted in time.
    ``clock``
        An optional clock to update with (omit to use the default clock).
    
    **Sample usages**
    
    The simplest usage would be a list of pairs ``(i,t)``::
    
        spiketimes = [(0,1*ms), (1,2*ms)]
        SpikeGeneratorGroup(N,spiketimes)
    
    A more complicated example would be to pass a generator::

        import random
        def nextspike():
            nexttime = random.uniform(0*ms,10*ms)
            while True:
                yield (random.randint(0,9),nexttime)
                nexttime = nexttime + random.uniform(0*ms,10*ms)
        P = SpikeGeneratorGroup(10,nextspike())
    
    This would give a neuron group ``P`` with 10 neurons, where a random one
    of the neurons fires at an average rate of one every 5ms.
    
    **Notes**
    
    Note that if a neuron fires more than one spike in a given interval ``dt``, additional
    spikes will be discarded. If you want them to stack, consider using the less efficient
    :class:`MultipleSpikeGeneratorGroup` object instead. A warning will be issued if this
    is detected.
    
    Also note that if you pass a generator, then reinitialising the group will not have the
    expected effect because a generator object cannot be reinitialised. Instead, you should
    pass a callable object which returns a generator. In the example above, that would be
    done by calling::
    
        P = SpikeGeneratorGroup(10,nextspike)
        
    Whenever P is reinitialised, it will call ``nextspike()`` to create the required spike
    container.
    """
    def __init__(self,N,spiketimes,clock=None):
        clock = guess_clock(clock)
        thresh = SpikeGeneratorThreshold(N,spiketimes)
        NeuronGroup.__init__(self,N,model=LazyStateUpdater(),threshold=thresh,clock=clock)
    def reinit(self):
        super(SpikeGeneratorGroup,self).reinit()
        self._threshold.reinit()
    def __repr__(self):
        return "SpikeGeneratorGroup"

class SpikeGeneratorThreshold(Threshold):
    def __init__(self,N,spiketimes):
        self.set_spike_times(N,spiketimes)
    def reinit(self):
        def makeiter(obj):
            if callable(obj): return iter(obj())
            return iter(obj)
        self.spiketimeiter = makeiter(self.spiketimes)
        try:
            self.nextspikenumber, self.nextspiketime = self.spiketimeiter.next()
        except StopIteration:
            self.nextspiketime = None
            self.nextspikenumber = 0
    def set_spike_times(self,N,spiketimes):
        # N is the number of neurons, spiketimes is an iterable object of tuples (i,t) where
        # t is the spike time, and i is the neuron number. If spiketimes is a list or tuple,
        # then it will be sorted here.
        if isinstance(spiketimes,(list,tuple)):
            spiketimes = sorted(spiketimes,key=itemgetter(1))
        self.spiketimes = spiketimes
        self.N = N
        self.reinit()
    def __call__(self,P):
        firing = zeros(self.N)
        while self.nextspiketime is not None and is_approx_less_than_or_equal(self.nextspiketime,P.clock.t):
            if firing[self.nextspikenumber]:
                log_warn('brian.SpikeGeneratorThreshold', 'Discarding multiple overlapping spikes')
            firing[self.nextspikenumber] = 1
            try:
                self.nextspikenumber, self.nextspiketime = self.spiketimeiter.next()
            except StopIteration:
                self.nextspiketime = None
        return where(firing)[0]

# The output of this function is fed into SpikeGeneratorGroup, consisting of
# time sorted pairs (t,i) where t is when neuron i fires
@check_units(t=second,n=1,sigma=second)
def PulsePacketGenerator(t,n,sigma):
    times = [pyrandom.gauss(t,sigma) for i in range(n)]
    times.sort()
    neuron = range(n)
    pyrandom.shuffle(neuron)
    return zip(neuron,times)

class PulsePacket(SpikeGeneratorGroup):
    """
    Fires a Gaussian distributed packet of n spikes with given spread
    
    **Initialised as:** :: 
    
        PulsePacket(t,n,sigma[,clock])
        
    with arguments:
    
    ``t``
        The mean firing time
    ``n``
        The number of spikes in the packet
    ``sigma``
        The standard deviation of the firing times.
    ``clock``
        The clock to use (omit to use default or local clock)
    
    **Methods**
    
    This class is derived from :class:`SpikeGeneratorGroup` and has all its
    methods as well as one additional method:
    
    .. method:: generate(t,n,sigma)
    
        Change the parameters and/or generate a new pulse packet.
    """
    @check_units(t=second,n=1,sigma=second)
    def __init__(self,t,n,sigma,clock=None):
        self.clock = guess_clock(clock)
        self.generate(t,n,sigma)
    def reinit(self):
        super(PulsePacket,self).reinit()
        self._threshold.reinit()
    @check_units(t=second,n=1,sigma=second)
    def generate(self,t,n,sigma):
        SpikeGeneratorGroup.__init__(self,n,PulsePacketGenerator(t,n,sigma),self.clock)
    def __repr__(self):
        return "Pulse packet neuron group"

def _test():
    import doctest
    doctest.testmod()

if __name__=="__main__":
    _test()
