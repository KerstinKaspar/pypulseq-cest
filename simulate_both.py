"""
simulate_sbb.py
    Script to run the C++ SimPulseqSBB simulation based on the defined parameters.
    You can adapt parameters in param_configs.py or use a standard CEST setting as defined in standard_cest_params.py.
"""
from sim_bmc.bmc_tool_v2 import BMCTool
from SimPulseqSBB import SimPulseqSBB
from sim_pulseq_sbb.parse_params import parse_sp
from sim.eval import get_offsets, calc_mtr_asym
import numpy as np
import matplotlib.pyplot as plt
from sim.set_params import load_params


# set the necessary filepaths:
sample_file = 'param_configs/sample_params.yaml'
experimental_file = 'param_configs/experimental_params.yaml'
seq_file = 'example/example_APTw_test.seq'


sp = load_params(sample_file, experimental_file)


# BMCTool simulation
Sim = BMCTool(sp, seq_file)
Sim.run()
m_out_bmc = Sim.Mout
mz_bmc = m_out_bmc[sp.mz_loc, :-1]

# SBB simulation
# parse the parameters for C++ code handling
sp_sim = parse_sp(sp, seq_file)
# run the simulation
SimPulseqSBB(sp_sim, seq_file)

# retrieve the calculated magnetization
m_out_sbb = sp_sim.GetFinalMagnetizationVectors()
mz_sbb = m_out_sbb[sp.mz_loc, :-1]

# fig_sbb = plot_z(mz_sbb, seq_file=seq_file, plot_mtr_asym=True, title='Z spectrum SBB simulation')
# fig_bmc = plot_z(mz_bmc, seq_file=seq_file, plot_mtr_asym=True, title='Z spectrum BMCTool simulation')

offsets = get_offsets(seq_file)

fig, ax1 = plt.subplots()
ax1.set_ylim([0, 1])
ax1.set_ylabel('Z', color='b')
ax1.set_xlabel('Offsets')
plt.plot(offsets, mz_bmc, '.--', label='$Z_{BMC}$', color='b')
plt.plot(offsets, mz_sbb, '.--', label='$Z_{SBB}$', color='g')
plt.gca().invert_xaxis()
plt.legend(loc=3)
ax1.tick_params(axis='y', labelcolor='b')

mtr_asym_bmc = calc_mtr_asym(mz_bmc)
mtr_asym_sbb = calc_mtr_asym(mz_sbb)
ax2 = ax1.twinx()
ax2.set_ylim([0, round(np.max(mtr_asym_bmc) + 0.01, 2)])
ax2.set_ylabel('$MTR_{asym}$', color='y')
ax2.plot(offsets, mtr_asym_bmc, label='$MTR_{asym, BMC}$', color='k')
ax2.plot(offsets, mtr_asym_sbb, label='$MTR_{asym, SBB}$', color='y')
ax2.tick_params(axis='y', labelcolor='y')
fig.tight_layout()
title = 'Z-spec'
plt.legend(loc=4)
plt.title(title)
plt.show()









