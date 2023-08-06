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
Generation of correlated spike trains.
Based on the article: Brette, R. (2007). Generation of correlated spike trains.
'''
from threshold import PoissonThreshold,HomogeneousPoissonThreshold
from neurongroup import NeuronGroup
from equations import Equations
from scipy.special import erf
from scipy.optimize import newton
from scipy import exp,pi,linalg,diag,isreal,array,dot
from units import check_units,hertz,second
from utils.circular import SpikeContainer

__all__=['rectified_gaussian','inv_rectified_gaussian','HomogeneousCorrelatedSpikeTrains',\
         'CorrelatedSpikeTrains']

# Contributor information
__credits__=dict(
author='Romain Brette (brette@di.ens.fr)',
date='April 2008',
paper='Brette, R. (2008). Generation of correlated spike trains. Neural Computation (in press)',
url='http://www.di.ens.fr/~brette/papers/Brette2008NC.html'
)

def rectified_gaussian(mu,sigma):
    '''
    Calculates the mean and standard deviation for a rectified Gaussian distribution.
    mu, sigma: parameters of the original distribution
    Returns mur,sigmar: parameters of the rectified distribution
    '''
    a=1.+erf(mu/(sigma*(2**.5)));
    
    mur=(sigma/(2.*pi)**.5)*exp(-0.5*(mu/sigma)**2)+.5*mu*a
    sigmar=((mu-mur)*mur+.5*sigma**2*a)**.5
    
    return (mur,sigmar)

def inv_rectified_gaussian(mur,sigmar):
    '''
    Inverse of the function rectified_gaussian
    '''
    if sigmar==0*sigmar: # for unit consistency
        return (mur,sigmar)
    
    x0=mur/sigmar
    ratio=lambda u,v:u/v
    f=lambda x:ratio(*rectified_gaussian(x,1.))-x0
    y=newton(f,x0*1.1) # Secant method
    sigma=mur/(exp(-0.5*y**2)/((2.*pi)**.5)+.5*y*(1.+erf(y*(2**(-.5)))))
    mu=y*sigma
    
    return (mu,sigma)

class HomogeneousCorrelatedSpikeTrains(NeuronGroup):
    '''
    Correlated spike trains with identical rates and homogeneous exponential correlations.
    Uses Cox processes (Ornstein-Uhlenbeck).
    '''
    @check_units(r=hertz,tauc=second)
    def __init__(self,N,r,c,tauc,clock=None):
        '''
        Initialization:
        r = rate (Hz)
        c = total correlation strength (in [0,1])
        tauc = correlation time constant (ms)
        '''
        # Correction of mu and sigma
        sigmar=(c*r/(2.*tauc))**.5
        mu,sigma=inv_rectified_gaussian(r,sigmar)
        eq=Equations('drate/dt=(mu-rate)/tauc + sigma*xi/tauc**.5 : Hz',mu=mu,tauc=tauc,sigma=sigma)
        NeuronGroup.__init__(self,1,model=eq,threshold=HomogeneousPoissonThreshold(),\
                             clock=clock)
        self.rate=mu
        self.N=N
        self.LS=SpikeContainer(N,1) # Spike storage
        
    def __len__(self):
        # We need to redefine this because it is not the size of the state matrix
        return self.N

    def __getslice__(self,i,j):
        Q=NeuronGroup.__getslice__(self,i,j)
        Q.N=j-i
        return Q

def decompose_correlation_matrix(C,R):
    '''
    Completes the diagonal of C and finds L such that C=LL^T.
    C is matrix of correlation coefficients with unspecified diagonal.
    R is the rate vector.
    C must be symmetric.
    N.B.: The diagonal of C is modified (with zeros).
    '''
    # 0) Remove diagonal entries and calculate D (var_i(x) is should have magnitude r_i^2)
    D=R**2
    C-=diag(diag(C))
    
    # Completion
    # 1) Calculate D^{-1}C
    L=dot(diag(1./D),C)
    
    # 2) Find the smallest eigenvalue
    eigenvals=linalg.eig(L)[0]
    alpha=-min(eigenvals[isreal(eigenvals)])

    # 3) Complete the diagonal with alpha*ri^2
    #alpha=alpha+.01; // avoids bad conditioning problems (uncomment if Cholesky fails)
    C+=diag(alpha*D)
    return linalg.cholesky(C,lower=1)

class CorrelatedSpikeTrains(NeuronGroup):
    '''
    Correlated spike trains with arbitrary rates and pair-wise exponential correlations.
    Uses Cox processes (Ornstein-Uhlenbeck).
    P['rate'] is the vector of (time-varying) rates.
    TO BE TESTED
    '''
    @check_units(tauc=second)
    def __init__(self,N,rates,C,tauc,clock=None):
        '''
        Initialization:
        rates = rates (Hz)
        C = correlation matrix
        tauc = correlation time constant (ms)
        '''
        eq=Equations('''
        rate : Hz
        dy/dt = -y*(1./tauc)+xi/(.5*tauc)**.5 : Hz
        ''')
        NeuronGroup.__init__(self,N,model=eq,threshold=PoissonThreshold(),\
                             clock=clock)
        self._R=array(rates)
        self._L=decompose_correlation_matrix(C.copy(),self._R)

    def update(self):
        # Calculate rates
        self.rate_=self._R+dot(self._L,self.y_)
        NeuronGroup.update(self)
        