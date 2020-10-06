#!/usr/bin/env python
"""
setup_win.py file from src_old
TODO write setup_win, setup_ux, setup_os files for pure installation of precompiled shared libraries
TODO make this work with precompilation
"""

from distutils.core import setup, Extension
import numpy

try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

eigen_include = '3rdParty/Eigen'

# SimPulseqSBB_module = Extension('_SimPulseqSBB', sources=['SimPulseqSBB_wrap.cxx', 'SimPulseqSBB.cpp',
#                                                           'SimulationParameters.cpp', 'ExternalSequence.cpp'],
#                                 include_dirs=[numpy_include, numpy_include + '/numpy', eigen_include],
#                                 language="c++",
#                                 )

setup(name='SimPulseqSBB',
      version='0.1',
      author="K Heinecke",
      description="SimPulseqSBB",
      #ext_modules=[SimPulseqSBB_module],
      py_modules=["SimPulseqSBB"],
      )