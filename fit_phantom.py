"""
fit_phantom.py
    functions for a numerical fit of simulated phantom data
"""

from phantom.phantom import Phantom #build_default_phantom, simulate_data, load_data, get_z, get_locs, plot_phantom, plot_phantom_zspec
from phantom.analytic import WasabiFit

filename = 'example/data/data_wasabi_test.txt'
seq_file = 'example/wasabi/example_wasabi.seq'

# LOAD
phantom = Phantom()
data = phantom.load(filename)

model = WasabiFit(phantom=phantom, data=data, seq_file=seq_file)
vals, fits = model.fit()
model.save_output('example/output/test_fit.yaml')
model2 = WasabiFit(phantom=phantom, data=data, seq_file=seq_file)
vals_load, fits_load = model2.load_fit('example/output/test_fit.yaml')

model.plot()


