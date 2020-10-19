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


def load_data(filename):
    # open json data
    with open(filename) as json_file:
        dataload = json.load(json_file)

    return dataload


def simulate_data():
    # generate and plot phantom
    phantom = build_default_phantom()
    # phantom_fig = plot_phantom(phantom)

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
    idces = list(np.ndindex(n_rows, n_cols)) # [128*87:128*93]
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
        Sim.run(par_calc=True)
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

    # z_specs = {k : simulations[k].zspec.tolist() for k in simulations.keys()}

    # save data as json
    today = date.today().strftime("%Y-%m-%d")
    data = {}
    data['B0'] = b0
    data['gamma'] = gamma
    data['scale'] = scale
    data['phantom'] = phantom.tolist()
    data['sim_locs'] = list(locs)
    # data['z_specs_k'] = list(z_specs.keys())
    # data['z_specs_v'] = [v.tolist() for v in z_specs.values()]
    data['phantom_sim'] = phantom_sim.tolist()
    data['offsets'] = offsets.tolist()
    data['n_cest_pools'] = len(sp.cest_pools)
    seq_name = seq_file.split('/')[-1].replace('.seq', '')
    with open('example/data/phantom_data_{seq_name}_{n}pools_{date}.txt'.format(n=data['n_cest_pools'], date=today,
                                                                                seq_name=seq_name), 'w') as outfile:
        json.dump(data, outfile)
    return data


# simulate
data = simulate_data()
# load data
# data = load_data('example/data/phantom_data_1pools2_2020-10-16.txt')

offsets = np.array(data['offsets'])
locs = data['sim_locs'] # if undefined use code from function simulate_data
phantom = np.array(data['phantom'])
phantom_sim = np.array(data['phantom_sim'])
z_specs = {data['z_specs_k'][i]: data['z_specs_v'][i] for i in range(len(data['z_specs_k']))} # if undefined use:
# z_specs = {}
# for loc in locs:
#     z = [phantom_sim[o][loc] for o in range(len(offsets))]
#     z_specs.update({loc: z})

# calculate MTRasym
mtr_asyms = {}
for loc in locs:
    mtr_asym = np.flip(z_specs[loc]) - z_specs[loc]
    mtr_asyms[loc] = mtr_asym

# show CEST pool offset phantom image
dw_pool = 5
idx = int(np.where(offsets == offsets[np.abs(offsets - dw_pool).argmin()])[0])
fig = plt.figure()
ax_im = plt.subplot(121)
tmp = ax_im.imshow(phantom_sim[idx])
plt.title("$Z({\Delta}{\omega})$ at offset " + str(offsets[idx]))
plt.colorbar(tmp)
#plt.show()

# plot some tissue spectra
# fig2 = figure()
ax_t = plt.subplot(122)
ax_t.set_ylim([0, 1])
ax_t.set_ylabel('$Z({\Delta}{\omega})$')
ax_t.set_xlabel('Offsets')
labels = ["gm top", "gm mid", "gm bottom", "wm bottom left", "wm top right ", "csf"]
locs = [(20, 64), (57, 64), (85, 56), (65, 41), (25, 80), (72, 62)]
for i in range(len(locs)):
    # TODO something is wrong with the indexing - matplotlib != numpy? imshow != annotate?
    mz = z_specs[locs[i]]
    plt.plot(offsets, mz, '.--', label=labels[i])
plt.gca().invert_xaxis()
plt.legend()
plt.title('Z-Spectra for tifferent tissue types and phantom locations.')
for i in range(len(locs)):
    ax_im.annotate(s=labels[i], xy=locs[i], arrowprops={'arrowstyle': 'simple'}, xytext=(locs[i][0]+2, locs[i][1]-4))
fig.show()

# plot some fraction spectra
fig3, ax1 = plt.subplots()
ax1.set_ylim([0, 1])
ax1.set_ylabel('Z')
ax1.set_xlabel('Offsets')
labels = ["gm", "wm f=min", "wm f=max"]
locs = [(88, 40), (92, 40), (92, 85)]
for i in range(len(locs)):
    mz = simulations[locs[i]].zspec
    plt.plot(offsets, mz, '.--', label=labels[i])
plt.gca().invert_xaxis()
plt.legend()
plt.show()
