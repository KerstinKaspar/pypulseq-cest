from sim_bmc.bmc_tool_v2 import BMCTool
from sim.params import Params
from phantom.phantom import build_default_phantom
from phantom.plot_phantom import plot_phantom
import numpy as np
from sim.eval import get_offsets
from time import time

phantom = build_default_phantom()
# phantom_fig = plot_phantom(phantom)


seq_file = 'example/example_APTw_test.seq'

b0 = 3  # T
gamma = 267.5153  # rad/uT
scale = 0.5

p_t1, p_t2, p_b0, p_b1, p_f = [phantom[i] for i in range(5)]
n_vars, n_rows, n_cols = phantom.shape
simulations = {}

time0 = time()
for loc in np.ndindex(n_rows, n_cols):
        if p_t1[loc] == 0:
            pass
        else:
            print(loc, 'from <', n_rows, 'x', n_cols)
            sp = Params()
            b0_inhom = p_b0[loc]
            rel_b1 = 1 + p_b1[loc]
            sp.set_scanner(b0=b0, gamma=gamma, b0_inhomogeneity=b0_inhom, rel_b1=rel_b1)
            f_w = 1
            r1_w = 1 / p_t1[loc]
            r2_w = 1 / p_t2[loc]
            sp.set_water_pool(r1=r1_w, r2=r2_w, f=f_w)
            # define CEST pool parameters
            # strong pool
            r1 = r1_w  # [Hz]
            r2 = 1 / 100e-3  # [Hz]
            k = 40  # exchange rate[Hz]
            f = p_f[loc]  # rel
            dw = 5  # [ppm]
            # set CEST pool parameters
            sp.set_cest_pool(r1=r1, r2=r2, k=k, f=f, dw=dw)
            sp.set_m_vec(scale)
            Sim = BMCTool(sp, seq_file)
            Sim.run()
            m_out = Sim.Mout
            mz = sp.get_mz(m_out)
            simulations.update({loc: sp})
            print('Mz: \n', mz)

time1 = time()
secs = time1 - time0
print("Simulations took", secs, "s.")

offsets = get_offsets(seq_file)
dw = 0.7
offsets = np.array(offsets)
idx = int(np.where(offsets == offsets[np.abs(offsets - dw).argmin()])[0])
import matplotlib.pyplot as plt
phantom_sim = np.zeros([len(offsets), n_rows, n_cols])
# len_mz = len(simulations[simulations.keys()[0]].mz)
for o in range(len(offsets)):
    for loc in list(simulations.keys()):
        phantom_sim[o, loc[0], loc[1]] = simulations[loc].mz[o]
for i in [5, 20, 27]:
     fig, ax = plt.subplots(figsize=(12, 9))
     tmp = ax.imshow(phantom_sim[i])
     plt.title(str(offsets[i]))
     plt.colorbar(tmp)
     plt.show()
from sim.eval import plot_z
mz_test = simulations[list(simulations.keys())[0]].mz
fig = plot_z(mz_test, seq_file=seq_file, plot_mtr_asym=False)

fig, ax1 = plt.subplots()
ax1.set_ylim([0, 1])
ax1.set_ylabel('Z', color='b')
ax1.set_xlabel('Offsets')
labels = ["gm top", "gm mid", "gm bottom", "wm bottom left", "wm top right ", "csf"]
locs = [(38, 128), (115, 128), (224, 128), (153, 82), (50, 155), (124, 144)]
for i in range(len(locs)):
    mz = simulations[locs[i]].mz[1:]
    plt.plot(offsets, mz, '.--', label=labels[i])
plt.gca().invert_xaxis()
plt.legend()
plt.show()
ax1.tick_params(axis='y', labelcolor='b')
# from sim_bmc.bmc_tool_v2 import BMCTool
# from sim.eval import get_offsets
# # choose a params file to import for the simulation
# from set_params import sp, seq_file
# # from standard_cest_params import sp, seq_file
# from phantom_examples.phantom_examples import create_phantom, plot_phantom, phantom_compartments
# from phantom_examples.phantom_examples import phantom_tissues_cest
# Sim = BMCTool(sp, seq_file)
# Sim.run()
# m_out = Sim.Mout
#
# mz = m_out[sp.mz_loc, :]
# mz1 = mz.copy()
# mz2 = mz.copy()
# sp1 = sp
# sp2 = sp
#
#
# offsets = get_offsets(seq_file)
#
# # phantom_examples = create_phantom(len(offsets), mvec=mz)
#
# phantom_examples = phantom_compartments(mz=mz, sp=sp, offsets=offsets, seq_file=seq_file, mtr_asym=True)
# phantom_examples = phantom_tissues_cest(mz, sp, mz1, sp1, mz2, sp2, offsets, 256, seq_file, False)
# fig = plot_phantom(phantom_examples=phantom_examples[0], sp=sp) #, offsets=offsets, pool=0)
