"""
fit_phantom.py
    functions for a numerical fit of simulated phantom data
"""

import numpy as np
from phantom.phantom import build_default_phantom, simulate_data, load_data, get_z, get_locs, plot_phantom, plot_phantom_zspec
from sim.util import sim_noise
from lmfit import Model

# # SIMULATE
# # generate and plot phantom
# phantom = build_default_phantom()
# # phantom_fig = plot_phantom(phantom)
# # set general simulation parameters
# seq_file = 'example/example_test.seq'
# b0 = 3  # T
# gamma = 267.5153  # rad/uT
# scale = 1
# data = simulate_data(phantom=phantom, seq_file=seq_file, b0=b0, gamma=gamma, scale=scale, noise=False, cest_pools=None)

# LOAD
data = load_data("example/data/data_wasabi_test.txt")

offsets = data['offsets']
locs = data['sim_locs']
phantom = data['phantom']
phantom_sim = data['phantom_sim']
noisy_phantom_sim = sim_noise(phantom_sim, is_phantom=True)
z_specs = get_z(noisy_phantom_sim, locs)
fig = plot_phantom_zspec(phantom_sim)


