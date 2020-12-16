#!/usr/bin/env python
"""
setup.py
    Setup definitions for distutils package creation
TODO write setup_ux, setup_os files for pure installation of precompiled shared libraries
"""

from distutils.core import setup, Extension
import numpy
from sys import platform
from pathlib import Path

try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

# defining paths to the desired files
eigen_path = Path('Eigen')
np_path = Path(numpy_include)


def windows_setup(eigen_path: Path, np_path: Path):
    SimPulseqSBB_module = Extension(name='_pySimPulseqSBB',
                                    sources=['pySimPulseqSBB.i', 'SimPulseqSBB.cpp',
                                                                'SimulationParameters.cpp',
                                                                'ExternalSequence.cpp'],
                                    include_dirs=[eigen_path, np_path, np_path / 'numpy'],
                                    language='c++',
                                    swig_opts=['-c++']
                                    )

    setup(name='pySimPulseqSBB',
          version='0.1',
          author="K. Heinecke",
          author_email='k.heinecke@campus.tu-berlin.de',
          description="Python package to use the C++ code SimPulseqSBB for pulseq-CEST simulations.",
          ext_modules=[SimPulseqSBB_module],
          py_modules=["pySimPulseqSBB"],
          # package_dir={'pypulseq': thirdparty_path.as_posix()},  #  something like this to move the pypulseq folder
          # packages=["pyparams", "pypulseq", 'pypulseq.Sequence', 'pypulseq.utils', 'pypulseq.utils.SAR', 'pypulseq.cest_util']
          )


if platform == "linux":
    print("Initiating setup for Linux operating system.")

elif platform == "win32":
    print("Initiating setup for Windows 32bit operating system.")
    windows_setup(eigen_path=eigen_path, np_path=np_path)

elif platform == "win64":
    print("Initiating setup for Windows 64bit operating system.")
    windows_setup(eigen_path=eigen_path, np_path=np_path)

elif platform == "darwin":  # Mac OS
    print("Initiating setup for OS X operating system.")
else:
    print("Setup for operating system", platform, "not implemented.")




