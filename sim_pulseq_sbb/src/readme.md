# Installing the python module
This simulation tool can run a solver in C++ code, for which the following is necessary:
## Installation guide:
The C++ code is precompiled into a shared library such that it should suffice to install the package according to your operating system. Should you still need to compile the files for yourself, see **Compilation guide** section below.
### Windows
- from this *pypulseq_cest/src* folder run the following command in the terminal:
    - *(you may have to substitute python with your python version, e.g. python3)*
```
    python setup_win.py install
``` 

### Linux
- from this *pypulseq_cest/src* folder run the following command in the terminal:
    - *(you may have to substitute python with your python version, e.g. python3)*
```
    sudo python setup_ux.py install
``` 
### Mac
**???**
- from this *pypulseq_cest/src* folder run the following command in the terminal:
    - *(you may have to substitute python with your python version, e.g. python3)*
```
    python setup_ux.py install
``` 

## Compilation guide
### Windows
- Prerequisites: 
    - [Swig](http://www.swig.org/)
    - [Visual C++](https://support.microsoft.com/de-de/help/2977003/the-latest-supported-visual-c-downloads) min. v12.0
- from the *pypulseq_cest/src/compile* folder run the following command in the terminal:
    - *(you may have to substitute python with your python version, e.g. python3)*
```
    swig -c++ -python SimPulseqSBB.i 
    python setup_win.py build_ext --inplace
    python setup_win.py install
```
### Linux
- Prerequisites: 
    - [Swig](http://www.swig.org/)
    - gpp compiler should be installed by default
- from the *pypulseq_cest/src/compile* folder run the following command in the terminal:
    - *(you may have to substitute python with your python version, e.g. python3)*
```
    swig -c++ -python SimPulseqSBB.i 
    python setup_ux.py build_ext --inplace
    python setup_ux.py install
```
### Mac
**???**
- Prerequisites: 
    - [Swig](http://www.swig.org/)
- from the *pypulseq_cest/src/compile* folder run the following commands in the terminal:
    - *(you may have to substitute python with your python version, e.g. python3)*
```
    swig -c++ -python SimPulseqSBB.i 
    python setup.py build_ext --inplace
    python setup_os.py install
```
