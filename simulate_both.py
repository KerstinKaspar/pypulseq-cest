"""
simulate_sbb.py
    Script to run the C++ SimPulseqSBB simulation based on the defined parameters.
    You can adapt parameters in set_params.py or use a standard CEST setting as defined in standard_cest_params.py.
"""
from sim_bmc.bmc_tool_v2 import BMCTool
from SimPulseqSBB import SimPulseqSBB
from sim_pulseq_sbb.parse_params import parse_sp
from sim.eval import plot_z
# choose a params file to import for the simulation
# from set_params import sp, seq_file
from standard_cest_params import sp, seq_file


# BMCTool simulation
Sim = BMCTool(sp, seq_file)
Sim.run()
m_out_bmc = Sim.Mout
mz_bmc = m_out_bmc[sp.mz_loc, :]

# SBB simulation
# parse the parameters for C++ code handling
sp_sim = parse_sp(sp, seq_file)
# run the simulation
SimPulseqSBB(sp_sim, seq_file)

# retrieve the calculated magnetization
m_out_sbb = sp_sim.GetFinalMagnetizationVectors()
mz_sbb = m_out_sbb[sp.mz_loc, :]

fig_sbb, ax_sbb = plot_z(mz_sbb, seq_file=seq_file, plot_mtr_asym=True, title='Z spectrum SBB simulation')
fig_bmc, ax_bmc = plot_z(mz_bmc, seq_file=seq_file, plot_mtr_asym=True, title='Z spectrum BMCTool simulation')











