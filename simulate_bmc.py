"""
simulate_bmc.py
    Script to run the BMCTool simulation based on the parameters defined in set_params.py
"""
from sim_bmc.bmc_tool_v2 import BMCTool
import matplotlib.pyplot as plt
# from set_params import *
from standard_cest_params import *

Sim = BMCTool(sp, seq_file)
Sim.run()
Mout = Sim.Mout

fig, ax = plt.subplots(figsize=(12,9))
ax.plot(Sim.seq.definitions['offsets_ppm'], Mout[6, 1:], marker='o', linestyle='--', linewidth=2, color='black')
ax.set_xlabel('frequency offset [ppm]', fontsize=20)
ax.set_ylabel('normalized signal', fontsize=20)
ax.set_ylim([-0.1,1])
ax.invert_xaxis()
ax.grid()
plt.show()
