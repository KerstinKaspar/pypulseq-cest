# issues
## differences pypulseq <> matlab
VERSION differences
changed in this pypulseq: make_gauss_pulse(time_bw_product: float = 4) <> m = 3
changed in this pypulseq (larger float): compression of shapes beim Schreiben von gauss_pulse.signal in seq.shape_library falsch (erhöht Anzahl Einträge)
## tools
fail to simulate SimPulseqSbb when no CEST pool is defined

## SWIG
[Beispiel Recon](https://github.com/ckolbPTB/PtbPyRecon/tree/27d956a8b4d5589603dbe3b990ea0910186f4fd2/PTBRecon/Extensions/source/rg)

[SWIG Python help](http://www.swig.org/Doc1.3/Python.html#Python_nn3)

# README notes from combined repo
We also provide the BMCSim Tool, which was originally implemented as a standalone simulation tool by Patrick Schuenke.
To enable simulation using both tools, the parameters and seq_file defined in the [set_params](sim/set_params.py) file can 
be used for both tools and the simulation run with the [simulate_bmc](simulate_bmc.py) script.

