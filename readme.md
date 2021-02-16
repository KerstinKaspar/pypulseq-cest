# Simulation tool and seq-file preparation for CEST saturation blocks

This repository contains the necessary code and tools to build CEST saturation blocks with 
[pypulseq](https://github.com/imr-framework/pypulseq), which is a python adaption of the matlab-based 
[pulseq](https://github.com/pulseq/pulseq) project. Please visit [https://pulseq-cest.github.io/](https://pulseq-cest.github.io/) for more information on the project. The documentation of the **pulseq** open file format for MR 
sequences can be found [here](https://pulseq.github.io/specification.pdf). 

## INSTALLATION
MORE INFO ON INSTALLATIONS CAN BE FOUND IN THE [sim/src/readme](sim/src/readme.md)
If your system requirements match the file, you can simply install the precompiled distributions. Should you not find a matching distribution, please refer to the system indeendent installation guide below.
### Windows precompiled installation
- from the [sim/src/compile/dist](sim/src/compile/dist) folder run the following command in the terminal to install into your current python environment:
    - choose the correct executable for your operating system (32 or 64 bit) and python version and replace the filename in the following code
    - if you don't find a suitable executable, please follow the instructions in the **Compilation guide** section below
```
    # example for installation
    easy_install pySimPulseqSBB-1.0.win-amd64-py3.7.exe
``` 
### SYSTEM INDEPENDENT INSTALLATION 
The following installation is recommended. If it should fail or you cannot run it, please follow both instructions in the [sim/src/readme](sim/src/readme.md) and [library/readme](library/readme.md) individually.
### Prerequisites for the system independent installation
To be able to create and simulate your own CEST saturation blocks using [pypulseq-cest](.), you need to install the following python packages:
- [pypulseq](https://github.com/imr-framework/pypulseq)
- [pyYaml](https://yaml.org/) for .yaml file handling 

You also need to have the following installed on your machine:
- [Git](https://git-scm.com/)
- [SWIG](http://www.swig.org/exec.html) (Installation for [Windows link](http://www.swig.org/Doc1.3/Windows.html))
- a working C++ compiler
    - for Windows, you need Visual C++ v.12.0 or higher, e.g. [Microsoft Visual C++ Redistributable](https://visualstudio.microsoft.com/downloads/)

### Installation
If you fulfill the prerequisites, you just need to run the [install.py](install.py) file.
You can do this from the terminal (from this [pypulseq-cest folder](.)):
```
python install.py
```
To avoid permission problems, run it with administrative rights (Windows: start the terminal with administrative rights, Linux: ```sudo python install.py```)
You might need to adapt your python executable, e.g. ```python3```

## Config and seq-file library
All simulations in [pypulseq-cest]() require a *yaml file* that includes all simulation settings and a *seq file*, which
defines the pre-saturation block. An [example seq-file](library/seq_example.seq), an [example yaml file]() as well as an 
[example script](library/write_seq_example.py) to create the [seq_example.seq](library/seq_example.seq) file can be 
found in the [library](library) subfolder. 

You will find further pre-defined and approved pre-saturation schemes and simulation configs in the [pulseq-cest-library](library/pulseq-cest-library)
If you have not successfully used the above installation, please read the subfolders [readme file](library/readme.md) to learn how to
download from the [pulseq-cest-library repository](https://github.com/kherz/pulseq-cest-library).

## Pulseq version compatibility
Since [pypulseq](https://github.com/imr-framework/pypulseq) is producing files of version 1.2, we provide functions 
to create pseudo version 1.3 files and to load files of either of these versions in the 
[sim/utils/seq](sim/utils/seq) subfolder.

You can use the following code to change the 1.2 file into a pseudo 1.3 file:
````python
from sim.utils.seq.conversion import convert_seq_12_to_pseudo_13
convert_seq_12_to_pseudo_13(file_path)
````

To load any sequence file of version 1.2 or 1.3, use:
````python
from sim.utils.seq.read import read_any_version
seq = read_any_version(file_path)
````
