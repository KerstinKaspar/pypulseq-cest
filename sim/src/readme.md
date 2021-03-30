## Installation
This simulation tool can run a solver in C++ code, for which the installation of the pre-compiled python distribution is necessary.

**If you haven't already done so, try running the install according to the [pypulseq-cest main readme](../../readme.md)**

Alternatively, if [Swig](http://www.swig.org/) and [Visual C++](https://support.microsoft.com/de-de/help/2977003/the-latest-supported-visual-c-downloads) are installed, the compilation and installation might be preferrable, see **Compilation guide** section below.
If all fails, you will find some "dumb" distributions (operating system dependent) that you can unpack into your python environment **site-packages* similar to the structure of the compressed folder.

## Distribution Installation guide:
Please refer to the [pypulseq-cest main readme](../../readme.md)

## Compilation guide
You now need to have the following installed on your machine:
- [Git](https://git-scm.com/)
- [SWIG](http://www.swig.org/exec.html) (Installation for [Windows link](http://www.swig.org/Doc1.3/Windows.html))
- a working C++ compiler
    - for Linux, this comes with your operating system
    - for Windows, you need Visual C++ v.12.0 or higher, e.g. [Microsoft Visual C++ Redistributable](https://visualstudio.microsoft.com/downloads/)
- to install the packages run the following command in the terminal from the [src/compile](src/compile) folder:
    - if you are a linux user, try adding the ```sudo``` pre-command or the ```--user``` post-command.
```
    python setup.py build_ext --inplace
    python setup.py install
```

- to build a wheel distribution for your operating system and python version:
```
    python setup.py build_ext --inplace
    python setup.py bdist_wheel
```
- to build a zipped distribution for your operating system and python version:
```
    python setup.py build_ext --inplace
    python setup.py bdist
```
