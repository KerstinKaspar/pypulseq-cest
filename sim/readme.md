# SimPulseqSBB 
## Simulation tool for CEST sequences (python and C++)
This tool contains the C++ code to approximate the Bloch-McConnel-Equations with the Pade approximation.
The simulation code was originally implemented by Kai Herz and implemented in Matlab as [pulseq-cest](https://github.com/kherz/pulseq-cest).
To use this simulation, the module hast do be installed according to the [readme](../readme.md) in the [pypulseq-cest root folder](..).

## Content
This [sim folder](.) contains the python code necessary for simulation. The C++-code can be found in the [src subfolder](src) (see below or [src/readme.md](src/readme.md))
- [sim.params](params.py): contains Params class to handle simulation parameters.
- [sim.set_params](set_params.py): contains functions to handle config files to set the parameters
- [sim.parse_params](parse_params.py): contains functions for C++ code handling.
 
- [sim.utils.eval](utils/eval.py): contains functions for plotting and evaluation of simulation output
- [sim.utils.utils](utils/utils.py): contains additional functions for simulation handling

- [sim.utils.seq.conversion](utils/seq/conversion.py): contains functions to (pseudo) convert sequences between versions
- [sim.utils.seq.read](utils/seq/read.py): contains functions to read different sequence file versions

### Source code (C++)
The [src folder](src) ontains C++ code for simulations and SWIG code for installation. Please refer to that folders [readme](src/readme.md)
for further information.