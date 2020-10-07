"""
simulate_sbb.py
    Script to run the C++ SimPulseqSBB simulation based on the parameters defined in set_params.py
"""

from SimPulseqSBB import SimPulseqSBB
from sim_pulseq_sbb.parse_params import parse_sp, get_offsets
from sim_pulseq_sbb.plot import plot_z
from set_params import sp, seq_file

# parse the parameters for C++ code handling
sp_sim = parse_sp(sp, seq_file)

# run the simulation
SimPulseqSBB(sp_sim, seq_file)

# retrieve the calculated magnetization
m_out = sp_sim.GetFinalMagnetizationVectors()
mz = m_out[sp.mz_loc, :]

offsets = get_offsets(seq_file)
plot_z(mz, seq_file=seq_file, plot_mtr_asym=True)










