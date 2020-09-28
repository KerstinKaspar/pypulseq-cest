#!/usr/bin/env python
"""
setup_ext.py file from src
"""

from distutils.core import setup, Extension
import numpy

try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

eigen_include = 'C:/Users/heinec03/PycharmProjects/pypulseq-cest/src/3rdParty/Eigen'

ext_module = Extension('_SimulationParameters2', sources=['SimulationParameters_wrap.cxx',
                                                     'SimulationParameters.cpp', 'ExternalSequence.cpp'],
                               #extra_compile_args=['-Xpreprocessor', '-fopenmp'], #, '-fPIC'
                            include_dirs=[numpy_include, numpy_include + '/numpy', eigen_include],
                            # extra_link_args=['-lomp'],
                                # swig_opts=['-threads'],
                               language="c++",
                              )

setup(name='SimulationParameters2',
      version='0.1',
      author="K Heinecke",
      description="""test""",
      ext_modules=[ext_module],
      py_modules=["SimulationParameters2"],
      )
