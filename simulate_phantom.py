from sim_bmc.bmc_tool_v2 import BMCTool
from sim.eval import get_offsets
# choose a params file to import for the simulation
from set_params import sp, seq_file
# from standard_cest_params import sp, seq_file
from phantom.phantom import create_phantom, plot_phantom


Sim = BMCTool(sp, seq_file)
Sim.run()
m_out = Sim.Mout

mz = m_out[sp.mz_loc, :]

offsets = get_offsets(seq_file)

phantom = create_phantom(len(offsets), mvec=mz)

fig = plot_phantom(phantom=phantom, sp=sp, offsets=offsets, pool=0)
