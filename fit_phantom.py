"""
fit_phantom.py
    functions for a numerical fit of simulated phantom data
"""

import numpy as np
from phantom.phantom import Phantom #build_default_phantom, simulate_data, load_data, get_z, get_locs, plot_phantom, plot_phantom_zspec
from datetime import date
from lmfit import Model
from time import time
import random
import matplotlib.pyplot as plt
import json
from pypulseq.Sequence.sequence import Sequence


filename = 'example/data/data_wasabi_test.txt'
seq_file = 'example/wasabi/example_wasabi.seq'

# LOAD
phantom = Phantom()
data = phantom.load(filename)

offsets = np.array(data['offsets'])

z_specs = phantom.get_z()
# z_fig = phantom.plot_zspec(offsets=offsets, dw=0, locs= (17, 64),
#                          export='example/test/test_{date}.jpg'.format(date=date.today().strftime("%Y-%m-%d")))


class Wasabi_fit:
    def __init__(self, phantom, data, seq_file=None, b1_nom=None, t_p=None):#
        self.b0 = phantom.b0
        self.gamma = data['gamma'] / (2 * np.pi)
        if seq_file:
            self.b1_nom, self.t_p = self._get_b1_tp(seq_file, self.gamma)  # 1.25*b0, 0.005
        elif b1_nom and t_p:
            self.b1_nom = b1_nom
            self.t_p = t_p
        else:
            raise Exception('You need to define either a seq-file or b1_nom and t_p for a fit.')

    @staticmethod
    def _wasabi(x, db0, b1, c, d, freq, tp):
        """WASABI function for simultaneous determination of B1 and B0. For more information read:
        Schuenke et al. Magnetic Resonance in Medicine, 77(2), 571–580. https://doi.org/10.1002/mrm.26133"""
        return np.abs(c - d * np.square(np.sin(np.arctan((b1 / (freq / gamma)) / (x - db0)))) *
                      np.square(np.sin(np.sqrt(np.square(b1 / (freq / gamma)) +
                                               np.square(x - db0)) * freq * 2 * np.pi * tp / 2)))

    @staticmethod
    def _get_b1_tp(source: (str, object), gamma):
        if type(source) is str:
            try:
                seq = Sequence()
                seq.read(source)
            except ValueError:
                print('Could not read sequence from file ', source)
        else:
            try:
                seq = source.seq
            except ValueError:
                print('Could not read seq file from the given input. Pleas give a sequence filepath or a BMCTool '
                      'object after simulation.')
        try:
            for i in range(2, 10):
                block = seq.get_block(i)
                if hasattr(block, 'rf'):
                    break
        except AttributeError:
            print('Can\'t find rf pulse in the first 10 blocks of the sequence.')
        t_p = block.rf.t.max
        amp = np.real(block.rf.signal)
        b1_nom = amp / gamma
        return b1_nom, t_p



model = Model(wasabi)
params = model.make_params()
params['freq'].set(gamma * b0, vary=False)
params['tp'].set(tp, vary=False)
params['db0'].set(0)
params['b1'].set(b1_nom, min=0)
params['c'].set(0.9)
params['d'].set(1.4, min=0)

best_vals = {}
best_fits = {}

count = 0
n_total = len(z_specs)
loopstart = time()
keys = list(z_specs.keys())
for i in range(n_total):
    data = z_specs[keys[i]]

    # set parameters within +/- 10% of true value to increase fit rebustness.
    # Of course this can NOT be done in real measurements later, because we don't know the true value in advance
    params['db0'].set(random.uniform(-0.3, 0.3))
    params['b1'].set(b1_nom * random.uniform(0.7, 1.3), min=0)

    # perform fitting
    res_ = model.fit(np.abs(data), params, x=offsets, max_nfev=100)
    vals = res_.best_values
    fit = res_.best_fit

    # write values
    best_vals.update({keys[i]: vals})
    best_fits.update({keys[i]: fit})

    # update progress bar and estimated time
    b = int(50 * count / n_total)
    left = int(50 - b)
    count += 1
    loopremain = (time() - loopstart) * (n_total - count) / (count * 50)
    print('[' + '#' * b + '-' * left + ']' +
          f' Estimated remaining time {loopremain:.1f} minutes.', end='\r')

# SAVE fit
output = {'best_vals': {str(k): v for k, v in best_vals.items()}, 'best_fits': {str(k): v.tolist() for k, v in best_fits.items()}}
with open(filename.replace('.txt', '_fit.txt'), 'w') as outfile:
    json.dump(output, outfile)

# LOAD fit data
with open(filename.replace('.txt', '_fit.txt')) as json_file:
    data = json.load(json_file)
vals = {eval(k): v for k, v in data['best_vals'].items()}
fits = {eval(k): np.array(v) for k, v in data['best_fits'].items()}

# PLOT fit
fig = plt.figure()
idx = random.randint(0, len(keys))
plt.plot(offsets, z_specs[keys[idx]], 'o', 'r', label='data')
plt.plot(offsets, fits[keys[idx]], '--', 'b', label='fit')
plt.legend()
plt.savefig('example/test/test_fit.jpg')
plt.show()

