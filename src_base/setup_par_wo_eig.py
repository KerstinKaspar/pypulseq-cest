#!/usr/bin/env python
"""
setup_ext.py file from src
"""

from distutils.core import setup, Extension
from distutils.command import build_ext

ext_module = Extension('_SimulationParameters', sources=['SimulationParameters_wrap.cxx',
                                                     'SimulationParameters.cpp', 'ExternalSequence.cpp'],
                               #extra_compile_args=['-Xpreprocessor', '-fopenmp'], #, '-fPIC'
                            # extra_link_args=['-lomp'],
                                # swig_opts=['-threads'],
                               language="c++",
                              )

setup(name='SimulationParameters',
      version='0.1',
      author="K Heinecke",
      description="""test""",
      ext_modules=[ext_module],
      py_modules=["SimulationParameters"],
      )
