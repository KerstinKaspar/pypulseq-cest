"""
simulate.py
    Script to run the C++ SimPulseqSBB simulation based on the defined parameters.
    You need to define the files containing sample and experimental parameters, as well as the sequence file.
"""
from SimPulseqSBB import SimPulseqSBB
from sim_pulseq_sbb.parse_params import parse_params
from sim_pulseq_sbb.eval import plot_z
from sim_pulseq_sbb.set_params import load_params
from sim_pulseq_sbb.util import get_offsets

# set the necessary filepaths:
sample_file = 'param_configs/sample_params.yaml'
experimental_file = 'param_configs/experimental_params.yaml'
seq_file = 'example/example_APTw_test.seq'

# load the parameters
sp = load_params(sample_file, experimental_file)
# parse for C++ handling
sim_params = parse_params(sp=sp, seq_file=seq_file)
# run the simulation
SimPulseqSBB(sim_params, seq_file)

# retrieve the calculated magnetization
# TODO get_z_specs
m_out = sim_params.GetFinalMagnetizationVectors()
mz = m_out[sp.mz_loc, 1:]

fig = plot_z(mz, seq_file=seq_file, plot_mtr_asym=True)