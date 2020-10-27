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


def phantom_ellipses(npx: int, ellipses: np.array = None) -> np.array:
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


def phantom_noise(npx: int = 128, mean: float = 0, std_base: float = 0, n: int = 10, std_max: float = 0.1) -> np.array:
    compartments = np.linspace(44, 84, n)
    # vars = np.linspace(var_base, var_max, n)
    # sigmas = vars ** 0.5
    sigmas = np.linspace(std_base, std_max, n)
    phantom_n = np.zeros([1, npx, npx])
    phantom_base = [[1, .6900, .920, 0., 0., 0.]]
    phantom_n[0, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_base)
    noise = np.random.normal(mean, sigmas[0], phantom_n.shape)
    phantom_n = phantom_n * noise
    for i in range(n-1):
        idx = [int(round(compartments[i])), int(round(compartments[i+1]))]
        noise = np.random.normal(mean, sigmas[i], phantom_n[0, 94:100, idx[0]:idx[1]].shape)
        phantom_n[0, 94:100, idx[0]:idx[1]] = noise
    return phantom_n


def phantom_fractions(npx: int = 128, f_base: float = 10e-3, n_fractions: int = 10, f_range: tuple = (0, 10e-3)) \
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
    phantom_f = np.zeros([1, npx, npx])
    phantom_base = [[f_base, .6900, .920, 0., 0., 0.]]
    phantom_f[0, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_base)
    for i in range(n_fractions-1):
        phantom_f[0, 84:90, int(round(compartments[i])):int(round(compartments[i+1]))] = fractions[i]
    return phantom_f


def phantom_tissues(npx: int = 128, b0: float = 3, f_tissue: (str, None) = 'wm', noise_tissue: (str, None) = 'wm') -> np.array:
    """
    creates a phantom_examples for the stated tissue types (gm: gray matter, wm: white matter and csf: cerebrospinal fluid)
    with the according t1 and t2 values from tissue_library.py and optionally a range of pool-fraction-parameters for
    one of the tissue types (if f_matter = "gm", "wm" or "csf").
    :param  npx: int (pixel size of the phantom_examples, default = 128)
    :param  f_tissue: str (optional tissue type to create a fraction range, default = "wm", set to None for no
            fraction range in the phantom)
    :param noise_tissue: str (optional tissue type to create a noise range, default = "wm", set to None for no
            noise range in the phantom)
    :param b0: float (field strength in T, default = 3)
    :return phantom_t: np.array (size [2, npx, npx] with phantom_examples[0] containing T1 and phantom_examples[1]
    containing T2 values for each pixel
    """
    tissues = ["gm", "wm", "csf"]
    phantom_t = np.zeros([2, npx, npx])
    phantom_base = [[0., .6900, .920, 0., 0., 0.]]
    compartments = [[0, .6624, .874, 0., -.0184, 0.],
                    [0, .16, .41, -.22, -.2, 18],  # [0.5, .16, .41, -.22, -.2, 18],
                    [0, .12, .31, .22, -.12, -12]]  # [0.4, .11, .31, .22, -.12, -12]]
    for t in range(2):
        phantom_temp = phantom_base.copy()
        for i in range(len(tissues)):
            t_comp = compartments[i]
            if t == 0:
                t_comp[0] = get_t1(tissue=tissues[i], b0=0)
            elif t == 1:
                t_comp[0] = get_t2(tissue=tissues[i], b0=0)
            phantom_temp.append(t_comp)
        phantom_t[t, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_temp)
    # TODO wm t1
    if type(f_tissue) == str:
        phantom_t[0, 84:90, 44:84] = get_t1(tissue=f_tissue, b0=b0)
        phantom_t[1, 84:90, 44:84] = get_t2(tissue=f_tissue, b0=b0)
    if type(noise_tissue) == str:
        phantom_t[0, 94:100, 44:84] = get_t1(tissue=noise_tissue, b0=b0)
        phantom_t[1, 94:100, 44:84] = get_t2(tissue=noise_tissue, b0=b0)
    return phantom_t


def phantom_b1_inhom(npx: int = 128, min_inhom: float = -0.3, max_inhom: float = 0.3) -> np.array:
    """
    creating a phantom with radial B1 inhomogeneities
    :param npx: pixel size of the phantom
    :param min_inhom: minimal b1 inhomogeneity in percent (factor in range -1 and 1)
    :param max_inhom: maximal b1 inhomogeneity in percent (factor in range -1 and 1)
    :return phantom_b1: array of size (1, npx, npx) with values for relative B1 of range 1-min_inhom and 1+ max_inhom
    """
    phantom_b1 = np.zeros([1, npx, npx])
    phantom_base = [[1, .6900, .920, 0., 0., 0.]]
    phantom_b1[0, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_base)
    inhom_range = max_inhom - min_inhom
    x = y = np.linspace(-inhom_range, inhom_range, 128)
    xx, yy = np.meshgrid(x, y)
    r = np.sqrt(xx ** 2 + yy ** 2)
    b1_inhom = np.ones((128, 128)) * 0.3 - r
    phantom_b1[0, :, :] = phantom_b1[0, :, :] * b1_inhom + 1
    return phantom_b1


def phantom_b0_inhom(npx: int = 128, min_inhom: float = -0.3, max_inhom: float = 0.3) -> np.array:
    """
    creating a phantom with linear B0 field inhomogeneities
    :param npx: pixel size of the phantom
    :param min_inhom: minimal B0 shift in ppm
    :param max_inhom: maximal B0 shift in ppm
    :return phantom_b1: array of size (1, npx, npx) with values for B0-shift
    """
    phantom_b0 = np.zeros([1, npx, npx])
    phantom_base = [[1, .6900, .920, 0., 0., 0.]]
    phantom_b0[0, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_base)
    b0_inhom = np.linspace(min_inhom, max_inhom, npx*npx).reshape(npx, npx)
    phantom_b0[0, :, :] = phantom_b0[0, :, :] * b0_inhom
    return phantom_b0


def build_default_phantom(npx: int = 128, fractions: bool = True, noise: bool = False) -> np.array:
    """
    building a default phantom at 3T with parameters for a large GM ellipse, 2 WM ellipses, 1 CSF ellipse,
    optionally with a bar of WM parameters and continuously spaced fractions
    :param npx: pixel size of the phantom
    :param fractions: bool to define the fraction option (default: True)
    :param noise: bool to define the noise option (default: True)
    :return phantom: array of size (4, npx, npx) without or (5, npx, npx) with fractions containing the T1, T2,
    B0 inhomogeneities, B1 inhomogeneities and possibly fractions for each pixel respectively
    """
    phantom_t = phantom_tissues(npx)
    phantom_b0 = phantom_b0_inhom(npx)
    phantom_b1 = phantom_b1_inhom(npx)
    phantom = np.concatenate([phantom_t, phantom_b0, phantom_b1])
    if fractions:
        phantom_f = phantom_fractions(npx)
        phantom = np.concatenate([phantom, phantom_f])
    if noise:
        phantom_n = phantom_noise(npx)
        phantom = np.concatenate([phantom, phantom_n])
    return phantom


def build_phantom(phantom_t: np.array, phantom_b0: np.array, phantom_b1: np.array, phantom_f: np.array = None):
    """
    building a phantom from the individual parameter phantoms
    :param phantom_t: array of size (2, npx, npx) containing the T1 and T2 values of the pixels
    :param phantom_b0: array of size (1, npx, npx) containing the B0 shift values for each pixel
    :param phantom_b1: array of size (1, npx, npx) containing the relative B1 values for each pixel
    :param phantom_f: optional array of size (1, npx, npx) containing the fraction values for each pixel
    :return phantom: array of size (4, npx, npx) without or (5, npx, npx) with fractions containing the T1, T2,
    B0 inhomogeneities, B1 inhomogeneities and possibly fractions for each pixel respectively
    """
    phantom = np.concatenate([phantom_t, phantom_b0, phantom_b1])
    if phantom_f.any():
        return np.concatenate([phantom, phantom_f])
    # TODO noise
    else:
        return phantom


def load_data(filename):
    # open json data
    with open(filename) as json_file:
        data = json.load(json_file)
    data['offsets'] = np.array(data['offsets'])
    data['locs'] = [tuple(loc) for loc in data['sim_locs']]  # if undefined use code from function simulate_data
    data['phantom'] = np.array(data['phantom'])
    data['phantom_sim'] = np.array(data['phantom_sim'])
    return data


def simulate_data(phantom: np.array = None, seq_file: str = 'example/example_test.seq', b0: float = 3,
                  gamma: float = 267.5153, scale: float = 1, noise: bool = False, cest_pools=None,
                  test_mode: bool = False):
    # generate and plot phantom
    if not phantom:
        phantom = build_default_phantom()
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
        sp.set_scanner(b0=b0, gamma=gamma, b0_inhomogeneity=b0_inhom, rel_b1=rel_b1)
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
        temp = ax[p].imshow(phantom[p])
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

# # Phantom playground
# import matplotlib.pyplot as plt
#
# phantom_base = [[0., .6900, .920, 0., 0., 0.],
#                 [1, .6624, .874, 0., -.0184, 0.],
#                 [0.5, .16, .41, -.22, -.2, 18],  # [0.5, .16, .41, -.22, -.2, 18],
#                 [0.4, .12, .31, .22, -.12, -12]]  # [0.4, .11, .31, .22, -.12, -12]]
#
# p = phantom_ellipses(128, phantom_base)
# p[84:90, 44:84] = 0.2
# p[94:100, 44:84] = 0.1
#
#
# plt.figure()
# plt.imshow(p[0])
# plt.show()

