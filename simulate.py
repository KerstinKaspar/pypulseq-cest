"""
simulate.py
    Script to run the C++ SimPulseqSBB simulation based on the defined parameters.
    You need to define the path to a config file ('sim_config') and to a seq file ('seq_file').
"""
from pypulseq_cest.simulate import simulate

sim_config = 'library/config_example.yaml'
seq_file = 'library/seq_example.seq'

sim = simulate(sim_config=sim_config, seq_file=seq_file)
