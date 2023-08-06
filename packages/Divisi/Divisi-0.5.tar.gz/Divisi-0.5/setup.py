#!/usr/bin/env python
#read and understand sphinx's setup.py

"""Divisi: Commonsense Reasoning over Semantic Networks

Divisi is a library for reasoning by analogy and association over semantic networks, 
including common sense knowledge. Divisi uses a sparse higher-order SVD and can help
find related concepts, features, and relation types in any knowledge base that can be
represented as a semantic network. By including common sense knowledge from ConceptNet, 
the results can include relationships not expressed in the original data but related 
by common sense."""
#import ez_setup  I havent written ez_setup yet. but if I had, it would be to install setuptools
#ez_setup.use_setuptools()
from setuptools import setup, Extension
import os, sys
from stat import ST_MTIME

classifiers=[
    'Framework :: Django',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.5',
    'Topic :: Database',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Text Processing :: Linguistic',]

if sys.version_info < (2, 3):
    _setup = setup
    def setup(**kwargs):
        kwargs.pop("classifiers", None)
        return _setup(**kwargs)

### Get the Numpy includes.
_numpy_includes = ''
try:
    import numpy
    _numpy_includes = numpy.get_include()
except ImportError:
    import sys
    _pyver = sys.version_info
    if _pyver[0] <= 2 and _pyver[1] <= 4:
        print """This package requires numpy.

On a Debian / Ubuntu system, you can run:
  sudo apt-get install python-numpy python-dev

Otherwise it will probably suffice to:
  sudo easy_install numpy
"""
        sys.exit(1)


### Update the Cython file, if necessary.
def get_modification_time(filename):
    return os.stat(filename)[ST_MTIME]
try:
    if get_modification_time('svdlib/_svdlib.pyx') > get_modification_time('svdlib/_svdlib.c'):
        try:
                # Try building the Cython file
                print 'Building Cython source'
                from Cython.Compiler.Main import compile
                res = compile('svdlib/_svdlib.pyx')
                if res.num_errors > 0:
                        print "Error building the Cython file."
                        import sys
                        sys.exit(1)
        except ImportError:
                print 'Skipped building the Cython file.'
except OSError:
    print 'Skipped checking the Cython file.'


svdlibc = Extension(
    name='divisi._svdlib',
    sources=[
        'svdlib/_svdlib.c',
        'svdlib/svdwrapper.c',
        'svdlib/las2.c',
        'svdlib/main.c',
        'svdlib/svdlib.c',
        'svdlib/svdutil.c',
        ],
    include_dirs=[_numpy_includes, 'svdlib'],
    )

doclines = __doc__.split("\n")

setup(
    name="Divisi",
    version = "0.5",
    maintainer='MIT Media Lab, Software Agents group',
    maintainer_email='conceptnet@media.mit.edu',     
    url='http://divisi.media.mit.edu/',
    license = "http://www.gnu.org/copyleft/gpl.html",
    platforms = ["any"],
    description = doclines[0],
    classifiers = classifiers,
    long_description = "\n".join(doclines[2:]),
    ext_modules = [svdlibc],
    packages=['divisi'],
#    install_requires=['numpy',],
)
