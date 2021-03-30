# Simulation tool and seq-file preparation for CEST saturation blocks

This repository contains the code and tools to build CEST saturation blocks with 
[pypulseq](https://github.com/imr-framework/pypulseq), which is a python adaption of the matlab-based 
[pulseq](https://github.com/pulseq/pulseq) project. 
Please visit [https://pulseq-cest.github.io/](https://pulseq-cest.github.io/) for more information on the pulseq-cest 
project. The documentation of the **pulseq** open file format for MR sequences can be found 
[here](https://pulseq.github.io/specification.pdf). Pulseq-cest specific seq file and parameter handling is done using the 
[bmctool](https://github.com/schuenke/BMCTool)  python package.

## Installation
For this installation, you need [Git](https://git-scm.com/), you just need to run the [install.py](install.py) file.
You can do this from the terminal (from this [pypulseq-cest folder](.)):
```
python install.py
```
If you run into any troubles, please refer to the **Troubleshooting** section below.

## Quick Start
You can run the [simulate.py](simulate.py) file for an example simulation. The steps are explained below.

1. You need a simulation configuration file in the YAML format and a sequence file in the seq format (see **Configuration and sequence file library** below). For example:
````python
sim_config = 'library/config_example.yaml'
seq_file = 'library/seq_example.seq'
````
2. You load and parse the parameters defined in the .yaml and .seq file with the following functions:
````python
sp = load_params(sim_config)
sim_params = parse_params(sp=sp, seq_file=seq_file)
````
3. You run the simulation using the SimPulseqSBB function. Note: Due to C++ handling, some functionalities are named in CamelCase.
````python
SimPulseqSBB(sim_params, seq_file)
````
4. You can retrieve the magnetization vector with the following function:
````python
m_out = sim_params.GetFinalMagnetizationVectors()
````
5. To get the correct magnetization in z-direction, you can use the following function.
````python
offsets, mz = get_zspec(m_out=m_out, sp=sp, seq_file=seq_file)
````
6. You can plot the magnetization with the following function:
````python
plot_z(mz=mz, offsets=offsets)
````

### Configuration and sequence file library
All simulations in [pypulseq-cest]() require a *yaml file* that includes all simulation settings and a *seq file*, which
defines the pre-saturation block. An [example seq-file](library/seq_example.seq), an [example yaml file]() as well as an 
[example script](library/write_seq_example.py) to create the [seq_example.seq](library/seq_example.seq) file can be 
found in the [library](library) subfolder. 

You will find further pre-defined and approved pre-saturation schemes and simulation configs in the [pulseq-cest-library](library/pulseq-cest-library)
If you have not successfully used the above installation, please read the subfolders [readme file](library/readme.md) to learn how to
download from the [pulseq-cest-library repository](https://github.com/kherz/pulseq-cest-library).




## Installation Troubleshooting
To avoid permission problems, you can run it with administrative rights:

**Windows**: start the terminal with administrative rights

**Linux**: Depending on the environment you want to install into, use ```sudo``` or the hand the ```--user``` flag like 
you would use for pip installations : 
```
sudo python install.py
```
or
```
python install.py --user
```
You might need to adapt your python executable, e.g. ```python3```

### Manual installation
#### Prerequisites 
To be able to create and simulate your own CEST saturation blocks using [pypulseq-cest](.), you need to install the
[BMCTool package](https://pypi.org/project/BMCTool/). You can install it with your favoured workflow or by running
```
    pip install bmctool
```
The installation using pip ensures that the required [pypulseq package](https://pypi.org/project/pypulseq/)
and [pyYaml package](https://pypi.org/project/PyYAML/) are installed automatically.
##### Alternative: System Independent Compilation Guide
Please refer to the system independent installation guide below
#### System independent Compilation Guide
If you can't find any matching distribution for your operating system, this compilation guide compiles and installs the tool directy with SWIG.
Please follow both instructions in the [sim/src/readme](sim/src/readme.md) and [library/readme](library/readme.md) individually.
##### Additional Prerequisites
You now need to have the following installed on your machine:
- [Git](https://git-scm.com/)
- [SWIG](http://www.swig.org/exec.html) (Installation for [Windows link](http://www.swig.org/Doc1.3/Windows.html))
- a working C++ compiler
    - for **Linux**, this comes with your operating system
    - for **Windows**, you need Visual C++ v.12.0 or higher, e.g. [Microsoft Visual C++ Redistributable](https://visualstudio.microsoft.com/downloads/)

### FAQ: I can't get any of this to work, what shall I do?
An alternative, pure python based tool that can handle the same input is the [bmctool](https://github.com/schuenke/BMCTool).
You will find the same functionalities, but with lower performance (simulation speed).