#!/usr/bin/env python
"""
setup_win.py file from src_old
"""

from distutils.core import setup, Extension
import numpy

try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

eigen_include = '3rdParty/Eigen'

SimPulseqSBB_module = Extension('_SimPulseqSBB', sources=['SimPulseqSBB_wrap.cxx', 'SimPulseqSBB.cpp',
                                                     'SimulationParameters.cpp', 'ExternalSequence.cpp'],
                               #extra_compile_args=['-Xpreprocessor', '-fopenmp'], #, '-fPIC'
                            include_dirs=[numpy_include, numpy_include + '/numpy', eigen_include],
                            # extra_link_args=['-lomp'],
                                # swig_opts=['-threads'],
                               language="c++",
                              )




setup(name='SimPulseqSBB',
      version='0.1',
      author="K Heinecke",
      description="SimPulseqSBB",
      ext_modules=[SimPulseqSBB_module],
      py_modules=["SimPulseqSBB"],
      )
