from sim_bmc.bmc_tool_v2 import BMCTool
from sim.params import Params
from phantom.phantom import build_default_phantom
from phantom.plot_phantom import plot_phantom
import numpy as np
from sim.eval import get_offsets
from time import time
import matplotlib.pyplot as plt
import json
from datetime import date

# open json data
# with open('example/data/phantom_data_1pools_2020-10-16.txt'.format(n=data['n_cest_pools'], date=today)) as json_file:
#     dataload = json.load(json_file)

# generate and plot phantom
phantom = build_default_phantom()
phantom_fig = plot_phantom(phantom)

# set general simulation parameters
seq_file = 'example/example_CW.seq'
b0 = 3  # T
gamma = 267.5153  # rad/uT
scale = 0.5

# unpack simulation parameters from phantom
p_t1, p_t2, p_b0, p_b1, p_f = [phantom[i] for i in range(5)]
n_vars, n_rows, n_cols = phantom.shape

# find all relevant locations for simulation
# to simulate part of the phantom (min_row to max_row), define something like idces[128*min_row, 128*max_row]
locs = []
idces = list(np.ndindex(n_rows, n_cols))[128*87:128*93]
for loc in idces:
    if p_t1[loc] != 0:
        locs.append(loc)
n_locs = len(locs)

# simulation for each phantom pixel in locs
time0 = time()
simulations = {}
for loc in locs:
        print('Simulation', locs.index(loc), 'of', n_locs)
        # define simulation parameters
        sp = Params()
        # define inhomogeneities from inhomogeneity maps
        b0_inhom = p_b0[loc]
        rel_b1 = p_b1[loc]
        sp.set_scanner(b0=b0, gamma=gamma, b0_inhomogeneity=b0_inhom, rel_b1=rel_b1)
        # define water pool from T1 and T2 maps
        r1_w = 1 / p_t1[loc]
        r2_w = 1 / p_t2[loc]
        sp.set_water_pool(r1=r1_w, r2=r2_w)
        # define CEST pool parameters
        r1 = r1_w  # [Hz]
        r2 = 1 / 100e-3  # [Hz]
        k = 40  # exchange rate[Hz]
        # define fractions from fraction map
        f = p_f[loc]  # rel
        dw = 5  # [ppm]
        sp.set_cest_pool(r1=r1, r2=r2, k=k, f=f, dw=dw)
        sp.set_m_vec(scale)
        # start the simulation for this pixel
        Sim = BMCTool(sp, seq_file)
        Sim.run()
        # retrieve simulated spectrum
        m_out = Sim.Mout
        mz = sp.get_zspec(m_out, m0=Sim.seq.definitions['run_m0_scan'][0])
        simulations.update({loc: sp})
time1 = time()
secs = time1 - time0
print("Simulations took", secs, "s.")

# create phantom images of all magnetizations at each offsets
offsets = np.array(get_offsets(seq_file))
phantom_sim = np.zeros([len(offsets), 128, 128])
for o in range(len(offsets)):
    for k in list(simulations.keys()):
        phantom_sim[o, k[0], k[1]] = simulations[k].zspec[o]

# save data as json
today = date.today().strftime("%Y-%m-%d")
data = {}
data['B0'] = b0
data['gamma'] = gamma
data['scale'] = scale
data['phantom'] = phantom.tolist()
data['phantom_sim'] = phantom_sim.tolist()
data['offsets'] = offsets.tolist()
data['n_cest_pools'] = len(sp.cest_pools)
with open('example/data/phantom_data_{n}pools_{date}.txt'.format(n=data['n_cest_pools'], date=today), 'w') as outfile:
    json.dump(data, outfile)

# calculate MTRasym
mtr_asyms = np.zeros([len(offsets), 128, 128])
for o in range(len(offsets)):
    for l in list(simulations.keys()):
        mtr_asym = np.flip(simulations[l].zspec) - simulations[l].zspec
        mtr_asyms[o, l[0],l[1]] = mtr_asym[o]

# show CEST pool offset phantom image
dw_pool = 5
idx = int(np.where(offsets == offsets[np.abs(offsets - dw_pool).argmin()])[0])
fig1, ax = plt.subplots(figsize=(12, 9))
tmp = ax.imshow(phantom_sim[idx])
plt.title("Z" + str(offsets[idx]))
plt.colorbar(tmp)
plt.show()

# plot some tissue spectra
fig2, ax1 = plt.subplots()
ax1.set_ylim([0, 1])
ax1.set_ylabel('Z', color='b')
ax1.set_xlabel('Offsets')
labels = ["gm top", "gm mid", "gm bottom", "wm bottom left", "wm top right ", "csf"]
locs = [(14, 64), (57, 64), (112, 64), (126, 41), (25, 78), (62, 72)]
for i in range(len(locs)):
    mz = simulations[locs[i]].zspec[1:]
    plt.plot(offsets, mz, '.--', label=labels[i])
plt.gca().invert_xaxis()
plt.legend()
plt.show()
ax1.tick_params(axis='y', labelcolor='b')

# plot some fraction spectra
fig3, ax1 = plt.subplots()
ax1.set_ylim([0, 1])
ax1.set_ylabel('Z')
ax1.set_xlabel('Offsets')
labels = ["gm", "wm f=min", "wm f=max"]
locs = [(88, 40), (92, 40), (92, 85)]
for i in range(len(locs)):
    mz = simulations[locs[i]].zspec[1:] * simulations[locs[i]].zspec[0]
    plt.plot(offsets, mz, '.--', label=labels[i])
plt.gca().invert_xaxis()
plt.legend()
plt.show()
