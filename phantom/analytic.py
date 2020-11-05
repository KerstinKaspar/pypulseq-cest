"""
phantom.analytic.py
    contains the Wasabi_fit class to perform analytic fits on phantoms (using lmfit)
"""
import numpy as np
from datetime import date
from lmfit import Model
from time import time
import random
import matplotlib.pyplot as plt
import yaml
from pypulseq.Sequence.sequence import Sequence


class WasabiFit:
    def __init__(self, phantom, data, seq_file=None, b1_nom=None, tp=None, init_c=None, init_d=None):
        # data
        self.offsets = np.array(data['offsets'])
        self.z_specs = phantom.get_z()
        # params
        self.b0 = phantom.b0
        self.gamma = data['gamma'] / (2 * np.pi)
        if seq_file:
            self.b1_nom, self.tp = self._get_b1_tp(seq_file, self.gamma)  # 1.25*b0, 0.005
        elif b1_nom and tp:
            self.b1_nom = b1_nom
            self.tp = tp
        else:
            raise Exception('You need to define either a seq-file or b1_nom and t_p for a fit.')
        if init_c:
            self.init_c = init_c
        else:
            self.init_c = 0.9  #TODO
        if init_d:
            self.init_d = init_d
        else:
            self.init_d = 1.4 #TODO
        # output
        self.best_vals = {}
        self.best_fits = {}

    @staticmethod
    def _wasabi(x, db0, b1, c, d, freq, tp, gamma):
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
        tp = block.rf.t.max()
        amp = np.real(block.rf.signal)[0]
        b1_nom = amp / gamma
        return b1_nom, tp

    def fit(self):
        model = Model(self._wasabi)
        params = model.make_params()
        params['gamma'].set(self.gamma, vary=False)
        params['freq'].set(self.gamma * self.b0, vary=False)
        params['tp'].set(self.tp, vary=False)
        params['db0'].set(0)
        params['b1'].set(self.b1_nom, min=0)
        params['c'].set(self.init_c)
        params['d'].set(self.init_d, min=0)

        count = 0
        n_total = len(self.z_specs)
        loopstart = time()
        keys = list(self.z_specs.keys())
        print('Fitting data.')
        for i in range(n_total):
            model_data = self.z_specs[keys[i]]

            # set parameters within +/- 10% of true value to increase fit rebustness.
            # Of course this can NOT be done in real measurements later, because we don't know the true value in advance
            params['db0'].set(random.uniform(-0.3, 0.3))
            params['b1'].set(self.b1_nom * random.uniform(0.7, 1.3), min=0)

            # perform fitting
            res_ = model.fit(np.abs(model_data), params, x=self.offsets, max_nfev=100)
            vals = res_.best_values
            fit = res_.best_fit

            # write values
            self.best_vals.update({keys[i]: vals})
            self.best_fits.update({keys[i]: fit})

            # update progress bar and estimated time
            b = int(50 * count / n_total)
            left = int(50 - b)
            count += 1
            loopremain = (time() - loopstart) * (n_total - count) / (count * 50)
            print('[' + '#' * b + '-' * left + ']' +
                  f' Estimated remaining time {loopremain:.1f} minutes.', end='\r')

        return self.best_vals, self.best_fits

    def save_output(self, filename: str = None):
        output = {'best_vals': {str(k): v for k, v in self.best_vals.items()},
                  'best_fits': {str(k): v.tolist() for k, v in self.best_fits.items()}}
        if not filename:
            filename = 'example/output/analytic/wasabi_fit_{date}.yaml'.format(date=date.today().strftime("%Y-%m-%d"))
        with open(filename, 'w') as outfile:
            yaml.dump(output, outfile)

    def load_fit(self, filename):
        with open(filename.replace('.txt', '_fit.txt')) as infile:
            data = yaml.load(infile)
        self.best_vals = {eval(k): v for k, v in data['best_vals'].items()}
        self.best_fits = {eval(k): np.array(v) for k, v in data['best_fits'].items()}
        return self.best_vals, self.best_fits

    def plot(self, save_filename: str = None, loc: tuple = None):
        fig = plt.figure()
        if not loc:
            keys = list(self.z_specs.keys())
            idx = random.randint(0, len(keys))
            loc = keys[idx]
        plt.plot(self.offsets, self.z_specs[loc], 'o', 'r', label='data')
        plt.plot(self.offsets, self.best_fits[loc], '--', 'b', label='fit')
        plt.legend()
        if save_filename:
            plt.savefig(save_filename)
        plt.show()