"""
pahntom.py
    simulate and plot a phantom_examples for CEST magnetization

TODO implement different ellipses for different pools
"""

import numpy as np
import matplotlib.pyplot as plt
from sim.params import Params
from sim.eval import calc_mtr_asym, get_z
from phantom.tissue_library import get_t1, get_t2


def phantom_ellipses(npx: int, ellipses: np.array = None):
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


def create_phantom(n_offsets: int, npx: int = 256) -> np.array:
    phantom = np.zeros([n_offsets, npx, npx])

    for i in range(n_offsets):
        e = [[1., .6900, .920, 0., 0., 0.],
             [-.9, .6624, .874, 0., -.0184, 0.],
             [-.2, .1100, .310, .22, 0., -18.],
             # [mvec[i], .1100, .310, .22, 0., -18.],
             [-.2, .1600, .410, -.22, 0., 18.],
             # [mvec[i], .1600, .410, -.22, 0., 18.],
             # [.1, .2100, .250, 0., -.3, 9.],
             # [.1, .0460, .046, 0., .25, 9.],
             [.1, .0460, .046, 0., .25, 9.]]
        # [mvec[i], .0460, .046, 0., .25, 9.]]
        # [.1,  .0460, .023,  -.08,  0.,   9.],
        # [.1,  .0230, .023,    0.,   0.,   9.],
        # [.1,  .0230, .046, .06,   0.,   9.]]

        phantom[i, :, :] = phantom_ellipses(npx=npx, ellipses=e)

    return phantom


def set_mag(phantom: np.array, n_offsets: int, mvec: np.array, npx: int = 256):
    for i in range(n_offsets):
        e = [[1., .6900, .920, 0., 0., 0.],
             [-.9, .6624, .874, 0., -.0184, 0.],
             [-.2, .1100, .310, .22, 0., -18.],
             [mvec[i], .1100, .310, .22, 0., -18.],
             [-.2, .1600, .410, -.22, 0., 18.],
             [mvec[i], .1600, .410, -.22, 0., 18.],
             # [.1, .2100, .250, 0., -.3, 9.],
             # [.1, .0460, .046, 0., .25, 9.],
             [.1, .0460, .046, 0., .25, 9.],
             [mvec[i], .0460, .046, 0., .25, 9.]]
        # [.1,  .0460, .023,  -.08,  0.,   9.],
        # [.1,  .0230, .023,    0.,   0.,   9.],
        # [.1,  .0230, .046, .06,   0.,   9.]]

        phantom[i, :, :] = phantom_ellipses(npx=npx, ellipses=e)
    return phantom



def phantom_compartments(mz: np.array, sp: Params, offsets: list, npx: int = 256, seq_file: str = None, mtr_asym: bool = False):
    if seq_file:
        z = get_z(mz=mz, seq_file=seq_file)
    else:
        z = mz
    if mtr_asym:
        mvec = calc_mtr_asym(z)
    else:
        mvec = z
    n_pools = len(sp.cest_pools)
    # phantom_examples = np.zeros([n_pools, npx, npx])
    o = np.array(offsets)
    # initiate empty phantom_examples
    phantom_base = [[1., .6900, .920, 0., 0., 0.],
                    [-.9, .6624, .874, 0., -.0184, 0.]]
    ellipses = [[-.2, .1100, .310, .22, 0., -18.],
                [-.2, .1600, .410, -.22, 0., 18.],
                [.1, .2100, .250, 0., -.3, 9.],
                [.1, .0460, .046, 0., .25, 9.]]
    # [.1,  .0460, .023,  -.08,  0.,   9.],
    # [.1,  .0230, .023,    0.,   0.,   9.],
    # [.1,  .0230, .046, .06,   0.,   9.]]
    idces = []
    for pool in range(n_pools):
        dw = sp.cest_pools[pool]['dw']
        idx = int(np.where(o == o[np.abs(o - dw).argmin()])[0])
        idces.append(idx)
        if pool == len(ellipses):
            print('Too many CEST pools (', n_pools, '). Only ', len(ellipses), ' pools supported.')
            break
        else:
            e = ellipses[pool]
            phantom_base.append(ellipses[pool])
            e[0] = mvec[idces[pool]]
            print(e)
            phantom_base.append(e)

    phantom = phantom_ellipses(npx=npx, ellipses=phantom_base)
    return phantom


def phantom_tissues_cest(mz_gm: np.array, sp_gm: Params, mz_wm: np.array, sp_wm: Params, mz_cf: np.array, sp_cf: Params,
                    offsets: list, npx: int = 256, seq_file: str = None, mtr_asym: bool = False):
    """
    function to create a phantom_examples contrasting simulations fo gray matter (gm), white matter (wm) and cerebral fluid (cf)
    """
    m_vecs = [mz_gm, mz_wm, mz_cf]
    if seq_file:
        m_vecs = [get_z(mz, seq_file) for mz in [mz_gm, mz_wm, mz_cf]]
    if mtr_asym:
        m_vecs = [calc_mtr_asym(z) for z in m_vecs]
    assert len(sp_gm.cest_pools) == len(sp_wm.cest_pools) == len(sp_cf.cest_pools)
    n_pools = len(sp_gm.cest_pools)
    phantom = np.zeros([n_pools, npx, npx])
    o = np.array(offsets)
    # initiate empty phantom_examples
    phantom_base = [[0.5, .6900, .920, 0., 0., 0.],
                    [0.5, .6624, .874, 0., 0, 0]]#-.0184, 0.]]
                    # [-.2, .1100, .310, .22, 0., -18.],
                    # [-.2, .1600, .410, -.22, 0., 18.],
                    # [.1, .0460, .046, 0., .25, 9.]]
    compartments = [[-.2, .1100, .310, .22, 0., -18.],
                    [-.2, .1600, .410, -.22, 0., -18.],
                    [.1, .0460, .046, 0., .25, 9.]]
    params = [sp_gm, sp_wm, sp_cf]
    for pool in range(n_pools):
        for tissue in range(len(params)):
            dw = params[tissue].cest_pools[pool]['dw']
            idx = int(np.where(o == o[np.abs(o - dw).argmin()])[0])
            c = compartments[tissue]
            c[0] = m_vecs[tissue][idx]
            print(c)
            phantom_base.append(c)
        print(phantom_base)
        phantom[pool, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_base)
    return phantom


def phantom_tissues(npx: int = 256, b0: float = 3, f_tissue: (str, None) = "wm"):
    """
    creates a phantom_examples for the stated tissue types (gm: gray matter, wm: white matter and csf: cerebrospinal fluid)
    with the according t1 and t2 values from tissue_library.py and optionally a range of pool-fraction-parameters for
    one of the tissue types (if f_matter = "gm", "wm" or "csf").
    :param  npx: int (pixel size of the phantom_examples, default = 256)
    :param  f_tissue: str (optional tissue type to create a fraction range from, default = "wm", set to None for no
            fraction range in the phantom_examples)
    :param b0: float (field strength in T, default = 3)
    :return phantom_examples: np.array (size [2, npx, npx] with phantom_examples[0] containing T1 and phantom_examples[1] containing T2 values
            for each pixel
    """
    tissues = ["gm", "wm", "wm", "csf"]
    phantom_t = np.zeros([2, npx, npx])
    phantom_base = [[0., .6900, .920, 0., 0., 0.]]
    compartments = [[0, .6624, .874, 0., -.0184, 0.],
                    [0, .18, .480, .25, -.2, -12.],
                    [0, .18, .480, -.25, -.2, 12.],
                    [0, .13, .2, 0., .15, 0]]
    # p = [[-1, .09, .120, .33, -.1, -12.],
    #      [-1, .09, .120, -.28, 0.08, 12.]]
    for t in range(2):
        phantom_temp = phantom_base.copy()
        for i in range(len(tissues)):
            t_comp = compartments[i]
            if t == 0:
                t_comp[0] = get_t1(tissue=tissues[i], b0=0)
                print(tissues[i], " T1: ", t_comp[0])
            elif t == 1:
                t_comp[0] = get_t2(tissue=tissues[i], b0=0)
                print(tissues[i], " T2: ", t_comp[0])
            phantom_temp.append(t_comp)
        # phantom_temp.append(p[0])
        # phantom_temp.append(p[1])
        phantom_t[t, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_temp)
    if f_tissue:
        phantom_t[0, 190:200, 78:178] = get_t1(tissue=f_tissue, b0=b0)
        print(f_tissue, " T1: ", phantom_t[0, 191, 79])
        phantom_t[1, 190:200, 78:178] = get_t2(tissue=f_tissue, b0=b0)
        print(f_tissue, " T2: ", phantom_t[1, 191, 79])
    return phantom_t


def phantom_fractions(npx: int = 256, f_base: float = 10e-3 ,n_fractions: int = 10, f_range: tuple = (0, 10e-3)):
    compartments = np.linspace(78, 178, n_fractions)
    fractions = np.linspace(f_range[0], f_range[1], n_fractions)
    phantom_f = np.zeros([1, npx, npx])
    phantom_base = [[f_base, .6900, .920, 0., 0., 0.]]
    phantom_f[0, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_base)
    for i in range(n_fractions-1):
        phantom_f[0, 190:200, int(round(compartments[i])):int(round(compartments[i+1]))] = fractions[i]
    return phantom_f


def phantom_b1_inhom(npx: int = 256, min_inhom: float = -0.3, max_inhom: float = 0.3, center: (tuple, None) = (0, 0)):
    phantom_b1 = np.zeros([1, npx, npx])
    phantom_base = [[1, .6900, .920, 0., 0., 0.]]
    phantom_b1[0, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_base)
    inhom_range = max_inhom - min_inhom
    x = y = np.linspace(-inhom_range, inhom_range, 256)
    # y = np.linspace(0, max_inhom - min_inhom, 256)
    xx, yy = np.meshgrid(x, y)
    r = np.sqrt(xx ** 2 + yy ** 2)
    b1_inhom = np.ones((256, 256)) * 0.3 - r
    phantom_b1[0, :, :] = phantom_b1[0, :, :] * b1_inhom
    return phantom_b1


def phantom_b0_inhom(npx: int = 256, min_inhom: float = -0.3, max_inhom: float = 0.3, center: (tuple, None) = (0, 0)):
    phantom_b0 = np.zeros([1, npx, npx])
    phantom_base = [[1, .6900, .920, 0., 0., 0.]]
    phantom_b0[0, :, :] = phantom_ellipses(npx=npx, ellipses=phantom_base)
    b0_inhom = np.linspace(min_inhom, max_inhom, npx*npx).reshape(npx, npx)
    phantom_b0[0, :, :] = phantom_b0[0, :, :] * b0_inhom
    return phantom_b0


def build_default_phantom(npx: int = 256, fractions: bool = True):
    phantom_t = phantom_tissues(npx)
    phantom_b0 = phantom_b0_inhom(npx)
    phantom_b1 = phantom_b1_inhom(npx)
    phantom = np.concatenate([phantom_t, phantom_b0, phantom_b1])
    if fractions:
        phantom_f = phantom_fractions(npx)
        return np.concatenate([phantom, phantom_f])
    else:
        return phantom


def build_phantom(phantom_t: np.array, phantom_b0: np.array, phantom_b1: np.array, phantom_f: np.array = None):
    phantom = np.concatenate([phantom_t, phantom_b0, phantom_b1])
    if phantom_f.any():
        return np.concatenate([phantom, phantom_f])
    else:
        return phantom