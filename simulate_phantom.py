from phantom.phantom import Phantom
import numpy as np
from sim.util import sim_noise
import matplotlib.pyplot as plt
import pickle

phantom = Phantom()
phantom.set_defaults(fractions=False)
data = phantom.simulate(seq_file='example/wasabi/example_wasabi.seq', noise=False)
filename = 'example/data/test_phantom_wasabi.p'
phantom.save_data(filename)

phantom.load(filename)

# with open(filename, 'wb') as outfile:
#     pickle.dump(data, outfile)
#
# with open(filename, 'rb') as infile:
#     data_loaded = pickle.load(infile)



# def load_data(filename):
#     # open json data
#     with open(filename) as file:
#         data = yaml.load(file)
#     return data
#
#
# def simulate_data(phantom: np.array = None, seq_file: str = 'example/example_test.seq', b0: float = 3,
#                   gamma: float = 267.5153, scale: float = 1, noise: bool = False, cest_pools = None, test_mode: bool = False):
#     # generate and plot phantom
#     if not phantom:
#         phantom = Phantom()
#         phantom.set_defaults()
#         phantom_fig = phantom.plot()
#
#     # unpack simulation parameters from phantom
#     assert phantom.count_layers() >= 5
#     p_t1, p_t2, p_b0, p_b1, p_f = [phantom[i] for i in range(5)]
#
#     locs, n_locs = get_locs(phantom, auto_range=test_mode)
#
#     # simulation for each phantom pixel in locs
#     tqdm_simulation = tqdm(locs)
#     time0 = time()
#     simulations = {}
#     for loc in tqdm_simulation:
#         # print('Simulation', locs.index(loc)+1, 'of', n_locs)
#         # define simulation parameters
#         sp = Params()
#         # define inhomogeneities from inhomogeneity maps
#         b0_inhom = p_b0[loc]
#         rel_b1 = p_b1[loc]
#         sp.set_scanner(b0=b0, gamma=gamma, b0_inhom=b0_inhom, rel_b1=rel_b1)
#         # define water pool from T1 and T2 maps
#         r1_w = 1 / p_t1[loc]
#         r2_w = 1 / p_t2[loc]
#         sp.set_water_pool(r1=r1_w, r2=r2_w)
#         for n in range(len(cest_pools)):
#             r1 = r1_w  # [Hz]
#             r2 = cest_pools[n]['r2'] # [Hz]
#             k = cest_pools[n]['k']  # exchange rate[Hz]
#             # define fractions from fraction map
#             f = p_f[loc]  # rel
#             dw = cest_pools[n]['dw']  # [ppm]
#             sp.set_cest_pool(r1=r1, r2=r2, k=k, f=f, dw=dw)
#         sp.set_m_vec(scale)
#         # start the simulation for this pixel
#         Sim = BMCTool(sp, seq_file)
#         Sim.run(par_calc=True)
#         # retrieve simulated spectrum
#         m_out = Sim.Mout
#         mz = sp.get_zspec(m_out, m0=False)
#         simulations.update({loc: sp})
#     time1 = time()
#     secs = time1 - time0
#     print("Simulations took", secs, "s.")
#
#     # create phantom images of all magnetizations at each offsets
#     offsets = np.array(get_offsets(seq_file))
#     phantom_sim = np.zeros([len(offsets), 128, 128])
#     for o in range(len(offsets)):
#         for k in list(simulations.keys()):
#             if noise:
#                 zspec = sim_noise(simulations[k].zspec[o])
#             else:
#                 zspec = simulations[k].zspec[o]
#             phantom_sim[o, k[0], k[1]] = zspec
#
#     # z_specs = {k : simulations[k].zspec.tolist() for k in simulations.keys()}
#
#     # save data as json
#     today = date.today().strftime("%Y-%m-%d")
#     data = {}
#     data['B0'] = b0
#     data['gamma'] = gamma
#     data['scale'] = scale
#     data['phantom'] = phantom.tolist()
#     data['sim_locs'] = list(locs)
#     # data['z_specs_k'] = list(z_specs.keys())
#     # data['z_specs_v'] = [v.tolist() for v in z_specs.values()]
#     data['phantom_sim'] = phantom_sim.tolist()
#     data['offsets'] = offsets.tolist()
#     data['n_cest_pools'] = len(sp.cest_pools)
#     seq_name = seq_file.split('/')[-1].replace('.seq', '')
#     with open('example/data/phantom_data_{seq_name}_{n}pools_{date}.yaml'.format(n=data['n_cest_pools'], date=today,
#                                                                                 seq_name=seq_name), 'w') as outfile:
#         yaml.dump(data, outfile)
#     return data


# simulate

# load data
# data = load_data('example/data/data_wasabi_test.txt')

offsets = np.array(data['offsets'])
locs = [tuple(loc) for loc in data['sim_locs']] # if undefined use code from function simulate_data
phantom = np.array(data['phantom'])
phantom_sim = np.array(data['phantom_sim'])
noisy_phantom_sim = sim_noise(phantom_sim, is_phantom=True)
# z_specs = {data['z_specs_k'][i]: data['z_specs_v'][i] for i in range(len(data['z_specs_k']))}
z_specs = {}
for loc in locs:
    z = np.array([phantom_sim[o][loc] for o in range(len(offsets))])
    z_noisy = sim_noise(z, is_zspec=True)
    z_specs.update({loc: z_noisy})

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
tmp = ax_im.imshow(noisy_phantom_sim[idx])
plt.title("$Z({\Delta}{\omega})$ at offset " + str(offsets[idx]))
plt.colorbar(tmp)
# plt.show()

# plot some tissue spectra
# fig2 = figure()
ax_t = plt.subplot(122)
ax_t.set_ylim([0, 1])
ax_t.set_ylabel('$Z({\Delta}{\omega})$')
ax_t.set_xlabel('Offsets')
labels = ["gm top", "gm mid", "gm bottom", "n1", "n2"]  # "wm", "csf"]
locs = [(17, 64), (57, 64), (108, 64), (95, 60), (95, 80)] # (41, 50), (41, 78)]  # locs = [(61, 22), (61, 70)]
for i in range(len(locs[:5])):
    # TODO something is wrong with the indexing - matplotlib != numpy? imshow != annotate?
    mz = z_specs[locs[i]]
    plt.plot(offsets, mz, '.--', label=labels[i])
plt.gca().invert_xaxis()
plt.legend()
plt.title('Z-Spectra for tifferent tissue types and phantom locations.')
for i in range(len(locs[:5])):
    ax_im.annotate(s=labels[i], xy=locs[i][::-1], arrowprops={'arrowstyle': 'simple'}, xytext=(locs[i][1]+5, locs[i][0]+5))
fig.show()

# # plot some fraction spectra
# fig3, ax1 = plt.subplots()
# ax1.set_ylim([0, 1])
# ax1.set_ylabel('Z')
# ax1.set_xlabel('Offsets')
# labels = ["gm", "wm f=min", "wm f=max"]
# locs = [(60, 40), (61, 40), (61, 85)]
# for i in range(len(locs)):
#     mz = simulations[locs[i]].zspec
#     plt.plot(offsets, mz, '.--', label=labels[i])
# plt.gca().invert_xaxis()
# plt.legend()
# plt.show()
