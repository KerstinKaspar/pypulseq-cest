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
np_path_np = np_path / 'numpy'


def linux_setup(eigen_path: Path, np_path: Path):
    # noinspection PyTypeChecker
    SimPulseqSBB_module = Extension(name='_pySimPulseqSBB',
                                    sources=['pySimPulseqSBB.i', 'SimPulseqSBB.cpp', 'SimulationParameters.cpp',
                                             'ExternalSequence.cpp'],
                                    extra_compile_args=['-Xpreprocessor', '-fopenmp', '-fPIC', '-fpermissive'],
                                    include_dirs=[np_path, np_path_np, eigen_path],
                                    extra_link_args=['-lgomp'],
                                    swig_opts=['-c++'],
                                    language="c++",
                                    )

    setup(name='pySimPulseqSBB',
          version='0.1',
          author="K Heinecke",
          author_email='k.heinecke@campus.tu-berlin.de',
          description="Python package to use the C++ code SimPulseqSBB for pulseq-CEST simulations.",
          ext_modules=[SimPulseqSBB_module],
          py_modules=["pySimPulseqSBB"],
          )


def windows_setup(eigen_path: Path, np_path: Path):
    # noinspection PyTypeChecker
    SimPulseqSBB_module = Extension(name='_pySimPulseqSBB',
                                    sources=['pySimPulseqSBB.i', 'SimPulseqSBB.cpp', 'SimulationParameters.cpp',
                                             'ExternalSequence.cpp'],
                                    include_dirs=[eigen_path, np_path, np_path_np],
                                    swig_opts=['-c++'],
                                    language = 'c++'
    )

    setup(name='pySimPulseqSBB',
          version='0.1',
          author="K. Heinecke",
          author_email='k.heinecke@campus.tu-berlin.de',
          description="Python package to use the C++ code SimPulseqSBB for pulseq-CEST simulations.",
          ext_modules=[SimPulseqSBB_module],
          py_modules=["pySimPulseqSBB"],
          )


def sim_setup(eigen_path: Path, np_path: Path, extra_compile_args=None, extra_link_args=None):
    if extra_link_args is None:
        extra_link_args = []
    if extra_compile_args is None:
        extra_compile_args = []
    # noinspection PyTypeChecker
    SimPulseqSBB_module = Extension(name='_pySimPulseqSBB',
                                    sources=['pySimPulseqSBB.i', 'SimPulseqSBB.cpp', 'SimulationParameters.cpp',
                                             'ExternalSequence.cpp'],
                                    include_dirs=[eigen_path, np_path, np_path_np],
                                    extra_compile_args=extra_compile_args,
                                    extra_link_args=extra_link_args,
                                    swig_opts=['-c++'],
                                    language = 'c++'
    )

    setup(name='pySimPulseqSBB',
          version='0.1',
          author="K. Heinecke",
          author_email='k.heinecke@campus.tu-berlin.de',
          description="Python package to use the C++ code SimPulseqSBB for pulseq-CEST simulations.",
          ext_modules=[SimPulseqSBB_module],
          py_modules=["pySimPulseqSBB"],
          )


def swig_setup():
    if platform == "linux":
        print("Initiating setup for Linux operating system.")
        sim_setup(eigen_path=eigen_path,
                  np_path=np_path,
                  extra_compile_args=['-Xpreprocessor', '-fopenmp'],  # '-fPIC', '-fpermissive'],
                  extra_link_args=['-lgomp'])
        # linux_setup(eigen_path=eigen_path, np_path=np_path)

    elif platform == "win32":
        print("Initiating setup for Windows 32bit operating system.")
        # windows_setup(eigen_path=eigen_path, np_path=np_path)
        sim_setup(eigen_path=eigen_path,
                  np_path=np_path,
                  extra_compile_args=['-Xpreprocessor', '-fopenmp'],
                  extra_link_args=[])

    elif platform == "win64":
        print("Initiating setup for Windows 64bit operating system.")
        # windows_setup(eigen_path=eigen_path, np_path=np_path)
        sim_setup(eigen_path=eigen_path,
                  np_path=np_path,
                  extra_compile_args=['-Xpreprocessor', '-fopenmp'],
                  extra_link_args=[])

    elif platform == "darwin":  # Mac OS
        print("Initiating setup for OS X operating system.")
        sim_setup(eigen_path=eigen_path,
                  np_path=np_path,
                  extra_compile_args=['-Xpreprocessor', '-fopenmp'],
                  extra_link_args=['-lomp'])
    else:
        print("Setup for operating system", platform, "not implemented.")


if __name__ == "__main__":
    swig_setup()




