# Simulation tool and seq-file preparation for CEST saturation blocks

## Sequence design in open file format for MR sequences
This repository contains the necessary code and tools to build CEST saturation blocks with a variation of [pypulseq](https://github.com/imr-framework/pypulseq)
which in itself is a python adaption of the matlab-based [pulseq](https://github.com/pulseq/pulseq). The documentation
of the open file format for MR sequences can be found [here](https://pulseq.github.io/specification.pdf). Pypulseq need
not be installed, as the version for CEST usage can be found in the [pypulseq](pypulseq) subfolder.

Example scripts and sequences can be found in the [example](./example) subfolder. Please find further remarks in that subfolders [readme](./example/readme.md)

## Simulation of CEST sequences
Furthermore, this repository provides a python implementation of the C++ based simulation tool [pulseq-cest-sim](https://github.com/kherz/pulseq-cest/tree/master/pulseq-cest-sim)
by Kai Herz, which was originally made available for use in MATLAB. The installation of the python package is necessary 
(see section *Installation* below). Here, you'll find a script to set parameters for a [standard simulation](standard_cest_params.py) as proposed by Moritz Zaiss or simulate your own Z-Spectra by defining your
parameters and the according seq-file in [set_params](set_params.py) and run the [simulation](simulate_sbb.py) script. The
package code and C++ source code can be found in the [sim_pulseq_sbb](sim_pulseq_sbb) module.

## Installation
Please refer to the [readme](./sim_pulseq_sbb/src/readme.md) in [sim_pulseq_sbb/src](./sim_pulseq_sbb/src) for 
installation of the necessary python module.
