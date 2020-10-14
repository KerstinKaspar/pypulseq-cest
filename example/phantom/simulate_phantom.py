from sim_bmc.bmc_tool_v2 import BMCTool
from sim.eval import get_offsets
# choose a params file to import for the simulation
from set_params import sp, seq_file
# from standard_cest_params import sp, seq_file
from phantom.phantom import create_phantom, plot_phantom, phantom_compartments
from phantom.phantom import phantom_tissues_cest

Sim = BMCTool(sp, seq_file)
Sim.run()
m_out = Sim.Mout

mz = m_out[sp.mz_loc, :]
mz1 = mz.copy()
mz2 = mz.copy()
sp1 = sp
sp2 = sp


offsets = get_offsets(seq_file)

# phantom = create_phantom(len(offsets), mvec=mz)

phantom = phantom_compartments(mz=mz, sp=sp, offsets=offsets, seq_file=seq_file, mtr_asym=True)
phantom = phantom_tissues_cest(mz, sp, mz1, sp1, mz2, sp2, offsets, 256, seq_file, False)
fig = plot_phantom(phantom=phantom[0], sp=sp) #, offsets=offsets, pool=0)
