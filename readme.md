# Simulation tool and seq-file preparation for CEST saturation blocks

## Sequence design in open file format for MR sequences
This repository contains the necessary code and tools to build CEST saturation blocks with [pypulseq](https://github.com/imr-framework/pypulseq)
which in itself is a python adaption of the matlab-based [pulseq](https://github.com/pulseq/pulseq). The documentation
of the open file format for MR sequences can be found [here](https://pulseq.github.io/specification.pdf).

An example script and sequences can be found in the [example](./example) subfolder. Please find further remarks in that subfolders [readme](./example/readme.md)
Since pypulseq is producing files of the version 1.2, we provide a function to create 

## Simulation of CEST sequences
The goal of this repository is to enable the simulation for CEST spectra in python. Therefore, we provide a python implementation of the C++ based simulation tool [pulseq-cest-sim](https://github.com/kherz/pulseq-cest/tree/master/pulseq-cest-sim)
by Kai Herz, which was originally made available for use in MATLAB. The installation of the python package is necessary 
(see section *Installation* below). You can simulate your own Z-Spectra by defining your parameters similar to the template files for [experimental (scanner etc.) parameters](param_configs/experimental_params.yaml) and [parameters regarding the sample](param_configs/sample_params.yaml).
We also provide config files to set parameters for an exemplary standard simulation and to simulate the WASABI approach. 
You can then run the simulation with the [simulate](simulate.py) script.
 
Parameter handling and evaluation tools are defined in the [sim_pulseq_sbb](sim_pulseq_sbb) folder. The package code and C++ source code can be found in the [src](sim_pulseq_sbb/src) subfolder.

## Installation
Please refer to the [readme](./sim_pulseq_sbb/src/readme.md) in [sim_pulseq_sbb/src](./sim_pulseq_sbb/src) for 
installation of the necessary python module.
