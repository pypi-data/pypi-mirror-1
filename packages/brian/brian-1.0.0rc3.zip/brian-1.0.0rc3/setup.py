"""Setup script for Brian

There are two types of distributions, source and binary distributions.

At the moment, there's not much difference for us because we have no
C/C++ extensions, but this will change later on. The source distribution
is installed by running "python setup.py install" after downloading the
file. The binary distribution is installed by running the exe file, or
on Unix/Linux by installing the RPM file (although we can't create this
on Windows).

To update the distribution files, run:

python setup.py bdist_wininst
python setup.py sdist --formats=gztar,zip

At the moment, the distribution includes all the .py files in the Brian
folder, and in the Brian/utils folder, and the brian_unit_prefs.py file
in the base folder. To add a new folder, change the 'packages' variable
below, and to add a new single module, change the 'py_modules' variable.

I didn't include the Examples in the distribution because they are not
really a Python module to be loaded. I thought we could just distribute
those files in a separate zip/gz file.
"""

from distutils.core import setup

version = '1.0.0rc3'

# the create_extras.py script will automatically generate an extras files
# containing the following files
extras_folders = ['tutorials/tutorial1_basic_concepts/*.py',
                  'tutorials/tutorial2_connections/*.py',
                  'examples/*.py',
                  'benchmarks/*.sce', 'benchmarks/*.m', 'benchmarks/*.cpp',
                  'docs/*.*', 'docs/_images/*.jpg', 'docs/api/*.*',
                  'docs/_sources/*.*', 'docs/_static/*.*' ]

if __name__=="__main__":
    setup(name='brian',
      version=version,
      py_modules=['brian_unit_prefs','brian_no_units','brian_no_units_no_warnings'],
      packages=['brian', 'brian.utils', 'brian.library', 'brian.tests'],
      url='http://brian.di.ens.fr/',
      description='A clock-driven simulator for spiking neural networks',
      author='Romain Brette, Dan Goodman',
      author_email='Romain.Brette at ens.fr'
      )