# Simulation tool and seq-file preparation for CEST saturation blocks

This repository contains the necessary code and tools to build CEST saturation blocks with 
[pypulseq](https://github.com/imr-framework/pypulseq), which is a python adaption of the matlab-based 
[pulseq](https://github.com/pulseq/pulseq) project. The documentation of the **pulseq** open file format for MR 
sequences can be found [here](https://pulseq.github.io/specification.pdf). 

## IMPORTANT: How to clone this repository
As the [pypulseq-cest]() repository includes a library, which is included as a 
[GitHub submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules), you should clone this repository using the
following command:
```
git clone --recurse-submodules https://github.com/KerstinHut/pypulseq-cest.git
```
This ensures that the [pulseq-cest-library](https://github.com/kherz/pulseq-cest-library) will we cloned as well.

## Installation
To be able to create and simulate your own CEST saturation blocks using [pypulseq-cest](), you need to install the
[pypulseq](https://github.com/imr-framework/pypulseq), [numpy](https://numpy.org/), 
[matlpotlib](https://matplotlib.org/) and [yaml](https://yaml.org/) python packages as well as the C++ solver. 
This is explained in detail in a separate [readme file](sim/src/readme.md), which can be found in the 
[sim/src](sim/src) subfolder. 

**Please make sure to read it!**

## Config and seq-file library
All simulations in [pypulseq-cest]() require a *yaml file* that includes all simulation settings and a *seq file*, which
defines the pre-saturation block. An [example seq-file](library/seq_example.seq), an [example yaml file]() as well as an 
[example script](library/write_seq_example.py) to create the [seq_example.seq](library/seq_example.seq) file can be 
found in the [library](library) subfolder. 

Please read the subfolders [readme file](library/readme.md) to learn how to
download further pre-defined and approved pre-saturation schemes and simulation configs.

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
