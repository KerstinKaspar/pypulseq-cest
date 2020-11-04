"""
phantom.py
    define a phantom with simulation parameters for CEST or WASABI simulations
"""

import numpy as np
import matplotlib.pyplot as plt
from phantom.tissue_library import get_t1, get_t2
from sim_bmc.bmc_tool_v2 import BMCTool
from sim.params import Params
# from phantom.plot_phantom import plot_phantom
from sim.eval import get_offsets
from sim.util import sim_noise
from time import time
import json
from datetime import date
from tqdm import tqdm


class Phantom():

    def __init__(self, npx: int = 128, b0: float = 3, tissues: list = None, compartments: list = None):
        self.layers = []
        self.t1 = None
        self.t2 = None
        self.b0_shift = None
        self.b1_inhom = None
        self.fractions = None
        self.noise = None
        self.npx = npx
        self.base = [[0., .6900, .920, 0., 0., 0.]]
        self.tissues, self.compartments = self._set_tissues(tissues, compartments)
        self.b0 = b0
        self.locs, self.n_locs = self._locate()
        self.simulated = None
        self.z_specs = None
        # TODO save sim data or not? also review load and sim functions
        # self.sim_data = None

    def set_t1(self, f_tissue: (str, None) = 'wm', noise_tissue: (str, None) = 'wm') -> np.array:
        """
        creates a phantom_examples for the stated tissue types (gm: gray matter, wm: white matter and csf: cerebrospinal fluid)
        with the according t1 values from tissue_library.py and optionally a range of pool-fraction-parameters for
        one of the tissue types (if f_matter = "gm", "wm" or "csf").
        :param  f_tissue: str (optional tissue type to create a fraction range, default = "wm", set to None for no
                fraction range in the phantom)
        :param noise_tissue: str (optional tissue type to create a noise range, default = "wm", set to None for no
                noise range in the phantom)
        :return phantom_t: np.array (size [npx, npx] containing T1 values for each pixel
        """
        base = self.base.copy()
        for i in range(len(self.tissues)):
            t_comp = self.compartments[i].copy()
            t_comp[0] = get_t1(tissue=self.tissues[i], b0=0)
            base.append(t_comp)
        phantom_t = self._phantom_ellipses(npx=self.npx, ellipses=base)
        if type(f_tissue) is str:
            phantom_t[84:90, 44:84] = get_t1(tissue=f_tissue, b0=self.b0)
        if type(noise_tissue) == str:
            phantom_t[94:100, 44:84] = get_t1(tissue=noise_tissue, b0=self.b0)
        self.t1 = phantom_t
        self.layers.append('t1')
        return phantom_t

    def set_t2(self,  f_tissue: (str, None) = 'wm', noise_tissue: (str, None) = 'wm') -> np.array:
        """
        creates a phantom_examples for the stated tissue types (gm: gray matter, wm: white matter and csf: cerebrospinal fluid)
        with the according t2 values from tissue_library.py and optionally a range of pool-fraction-parameters for
        one of the tissue types (if f_matter = "gm", "wm" or "csf").
        :param  f_tissue: str (optional tissue type to create a fraction range, default = "wm", set to None for no
                fraction range in the phantom)
        :param noise_tissue: str (optional tissue type to create a noise range, default = "wm", set to None for no
                noise range in the phantom)
        :return phantom_t: np.array (size [ npx, npx]  containing T2 values for each pixel
        """
        base = self.base.copy()
        for i in range(len(self.tissues)):
            t_comp = self.compartments[i].copy()
            t_comp[0] = get_t2(tissue=self.tissues[i], b0=0)
            base.append(t_comp)
        phantom_t = self._phantom_ellipses(npx=self.npx, ellipses=base)
        if type(f_tissue) is str:
            phantom_t[84:90, 44:84] = get_t2(tissue=f_tissue, b0=self.b0)
        if type(noise_tissue) == str:
            phantom_t[94:100, 44:84] = get_t2(tissue=noise_tissue, b0=self.b0)
        self.t2 = phantom_t
        self.layers.append('t2')
        return phantom_t

    def set_t1_t2(self, self_tissue: (str, None) = 'wm', noise_tissue: (str, None) = 'wm') -> np.array:
        self.set_t1(self_tissue, noise_tissue)
        self.set_t2(self_tissue, noise_tissue)
        return self.t1, self.t2

    def get_t1(self):
        return self.t1

    def get_t2(self):
        return self.t2

    def get_t1_t2(self):
        return self.t1, self.t2

    def set_b0_shift(self, min_shift: float = -0.3, max_shift: float = 0.3) -> np.array:
        """
        creating a phantom with linear B0 field inhomogeneities
        :param npx: pixel size of the phantom
        :param min_shift: minimal B0 shift in ppm
        :param max_shift: maximal B0 shift in ppm
        :return phantom_b1: array of size (1, npx, npx) with values for B0-shift
        """
        phantom_b0 = self._phantom_ellipses(npx=self.npx, ellipses=self.base)
        b0_inhom = np.linspace(min_shift, max_shift, self.npx * self.npx).reshape(self.npx, self.npx)
        phantom_b0 = phantom_b0 * b0_inhom
        self.b0_shift = phantom_b0
        self.layers.append('b0_shift')
        return phantom_b0

    def set_b1_inhom(self, min_inhom: float = -0.3, max_inhom: float = 0.3) -> np.array:
        """
        creating a phantom with radial B1 inhomogeneities
        :param min_inhom: minimal b1 inhomogeneity in percent (factor in range -1 and 1)
        :param max_inhom: maximal b1 inhomogeneity in percent (factor in range -1 and 1)
        :return phantom_b1: array of size (1, npx, npx) with values for relative B1 of range 1-min_inhom and 1+ max_inhom
        """
        phantom_b1 = self._phantom_ellipses(npx=self.npx, ellipses=self.base)
        inhom_range = max_inhom - min_inhom
        x = y = np.linspace(-inhom_range, inhom_range, 128)
        xx, yy = np.meshgrid(x, y)
        r = np.sqrt(xx ** 2 + yy ** 2)
        b1_inhom = np.ones((128, 128)) * 0.3 - r
        phantom_b1 = phantom_b1 * b1_inhom + 1
        self.b1_inhom = phantom_b1
        self.layers.append('b1_inhom')
        return phantom_b1

    def set_fractions(self, f_base: float = 10e-3, n_fractions: int = 10, f_range: tuple = (0, 10e-3)) \
            -> np.array:
        """
        defining a phantom with a section of bar-shaped continouously spaced fraction parameters
        :param npx: pixel size of the phantom
        :param f_base: fraction parameter for the phantom outside the fraction bar
        :param n_fractions: number of fractions to split the fraction bar into
        :param f_range: (min, max) of the fraction parameters in the fraction bar
        :return phantom_f: array of size (1, npx, npx)
        """
        compartments = np.linspace(44, 84, n_fractions)
        fractions = np.linspace(f_range[0], f_range[1], n_fractions)
        base = self.base.copy()
        base[0] = f_base
        phantom_f = self._phantom_ellipses(npx=self.npx, ellipses=base)
        for i in range(n_fractions-1):
            phantom_f[84:90, int(round(compartments[i])):int(round(compartments[i+1]))] = fractions[i]
        self.fractions = phantom_f
        self.layers.append('fractions')
        return phantom_f

    def get_fractions(self):
        return self.fractions

    def set_noise(self, mean: float = 0, std_base: float = 0, n: int = 10, std_max: float = 0.1) -> np.array:
        compartments = np.linspace(44, 84, n)
        # vars = np.linspace(var_base, var_max, n)
        # sigmas = vars ** 0.5
        sigmas = np.linspace(std_base, std_max, n)
        phantom_n = self._phantom_ellipses(npx=self.npx, ellipses=self.base)
        noise = np.random.normal(mean, sigmas[0], phantom_n.shape)
        phantom_n = phantom_n * noise
        for i in range(n-1):
            idx = [int(round(compartments[i])), int(round(compartments[i+1]))]
            noise = np.random.normal(mean, sigmas[i], phantom_n[0, 94:100, idx[0]:idx[1]].shape)
            phantom_n[94:100, idx[0]:idx[1]] = noise
        self.noise = phantom_n
        self.layers.append('noise')
        return phantom_n

    def get_noise(self):
        return self.noise

    def count_layers(self):
        return len(self.layers)

    def get_layers(self):
        return {k: v for (k, v) in self.__dict__.items() if k in self.layers}

    def set_defaults(self, fractions: bool = True, noise: bool = False) -> np.array:
        """
        building a default phantom at 3T with parameters for a large GM ellipse, 2 WM ellipses, 1 CSF ellipse,
        optionally with a bar of WM parameters and continuously spaced fractions
        :param fractions: bool to define the fraction option (default: True)
        :param noise: bool to define the noise option (default: True)
        :return phantom: array of size (4, npx, npx) without or (5, npx, npx) with fractions containing the T1, T2,
        B0 inhomogeneities, B1 inhomogeneities and possibly fractions for each pixel respectively
        """
        self.set_t1_t2()
        self.set_b0_shift()
        self.set_b1_inhom()
        if fractions:
            self.set_fractions()
        if noise:
            self.set_noise()
        return self

    def stack(self):
        """
        building a phantom from the individual parameter layers
        :return phantom: array of size (layers, npx, npx) containing the T1, T2,
        B0 shift, B1 inhomogeneities and possibly fractions and noise for each pixel respectively
        """
        phantom = np.stack([v for (k, v) in self.__dict__.items() if k in self.layers])
        return phantom

    def unstack(self, phantom: np.array):
        n_layers = len(phantom)
        self.t1, self.t2, self.b0_shift, self.b1_inhom = [phantom[i] for i in range(4)]
        if n_layers > 4:
            self.fractions = phantom[4]
        if n_layers > 5:
            self.noise = phantom[5]
        return [phantom[i] for i in range(n_layers)]

    def load(self, filename: str):
        # open json data
        with open(filename) as json_file:
            data = json.load(json_file)
        phantom = np.array(data['phantom'])
        self.unstack(phantom=phantom)
        self.simulated = data['phantom_sim']
        # self.sim_data = data
        self.b0 = data['B0']
        # TODO reimplement for new simulation data
        # self.locs = data['locs']
        return data

    def simulate(self, seq_file: str = 'example/example_test.seq', b0: float = 3, gamma: float = 267.5153,
                 scale: float = 1, noise: bool = False, cest_pools=None, export_file: (bool, str) = False):
        # if no phantom is defined
        if len(self.layers) < 1:
            self.set_defaults()
        # simulation for each phantom pixel in locs
        tqdm_simulation = tqdm(self.locs)
        time0 = time()
        simulations = {}
        for loc in tqdm_simulation:
            # print('Simulation', locs.index(loc)+1, 'of', n_locs)
            # define simulation parameters
            sp = Params()
            # define inhomogeneities from inhomogeneity maps
            b0_inhom = self.b0_shift[loc]
            rel_b1 = self.b1_inhom[loc]
            sp.set_scanner(b0=b0, gamma=gamma, b0_inhom=b0_inhom, rel_b1=rel_b1)
            # define water pool from T1 and T2 maps
            r1_w = 1 / self.t1[loc]
            r2_w = 1 / self.t2[loc]
            sp.set_water_pool(r1=r1_w, r2=r2_w)
            for n in range(len(cest_pools)):
                r1 = r1_w  # [Hz]
                r2 = cest_pools[n]['r2']  # [Hz]
                k = cest_pools[n]['k']  # exchange rate[Hz]
                # define fractions from fraction map
                f = self.fractions[loc]  # rel
                dw = cest_pools[n]['dw']  # [ppm]
                sp.set_cest_pool(r1=r1, r2=r2, k=k, f=f, dw=dw)
            sp.set_m_vec(scale)
            # start the simulation for this pixel
            Sim = BMCTool(sp, seq_file)
            Sim.run(par_calc=True)
            # retrieve simulated spectrum
            m_out = Sim.Mout
            mz = sp.get_zspec(m_out)
            simulations.update({loc: sp})
        time1 = time()
        secs = time1 - time0
        print("Simulation took", secs, "s.")

        # create phantom images of all magnetizations at each offsets
        offsets = np.array(get_offsets(seq_file))
        phantom_sim = np.zeros([len(offsets), 128, 128])
        for o in range(len(offsets)):
            for k in list(simulations.keys()):
                if noise:
                    zspec = sim_noise(simulations[k].zspec[o])
                else:
                    zspec = simulations[k].zspec[o]
                phantom_sim[o, k[0], k[1]] = zspec

        today = date.today().strftime("%Y-%m-%d")
        data = {}
        data['B0'] = b0
        data['gamma'] = gamma
        data['scale'] = scale
        data['phantom'] = self.stack().tolist()
        data['sim_locs'] = list(self.locs)
        data['phantom_sim'] = phantom_sim.tolist()
        data['offsets'] = offsets.tolist()
        data['n_cest_pools'] = len(sp.cest_pools)
        if export_file:
            if export_file is not str:
                seq_name = seq_file.split('/')[-1].replace('.seq', '')
                export_file = 'example/data/phantom_data_{seq_name}_{n}pools_{date}.txt'.format(n=data['n_cest_pools'],
                                                                                                date=today,
                                                                                                seq_name=seq_name)
            else:
                with open(export_file, 'w') as outfile:
                    json.dump(data, outfile)
        self.simulated = phantom_sim
        # self.sim_data = data
        return data

    def get_z(self, locs: (list, tuple) = None, noise: bool = True):
        if not locs:
            locs = self.locs
        z_specs = {}
        if type(locs) is tuple:
            locs = [locs]
        for loc in locs:
            z = np.array([self.simulated[o][loc[0]][loc[1]] for o in range(len(self.simulated))])
            if noise:
                z = sim_noise(z, is_zspec=True)
            z_specs.update({tuple(loc): z})
        self.z_specs = z_specs
        return z_specs

    def plot(self, export: (bool, str) = False):
        titles = [l.capitalize().replace('_', ' ') for l in self.layers]
        phantom = self.stack()
        n_plots = phantom.shape[0]
        fig, ax = plt.subplots(1, n_plots)
        for p in range(len(ax)):
            ax[p].imshow(phantom[p])
            ax[p].title.set_text('Phantom' + titles[p])
        if export:
            if type(export) is not str:
                today = date.today().strftime("%Y-%m-%d")
                filename = 'example/output/phantom_{date}.jpg'.format(date=today)
            else:
                filename = export
            plt.savefig(filename)
        plt.show()
        return fig

    def plot_zspec(self, offsets: np.array = None, dw: float = None, locs: (tuple, list, dict) = None,
                   default_samples: bool = False, export: (bool, str) = False):
        if dw and offsets:
            idx = int(np.where(offsets == offsets[np.abs(offsets - dw).argmin()])[0])
        elif not dw:
            idx = np.random.randint(len(self.simulated))
        fig = plt.figure()
        ax_im = plt.subplot(121)
        tmp = ax_im.imshow(self.simulated[idx])
        title = "$Z({\Delta}{\omega})$"
        if offsets.any():
            title += " at offset " + str(offsets[idx])
        plt.title(title)
        plt.colorbar(tmp)

        # plot some tissue spectra
        ax_t = plt.subplot(122)
        ax_t.set_ylim([0, 1])
        ax_t.set_ylabel('$Z({\Delta}{\omega})$')

        if default_samples:
            labels = ["gm top", "gm mid", "gm bottom", "n1", "n2"]
            locs = [(17, 64), (57, 64), (108, 64), (95, 60),
                    (95, 80)]
        elif locs:
            if type(locs) is dict:
                labels = [k for k in locs.keys()]
                locs = [v for v in locs.values()]
            else:
                if type(locs) is tuple:
                    locs = [locs]
                if type(locs) is list:
                    labels = ['loc ' + str(l) for l in locs]
                else:
                    raise ValueError('locs has to be of type tuple, list(tuples) or dict({labels: locs}')
        else:
            idx = np.random.randint(len(self.locs))
            locs = [self.locs[idx]]
            labels = ['random loc ' + str(l) for l in locs]

        if not self.z_specs:
            self.get_z(locs=locs)

        if offsets.any():
            ax_t.set_xlabel('Offsets')
            for i in range(len(locs)):
                mz = self.z_specs[locs[i]]
                plt.plot(offsets, mz, '.--', label=labels[i])
        else:
            ax_t.set_xlabel('Datapoints')
            for i in range(len(locs)):
                mz = self.z_specs[locs[i]]
                plt.plot(mz, '.--', label=labels[i])
        plt.gca().invert_xaxis()
        plt.legend()
        plt.title('Z-Spec vs phantom location')
        for i in range(len(locs)):
            ax_im.annotate(s=labels[i], xy=locs[i][::-1], arrowprops={'arrowstyle': 'simple'},
                           xytext=(locs[i][1] + 5, locs[i][0] + 5))
        # plt.show()
        if export:
            if type(export) is not str:
                today = date.today().strftime("%Y-%m-%d")
                filename = 'example/output/zspec_{date}.jpg'.format(date=today)
            else:
                filename = export
            plt.savefig(filename)
        return fig

    @staticmethod
    def _phantom_ellipses(npx: int, ellipses: np.array = None) -> np.array:
        """
        converts the ellipse definitions into ellipses with the specified intensities on the array grid
        :param npx: number of pixels for the phantom
        :param ellipses: list of ellipse definitions
        :return p: array of size npx x npx
        """
        # Create blank image
        p = np.zeros((npx, npx))

        # Create the pixel grid
        ygrid, xgrid = np.mgrid[-1:1:(1j * npx), -1:1:(1j * npx)]

        for e in ellipses:
            I = e[0]
            a2 = e[1] ** 2
            b2 = e[2] ** 2
            x0 = e[3]
            y0 = e[4]
            phi = e[5] * np.pi / 180  # Rotation angle in radians

            # Create the offset x and y values for the grid
            x = xgrid - x0
            y = ygrid - y0

            cos_p = np.cos(phi)
            sin_p = np.sin(phi)

            # Find the pixels within the ellipse
            locs = (((x * cos_p + y * sin_p) ** 2) / a2
                    + ((y * cos_p - x * sin_p) ** 2) / b2) <= 1

            # Add the ellipse intensity to those pixels
            p[locs] += I

        return p

    @staticmethod
    def _set_tissues(tissues: list = None, compartments: list = None):
        """
        Setting a list of tissue options to handle library look up and compartments to simulate the tissues in.
        :param tissues: list of string parameters to look up tissue parameters in the tissue_library.py file (default
                        ["gm", "wm", "csf"])
        :param compartments: list of lists, individually defining ellipses to simulate the tissues in, default:
                            [[0, .6624, .874, 0., -.0184, 0.],
                            [0, .16, .41, -.22, -.2, 18],
                            [0, .12, .31, .22, -.12, -12]]
        :return: tissues, compartments, either set or default
        """
        if not tissues:
            tissues = ["gm", "wm", "csf"]
        if not compartments:
            compartments = [[0, .6624, .874, 0., -.0184, 0.],
                            [0, .16, .41, -.22, -.2, 18],  # [0.5, .16, .41, -.22, -.2, 18],
                            [0, .12, .31, .22, -.12, -12]]  # [0.4, .11, .31, .22, -.12, -12]]
        if len(tissues) != len(compartments):
            raise AssertionError('List lengths of tissues and compartments have to match. Tissues: ', len(tissues),
                                 ', compartments: ', len(compartments))
        return tissues, compartments

    def _locate(self, return_n: bool = True):
        base = self.base.copy()
        base[0][0] = 1
        phantom = self._phantom_ellipses(self.npx, base)
        n_rows, n_cols = phantom.shape
        locs = []
        idces = list(np.ndindex(n_rows, n_cols))
        for loc in idces:
            if phantom[loc] != 0:
                locs.append(loc)
        n_locs = len(locs)
        if return_n:
            return locs, n_locs
        else:
            return locs


def load_data(filename):
    # open json data
    with open(filename) as json_file:
        data = json.load(json_file)
    data['offsets'] = np.array(data['offsets'])
    data['locs'] = [tuple(loc) for loc in data['sim_locs']]  # if undefined use code from function simulate_data
    data['phantom'] = np.array(data['phantom'])
    data['phantom_sim'] = np.array(data['phantom_sim'])
    return data


def simulate_data(phantom: Phantom = None, seq_file: str = 'example/example_test.seq', b0: float = 3,
                  gamma: float = 267.5153, scale: float = 1, noise: bool = False, cest_pools=None,
                  test_mode: bool = False):
    # generate and plot phantom
    if not phantom:
        phantom = Phantom()
        phantom.set_defaults()
        phantom_fig = plot_phantom(phantom)

    # unpack simulation parameters from phantom
    assert len(phantom) >= 5
    p_t1, p_t2, p_b0, p_b1, p_f = [phantom[i] for i in range(5)]
    locs, n_locs = get_locs(phantom, auto_range=test_mode, return_n=True)

    # simulation for each phantom pixel in locs
    tqdm_simulation = tqdm(locs)
    time0 = time()
    simulations = {}
    for loc in tqdm_simulation:
        # print('Simulation', locs.index(loc)+1, 'of', n_locs)
        # define simulation parameters
        sp = Params()
        # define inhomogeneities from inhomogeneity maps
        b0_inhom = p_b0[loc]
        rel_b1 = p_b1[loc]
        sp.set_scanner(b0=b0, gamma=gamma, b0_inhom=b0_inhom, rel_b1=rel_b1)
        # define water pool from T1 and T2 maps
        r1_w = 1 / p_t1[loc]
        r2_w = 1 / p_t2[loc]
        sp.set_water_pool(r1=r1_w, r2=r2_w)
        for n in range(len(cest_pools)):
            r1 = r1_w  # [Hz]
            r2 = cest_pools[n]['r2']  # [Hz]
            k = cest_pools[n]['k']  # exchange rate[Hz]
            # define fractions from fraction map
            f = p_f[loc]  # rel
            dw = cest_pools[n]['dw']  # [ppm]
            sp.set_cest_pool(r1=r1, r2=r2, k=k, f=f, dw=dw)
        sp.set_m_vec(scale)
        # start the simulation for this pixel
        Sim = BMCTool(sp, seq_file)
        Sim.run(par_calc=True)
        # retrieve simulated spectrum
        m_out = Sim.Mout
        mz = sp.get_zspec(m_out, m0=False)
        simulations.update({loc: sp})
    time1 = time()
    secs = time1 - time0
    print("Simulations took", secs, "s.")

    # create phantom images of all magnetizations at each offsets
    offsets = np.array(get_offsets(seq_file))
    phantom_sim = np.zeros([len(offsets), 128, 128])
    for o in range(len(offsets)):
        for k in list(simulations.keys()):
            if noise:
                zspec = sim_noise(simulations[k].zspec[o])
            else:
                zspec = simulations[k].zspec[o]
            phantom_sim[o, k[0], k[1]] = zspec

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


def get_locs(phantom, set_range: tuple = None, auto_range: bool = False, return_n: bool = False):
    if phantom.ndim == 3:
        _, n_rows, n_cols = phantom.shape
    elif phantom.ndim == 2:
        n_rows, n_cols = phantom.shape
    else:
        raise Exception("Phantom needs to have to or 3 dimensions, not", phantom.ndim)
    locs = []
    idces = list(np.ndindex(n_rows, n_cols))
    if auto_range:
        set_range = (128*60, 128*62)
    if set_range:
        idces = idces[range(set_range)]
    if phantom.ndim == 3:
        for loc in idces:
            if phantom[0][loc] != 0:
                locs.append(loc)
    elif phantom.ndim == 2:
        for loc in idces:
            if phantom[loc] != 0:
                locs.append(loc)
    n_locs = len(locs)
    if return_n:
        return locs, n_locs
    else:
        return locs


def get_z(phantom_sim: np.array, locs: (list, tuple) = None):
    if not locs:
        locs = get_locs(phantom_sim)
    z_specs = {}
    if type(locs) is tuple:
        locs = [locs]
    for loc in locs:
        z = np.abs([phantom_sim[o][loc] for o in range(len(phantom_sim))])
        z_noisy = sim_noise(z, is_zspec=True)
        z_specs.update({tuple(loc): z_noisy})
    return z_specs


def plot_phantom(phantom):
    titles = ['T1', 'T2', 'B0 inhom.', 'B1 inhom.', 'fractions', 'noise']
    n_plots = phantom.shape[0]
    fig, ax = plt.subplots(1, n_plots)
    for p in range(len(ax)):
        ax[p].imshow(phantom[p])
        ax[p].title.set_text('Phantom' + titles[p])
    plt.show()
    plt.savefig('example/test/phantom_examples.jpg')
    return fig


def plot_phantom_zspec(phantom_sim: np.array, z_specs: np.array = None, offsets: np.array = None, dw: float = None, locs: (tuple, list, dict) = None,
                       test_mode: bool = False):
    if dw and offsets:
        idx = int(np.where(offsets == offsets[np.abs(offsets - dw).argmin()])[0])
    elif not dw:
        idx = np.random.randint(len(phantom_sim))
    fig = plt.figure()
    ax_im = plt.subplot(121)
    tmp = ax_im.imshow(phantom_sim[idx])
    title = "$Z({\Delta}{\omega})$"
    if offsets:
        title += " at offset " + str(offsets[idx])
    plt.title(title)
    plt.colorbar(tmp)
    # plt.show()

    # plot some tissue spectra
    ax_t = plt.subplot(122)
    ax_t.set_ylim([0, 1])
    ax_t.set_ylabel('$Z({\Delta}{\omega})$')

    if test_mode:
        labels = ["gm top", "gm mid", "gm bottom", "n1", "n2"]  # "wm", "csf"]
        locs = [(17, 64), (57, 64), (108, 64), (95, 60), (95, 80)]  # (41, 50), (41, 78)]  # locs = [(61, 22), (61, 70)]
    elif locs:
        if type(locs) is dict:
            labels = [k for k in locs.keys()]
            locs = [v for v in locs.values()]
        else:
            if type(locs) is tuple:
                locs = [locs]
            if type(locs) is list:
                labels = ['loc ' + str(l) for l in locs]
            else:
                raise ValueError('locs has to be of type tuple, list(tuples) or dict({labels: locs}')
    else:
        all_locs = get_locs(phantom_sim)
        idx = np.random.randint(len(all_locs))
        locs = [all_locs[idx]]
        labels = ['random loc ' + str(l) for l in locs]

    if not z_specs:
        z_specs = get_z(phantom_sim=phantom_sim, locs = locs)

    if offsets:
        ax_t.set_xlabel('Offsets')
        for i in range(len(locs)):
            mz = z_specs[locs[i]]
            plt.plot(offsets, mz, '.--', label=labels[i])
    else:
        ax_t.set_xlabel('Datapoints')
        for i in range(len(locs)):
            mz = z_specs[locs[i]]
            plt.plot(mz, '.--', label=labels[i])
    plt.gca().invert_xaxis()
    plt.legend()
    plt.title('Z-Spec vs phantom location')
    for i in range(len(locs)):
        ax_im.annotate(s=labels[i], xy=locs[i][::-1], arrowprops={'arrowstyle': 'simple'},
                       xytext=(locs[i][1] + 5, locs[i][0] + 5))
    fig.show()
    return fig

