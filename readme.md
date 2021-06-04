# PyPulseq-CEST: Simulation tool and seq-file preparation for CEST saturation blocks

This repository contains the code and tools to build CEST saturation blocks with 
[pypulseq](https://github.com/imr-framework/pypulseq), which is a python adaption of the matlab-based 
[pulseq](https://github.com/pulseq/pulseq) project. 
Please visit [https://pulseq-cest.github.io/](https://pulseq-cest.github.io/) for more information on the pulseq-cest 
project. The documentation of the **pulseq** open file format for MR sequences can be found 
[here](https://pulseq.github.io/specification.pdf). Pulseq-cest specific seq file and parameter handling is done using the 
[BMCTool](https://github.com/schuenke/BMCTool)  python package.

## Installation
For the installation of pulseq-CEST you need to have [Git](https://git-scm.com/) installed. If this is the case, just
perform the following steps:

#### 1) Download the code:
Simply clone the GitHub repository **OR** download the latest version as a 
   [ZIP file](https://github.com/KerstinHut/pypulseq-cest/archive/refs/heads/master.zip) and extract it into a folder on
   you computer.

#### 2) Install the code:
We recommend using a clean python/anaconda environment with python version >= 3.7. Two convenient ways to start the 
installation are:
   * Open a terminal in the _pypulseq-cest_ folder, activate your environment and excute ``python setup.py``
   * Open the _pypulseq-cest_ folder as a project in your favorite IDE (e.g. PyCharm), select your environment and
   execute the [setup.py](setup.py) file in your IDE.
     
The installation installs the following packages into your local python environment:
   * **pySimPulseSBB**: package containing the C++ based simulation code
   * **pypulseq_cest**: package containing the python based parser functions
   * **BMCTool**: package for pulseq-cest specific seq file and config file handling
   * **pypulseq**: package for general seq file writing/reading
   * all other required packages like PyYAML, numpy, matplotlib, etc...  

#### 3 Download the pulseq-cest-library:
During the installation, a folder named _**pulseq-cest-library**_ should have been created in the _**library**_ 
subfolder. If this is not the case, download the latest version as a 
[ZIP file](https://github.com/kherz/pulseq-cest-library/archive/refs/heads/master.zip) and add it to the _**library**_ 
folder manually.  
   
If you run into any troubles during installation, please refer to the **Troubleshooting** section below.

## Quick Start
For an example, you can run the following from any script at any location with pypulseq_cest installed:
````python
from pypulseq_cest.simulate import sim_example

sim_example()
````

You can run the [simulate.py](simulate.py) file for an example simulation. The individual steps/lines are explained below.

1. Import the simulate function
````python
from pypulseq_cest.simulate import simulate
````

2.  You need a simulation configuration file in the YAML format and a sequence file in the seq format (see **Configuration and sequence file library** below). For example:
````python
sim_config = 'pypulseq_cest/example_library/config_example.yaml'
seq_file = 'pypulseq_cest/example_library/seq_example.seq'
````

2. Run the simulations with
````python
sim = simulate(config_file=sim_config, seq_file=seq_file)
````


### Configuration and sequence file library
All simulations in [pypulseq-cest](.) require a *yaml file* that includes all simulation settings and a *seq file*, which
defines the pre-saturation block. An [example seq-file](pypulseq_cest/example_library/seq_example.seq), and an [example yaml file](pypulseq_cest/example_library/config_example.seq) file can be 
found in the [library](pypulseq_cest/example_library) subfolder. 

You will find further pre-defined and approved pre-saturation schemes and simulation configs in the [pulseq-cest-library](pulseq-cest-library)
If you have not successfully used the above installation, please download it from the [pulseq-cest-library repository](https://github.com/kherz/pulseq-cest-library).


## Installation Troubleshooting
To avoid permission problems, you can run the setup with administrative rights:

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
If you can't install pypulseq-cest with the installation guide above, you can manually install the pySimPulseqSBB C++ code with the following instructions.
It is then possible, to use all functionalities from this working directory.
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
Please follow both instructions in the [sim/src/readme](sim/src/readme.md) and [library/readme](pypulseq_cest/library/readme.md) individually.
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