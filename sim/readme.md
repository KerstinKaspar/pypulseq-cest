# SimPulseqSBB 
## Simulation tool for CEST sequences (python and C++)
This tool contains the C++ code to approximate the Bloch-McConnel-Equations with the Pade approximation.
The simulation code was originally implemented by Kai Herz and implemented in Matlab as [pulseq-cest](https://github.com/kherz/pulseq-cest).
To use this simulation, the module hast do be installed according to the [readme](src/readme.md) in the [src](src) subfolder.
The [parse_params](parse_params.py) script will be called during simulation for C++ code handling. 