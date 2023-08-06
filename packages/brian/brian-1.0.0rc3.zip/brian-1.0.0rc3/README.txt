============ B R I A N =============================
A clock-driven simulator for spiking neural networks
====================================================

Version: 1.0.0 (release candidate 3)
Authors:
	Romain Brette
		http://www.di.ens.fr/~brette/index.html
	Dan Goodman
		http://neuro.di.ens.fr/tiki-index.php?page=Dan+Goodman

==== Installation ==========================================================

Requirements: Python (version >= 2.5), the following modules:

* numpy
* scipy
* pylab
* sympy

Windows: run the installer exe file

Others: run 'python setup.py install' from the download folder.

==== Extras ================================================================

Included in the extras download are:

docs
	Documentation for Brian - unfinished - including tutorials.

docs/api
	Automatically generated API documentation for Brian. It's not very
	readable yet, but it's up to date.

examples
	Examples of using Brian, these serve as supplementary documentation.
	
tutorials
	Fully worked through tutorials on using Brian. These can be read
	through in the documentation too.	

benchmarks
	Currently includes Scilab and Matlab versions of the CUBA and COBA
	examples, and a C++ version of the CUBA example.

==== Usage and Documentation ===============================================

See the documentation in the extras download.

==== Changes ===============================================================

Version 1.0.0 RC2 to version 1.0.0 RC3:

* Small bugfixes

Version 1.0.0 RC1 to version 1.0.0 RC2:

* Documentation system now much better, using Sphinx, includes
  cross references, index, etc.
* Added VariableReset
* Added run_all_tests()
* numpywrappers module added, but not in global namespace
* Quantity comparison to zero doesn't check units (positivity/negativity)

Version 1.0.0 beta to version 1.0.0 RC1:

* Connection: connect_full allows a functional weight argument (like connect_random)
* Short-term plasticity:
  In Connection: 'modulation' argument allows modulating weights by a state
  variable from the source group (see examples).
* HomogeneousCorrelatedSpikeTrains: input spike trains with exponential correlations.
* Network.stop(): stops the simulation (can be called by a user script)
* PopulationRateMonitor: smooth_rate method
* Optimisation of Euler code: use compile=True when initialising NeuronGroup
* More examples
* Pickling now works (saving and loading states)
* dot(a,b) now works correctly with qarray's with homogeneous units
* Parallel simulations using Parallel Python (independent simulations only)
* Example of html inferfaces to Brian scripts using CherryPy
* Time dependence in equations (see phase_locking example)
* SpikeCounter and PopulationSpikeCounter