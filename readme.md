# PyPulseq-CEST: Simulation tool and seq-file preparation for CEST saturation blocks

This repository contains the code and tools to build CEST saturation blocks with 
[pypulseq](https://github.com/imr-framework/pypulseq), which is a python adaption of the matlab-based 
[pulseq](https://github.com/pulseq/pulseq) project. 
Please visit [https://pulseq-cest.github.io/](https://pulseq-cest.github.io/) for more information on the pulseq-cest 
project. The documentation of the **pulseq** open file format for MR sequences can be found 
[here](https://pulseq.github.io/specification.pdf). Pulseq-cest specific seq file and parameter handling is done using the 
[BMCTool](https://github.com/schuenke/BMCTool)  python package.

## Installation
For the installation of pypulseq-CEST you need to have [Git](https://git-scm.com/) installed. If this is the case, just
perform the following steps:

### 1) Download the code:
Clone the GitHub repository **OR** download the latest version as a 
   [ZIP file](https://github.com/KerstinHut/pypulseq-cest/archive/refs/heads/master.zip) and unzip it into a folder.

### 2) Installation using *setup.py* file:
We provide several pre-compiled distributions of the C++ based simulation code for Linux and Windows and python 
versions between 3.6 and 3.9. Using these pre-compiled distributions is the recommended installation. We further 
recommend using a clean python/anaconda environment. Two convenient ways to start the automatic installation via 
*setup.py* file are:
   * Open a terminal in the _pypulseq-cest_ folder, activate your environment and execute `python setup.py`
   * Open the _pypulseq-cest_ folder in your favorite IDE (e.g. PyCharm) and run the [setup.py](setup.py) file.
     
The installation process should install the following packages into your local python environment:
   * **pySimPulseSBB**: package containing the C++ based simulation code
   * **pypulseq_cest**: package containing the python based parser functions
   * **BMCTool**: package for pulseq-cest specific seq file and config file handling
   * **pypulseq**: package for general seq file writing/reading
   * all other required packages like PyYAML, numpy, matplotlib, etc...  

### 3) Download the pulseq-cest-library:
During the installation, a folder named _**pulseq-cest-library**_ should have been created in the _**library**_ 
subfolder. If this is not the case, download the latest version as a 
[ZIP file](https://github.com/kherz/pulseq-cest-library/archive/refs/heads/master.zip) and add it to the _**library**_ 
folder manually.  
   
If you run into any troubles during installation, please refer to the **Troubleshooting** section below.

## Quick Start

To perform an example simulation, you can run the following code:
````python
from pypulseq_cest.simulate import sim_example
sim_example()
````

As an alternative, we provide a [quick_start.py](quick_start.py) script. The individual steps/lines are explained below.:

1. Import all required classes and functions
    ````python
    from pySimPulseqSBB import BMCSim
    from pypulseq_cest.parser import parse_params, get_zspec
    from bmctool.set_params import load_params
    from bmctool.utils.eval import plot_z
    ````

2.  Define a config and a sequence file
    ````python
    sim_config = 'pypulseq_cest/example_library/config_example.yaml'
    seq_file = 'pypulseq_cest/example_library/seq_example.seq'
    ````
    For more information about the config and sequence files, check the **Configuration and sequence file library** 
    section below or visit the [pulseq-cest-library](https://github.com/kherz/pulseq-cest-library) Github repository.
    

3. Prepare and start the simulation

    ````python
    # load the simulation parameters
    sp = load_params(config_file)
    
    # create SWIG object of type SimulationParameters (C++ class)
    sim_params = parse_params(sp=sp)
    
    # create SWIG object of type BMCSim (C++ class)
    sim = BMCSim(sim_params)
    
    # set external sequence (*.seq) file
    sim.LoadExternalSequence(str(seq_file))
    
    # run simulation
    sim.RunSimulation()
    ````

4. Data processing and plotting:
   ````python   
   # retrieve magnetization vectors (x, y and z component of all pools):
    m_out = sim.GetMagnetizationVectors()
    
    # get offset values and z-magnetization of the water pool
    offsets, mz = get_zspec(m_out=m_out, sp=sp, seq_file=seq_file)
   ````
   Afterwards a z-spectrum can be plotted using the provided *plot_z* function:
    ````python
    plot_z(mz=mz, offsets=offsets, normalize=True, plot_mtr_asym=True)
    ````

   The *plot_z* function accepts several additional keyword arguments that allow to adjust the generated plot. 
   These are for example *normalize* (bool: toggle normalization), 
   *norm_threshold* (value/list/array: threshold for normalization offsets), *offsets* (list/array: 
   manually defined x-values), *invert_ax* (bool: toggle invert ax), *plot_mtr_asym* (bool:toggle plot MTR_asym) and 
   *title*, *x_label*, *y_label* to control the lables.
    

## Configuration and sequence file library
All simulations in [pypulseq-cest](.) require a *yaml file* that includes all simulation settings and a *seq file*, which
defines the pre-saturation block. An [example seq-file](pypulseq_cest/example_library/seq_example.seq), and an [example yaml file](pypulseq_cest/example_library/config_example.seq) file can be 
found in the [library](pypulseq_cest/example_library) subfolder. 

You will find further pre-defined and approved pre-saturation schemes and simulation configs in the [pulseq-cest-library](pulseq-cest-library)
If you have not successfully used the above installation, please download it from the [pulseq-cest-library repository](https://github.com/kherz/pulseq-cest-library).


# Project structure
This project tree is supposed to clarify the project components, their functionality and the source.

````text
pypulseq-cest
|
| -- src: source code and code handling
|     |
|     | -- compile (C++, SWIG): C++ code for simulation handling (SimPulseqSBB), 
|     |     |                   SWIG for direct wrapping (pySimPulseqSBB)
|     |     |
|     |     | -- Eigen (C++): library for matrix handling in C++
|     |     | -- dist: built distributions of pySimPulseqSBB for different environments
|     |     |
|     |     - BlochMcConnellSolver.h, ExternalSequence.cpp, ExternalSequence.h, SimPulseqSBB.cpp, 
|     |       SimPulseqSBB.h, SimulationParameters.cpp, SimulationParameters.h, 
|     |       SimPulseqSBBTemplate.h (C++): simulation handling (SimPulseqSBB)
|     |     - pySimPulseqSBB.i, numpy.i, eigen.i (SWIG): SWIG wrapper handling
|     |     - setup.py: installation of pySimPulseqSBB, the direct wrapped C++ code
|     |  
|     - readme.md: manual installation guide
|     - setup_pypulseq_cest.py: installation of the pypulseq_cest parser package
|     - MANIFEST.in: defining the pypulseq_cest package for setup_pypulseq_cest
|
| -- pypulseq_cest (python): package with parser functions for use of pySimPulseqSBB in python
|     |  
|     | -- example_library (seq, yaml): input files for an exemplary simulation
|     |     |
|     |     - config_example.yaml: example file for simulation configurations
|     |     - seq_example.seq: example sequence in the Pulseq format
|     |  
|     - parser.py: functions to parse simulation parameters to pySimPulseqSBB (SWIGged C++)
|     - simulate.py: pythonic implementation of the simulation function to simplify parsing
|
| (--) after successful installation: pulseq-cest-library (python, matlab, seq, yaml): contains
|      additional config and sequence files --> visit https://pulseq-cest.github.io/ for more info
|
- readme.md, CONTRIBUTING.md, LICENSE.md: project information
- setup.py: complete installation (pypulseq_cest, pySimPulseqSBB, dependencies)
- simulate.py: exemplary simulation script
````


## Installation Troubleshooting
### Permission problems:
To avoid permission problems, you can run the setup with administrative rights:
+ **Windows**: start the terminal with administrative rights

+ **Linux**: depending on the environment you want to install into, use ```sudo``` or hand the ```--user``` flag:  
    ```
    sudo python setup.py
    ```
    or
    ```
    python setup.py --user
    ```
    You might need to adapt your python executable, e.g. ```python3```

### System independent installation using *setup.py* file: 
If your first try to install pypulseq-cest via *setup.py* file didn't work, your system configuration is probably 
not included in the pre-compiled distributions we provide. For this case we provide a system independent installation. To
run this, please ensure that the following prerequisites are fullfilled:
1. The [BMCTool package](https://pypi.org/project/BMCTool/) has to be installed. This can be done by running
`pip install bmctool`. Using pip ensures that the required [pypulseq package](https://pypi.org/project/pypulseq/)
and [pyYaml package](https://pypi.org/project/PyYAML/) are installed as well.
2. The following programs have to be installed on your computer:
   - [Git](https://git-scm.com/)
   - [SWIG](http://www.swig.org/exec.html) (Installation for [Windows](http://www.swig.org/Doc1.3/Windows.html))
   - a working C++ compiler
     - for **Linux**, this comes with your operating system
     - for **Windows**, you need Visual C++ v.12.0 or higher, e.g. [Microsoft Visual C++ Redistributable](https://visualstudio.microsoft.com/downloads/)

If this is the case, simply re-run the *setup.py* file. This should execute all required steps including the compilation
and installation of the C++ based code. 

In the installation still didn't work, please try this [Manual Installation Guide](src/readme.md).

## FAQ: I can't get any of this to work, what shall I do?
An alternative, pure python based tool that can handle the same input is the [bmctool](https://github.com/schuenke/BMCTool).
You will find the same functionalities, but with lower performance (simulation speed).