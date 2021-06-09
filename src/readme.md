# Manual Installation Guide

**If you haven't already done so, try running the installation via *setup.py* file according to the general
[pypulseq-cest readme](../readme.md).**


### Prerequisites 
1. The [BMCTool package](https://pypi.org/project/BMCTool/) has to be installed. This can be done by running
`pip install bmctool`. Using pip ensures that the required [pypulseq package](https://pypi.org/project/pypulseq/)
and [pyYaml package](https://pypi.org/project/PyYAML/) are installed as well.
2. The following programs have to be installed on your computer:
   - [Git](https://git-scm.com/)
   - [SWIG](http://www.swig.org/exec.html) (Installation for [Windows](http://www.swig.org/Doc1.3/Windows.html))
   - a working C++ compiler
     - for **Linux**, this comes with your operating system
     - for **Windows**, you need Visual C++ v.12.0 or higher, e.g. [Microsoft Visual C++ Redistributable](https://visualstudio.microsoft.com/downloads/)
  
### Manual Installation
To manually install the pypulseq-cest code, please follow these steps:


1) From this (**[src](.)**) directory, install the *pypulseq_cest* package by running by running the following commands in the terminal (*linux users might 
   need to add the `sudo` pre-command or `--user` post-command*)
```
    python setup_pypulseq_cest.py. install
```

2) switch to the **[src/compile](compile)** directory
3) install the *pySimPulseqSBB* package by running the following commands in the terminal (*linux users might need to 
   add the `sudo` pre-command or `--user` post-command*)

```
    python setup.py build_ext --inplace
    python setup.py install
```

**PLEASE NOTE THAT THIS IS NOT THE _setup.py_ FILE FROM THE ROOT DIRECTORY**
