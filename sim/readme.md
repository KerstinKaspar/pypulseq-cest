# SimPulseqSBB 
## Simulation tool for CEST sequences (python and C++)
This tool contains the C++ code to approximate the Bloch-McConnel-Equations with the Pade approximation.
The simulation code was originally written by Kai Herz and implemented in Matlab as [pulseq-cest](https://github.com/kherz/pulseq-cest).
To use this simulation, the module hast do be installed according to the [readme](../readme.md) in the [pypulseq-cest root folder](..).

## Content
This [sim folder](.) contains the python code necessary to parse the BMCTool parameters to the C++ simulation. 

- [sim.parser](parse_params.py): contains functions for C++ code handling.

Simulation settings are handled with the [BMCTool](https://pypi.org/project/BMCTool/)

### Source code (C++)
The [src folder](src) contains C++ code for simulations and SWIG code for installation. Please refer to that folders [readme](src/readme.md)
for further information.