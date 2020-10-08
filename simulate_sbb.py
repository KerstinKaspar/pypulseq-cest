"""
simulate_sbb.py
    Script to run the C++ SimPulseqSBB simulation based on the defined parameters.
    You can adapt parameters in set_params.py or use a standard CEST setting as defined in standard_cest_params.py.
"""
from SimPulseqSBB import SimPulseqSBB
from sim_pulseq_sbb.parse_params import parse_sp
from sim.eval import plot_z
# choose a params file to import for the simulation
from set_params import sp, seq_file
# from standard_cest_params import sp, seq_file


# parse the parameters for C++ code handling
sp_sim = parse_sp(sp, seq_file)

# run the simulation
SimPulseqSBB(sp_sim, seq_file)

# retrieve the calculated magnetization
m_out = sp_sim.GetFinalMagnetizationVectors()
mz = m_out[sp.mz_loc, :]

fig = plot_z(mz, seq_file=seq_file, plot_mtr_asym=True)










