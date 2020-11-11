## Installation
This simulation tool can run a solver in C++ code, for which the installation of the pre-compiled python distribution is necessary.
Alternatively, if [Swig](http://www.swig.org/) and [Visual C++](https://support.microsoft.com/de-de/help/2977003/the-latest-supported-visual-c-downloads) are installed, the compilation and installation might be preferrable, see **Compilation guide** section below.
If all fails, you will find some "dumb" distributions (operating system dependent) that you can unpack into your python environment **Lib/site-packages* similar to the structure of the compressed folder.

## Distribution Installation guide:
### Windows
- from the *pulseq-cest-sim/src/dist* folder run the following command in the terminal to install into your current python environment:
    - choose the correct executable for your operating system (32 or 64 bit) and python version and replace the filename in the following code
    - if you don't find a suitable executable, please follow the instructions in the **Compilation guide** section below
```
    # example for installation
    easy_install pySimPulseqSBB-1.0.win-amd64-py3.7.exe
``` 

### Linux
not yet built, please refer to the **Compilation guide** below
### Mac
not yet built, please refer to the **Compilation guide** below

## Compilation guide
- Prerequisites: 
    - [Swig](http://www.swig.org/)
    - for Windows: [Visual C++](https://support.microsoft.com/de-de/help/2977003/the-latest-supported-visual-c-downloads) min. v12.0
- to install the packages run the following command in the terminal from the [pulseq-cest-sim/src/](pulseq-cest-sim/src/) folder:
```
    python setup.py build_dist --inplace
    python setup.py install
```

- to build an executable for your distribution and python version:
```
    python setup.py bdist --format=wininst
```

- to build a compressed "dumb" distribution folder (compiled python packages that hav to be unpacked into the environment library):
```
    python setup.py bdist
```