"""
simulate_bmc.py
    Script to run the BMCTool simulation based on the defined parameters.
    You can adapt parameters in set_params.py or use a standard CEST setting as defined in standard_cest_params.py.
"""
from sim_bmc.bmc_tool_v2 import BMCTool
from sim.eval import plot_z
# choose a params file to import for the simulation
from set_params import sp, seq_file
# from standard_cest_params import sp, seq_file
import numpy as np

Sim = BMCTool(sp, seq_file)
Sim.run()
m_out = Sim.Mout

mz = m_out[sp.mz_loc, :]

fig = plot_z(mz, seq_file=seq_file, plot_mtr_asym=True)

from set_params_2 import sp2

Sim2 = BMCTool(sp2, seq_file)
Sim2.run()
m_out2 = Sim2.Mout

mz2 = m_out2[2, :]

fig2 = plot_z(mz, seq_file=seq_file, plot_mtr_asym=True)
np.allclose(mz, mz2)