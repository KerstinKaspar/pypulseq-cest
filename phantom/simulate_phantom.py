from sim_bmc.bmc_tool_v2 import BMCTool
from sim.eval import plot_z, get_offsets
# choose a params file to import for the simulation
from set_params import sp, seq_file
# from standard_cest_params import sp, seq_file
from phantom.phantom import create_phantom
import numpy as np
import matplotlib.pyplot as plt

Sim = BMCTool(sp, seq_file)
Sim.run()
m_out = Sim.Mout

mz = m_out[sp.mz_loc, :]

offsets = get_offsets(seq_file)

phantom = create_phantom(len(offsets), mvec=mz)

# find index closest to CEST resonance
idx = offsets.index(min(offsets))

fig, ax = plt.subplots(figsize=(12,9))
tmp = ax.imshow(phantom[idx, ])
plt.show()