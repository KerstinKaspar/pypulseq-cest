#!/usr/bin/env python
"""
setup.py
    Setup definitions for distutils package creation
"""

from setuptools import setup, Extension
import numpy
from pathlib import Path

try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

# defining paths to the desired files
eigen_path = Path('Eigen')
np_path = Path(numpy_include)
np_path_np = np_path / 'numpy'


SimPulseqSBB_module = Extension(name='_pySimPulseqSBB',
                                sources=['pySimPulseqSBB.i', 'SimulationParameters.cpp',
                                         'ExternalSequence.cpp', 'BMCSim.cpp'],
                                include_dirs=[eigen_path, np_path, np_path_np],
                                swig_opts=['-c++'],
                                language='c++'
                                )

setup(name='pySimPulseqSBB',
      version='0.1',
      author="K. Heinecke",
      author_email='k.heinecke@campus.tu-berlin.de',
      description="Python package to use the C++ code SimPulseqSBB for pulseq-CEST simulations.",
      ext_modules=[SimPulseqSBB_module],
      py_modules=["pySimPulseqSBB", 'parser'],
      )



