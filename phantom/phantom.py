"""
pahntom.py
    simulate and plot a phantom for CEST magnetization

TODO implement different ellipses for different pools
"""

import numpy as np
import matplotlib.pyplot as plt
from sim.params import Params
from sim.eval import calc_mtr_asym, get_z


def set_phantom(npx: int, ellipses: np.array = None):
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

        phantom[i, :, :] = set_phantom(npx=npx, ellipses=e)

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

        phantom[i, :, :] = set_phantom(npx=npx, ellipses=e)
    return phantom


def plot_phantom(phantom: np.array, sp: Params): #, offsets: list, pool: int = 0):
    # TODO here where o, set M{i] into according ellipse per CEST pool
    n_pools = len(sp.cest_pools)
    fig, ax = plt.subplots(figsize=(12, 9))
    tmp = ax.imshow(phantom)
    plt.title('Phantom:' + str(n_pools) + ' CEST-pools')
    plt.show()
    return fig


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
    # phantom = np.zeros([n_pools, npx, npx])
    o = np.array(offsets)
    # initiate empty phantom
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

    phantom = set_phantom(npx=npx, ellipses=phantom_base)
    return phantom

def phantom_tissues(mz_gm: np.array, sp_gm: Params, mz_wm: np.array, sp_wm: Params, mz_cf: np.array, sp_cf: Params,
                    offsets: list, npx: int = 256, seq_file: str = None, mtr_asym: bool = False):
    """
    function to create a phantom contrasting simulations fo gray matter (gm), white matter (wm) and cerebral fluid (cf)
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
    # initiate empty phantom
    phantom_base = [[1., .6900, .920, 0., 0., 0.],
                    [-.9, .6624, .874, 0., -.0184, 0.]]
                    # [-.2, .1100, .310, .22, 0., -18.],
                    # [-.2, .1600, .410, -.22, 0., 18.],
                    # [.1, .0460, .046, 0., .25, 9.]]
    compartments = [[-.2, .1100, .310, .22, 0., -18.],
                    [-.2, .1600, .410, -.22, 0., 18.],
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
        phantom[pool, :, :] = set_phantom(npx=npx, ellipses=phantom_base)
    return phantom

