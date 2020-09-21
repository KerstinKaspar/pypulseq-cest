#!/usr/bin/env python
"""
setup.py file for simulation parameters
"""

from distutils.core import setup, Extension

# Third-party modules - we depend on numpy for everything
import numpy

# Obtain the numpy include directory.  This logic works across numpy versions.
try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

SimPulseqSBB_module = Extension('_SimPulseqSBB', sources=['SimPulseqSBB_wrap.cxx',
                                                      'SimPulseqSBB.cpp'],
                               extra_compile_args=['-Xpreprocessor', '-fopenmp'],
                               extra_link_args=['-lomp'], # '-lomp' for Mac,  -lgomp for Linux
                               swig_opts=['-threads'],
                               include_dirs=[numpy_include, numpy_include + '/numpy']
                              )

setup(name='SimPulseqSBB',
      version='0.1',
      author="K Heinecke",
      description="""Definition of simulation parameters""",
      ext_modules=[SimPulseqSBB_module],
      py_modules=["SimPulseqSBB"],
      )
