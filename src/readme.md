## Installation guide:
1. Prerequisites: Swig, C++ and for windows VisualC++
2. navigate to this folder, then use the following commands:

```
swig -c++ -python SimPulseqSBB.i ExternalSequence.i
python setup.py install
```

To install a single module ust the setup_sim.py or setup_ext.py installation files respectively.