"""
plot_phantom.py
    plotting functions for phantoms and simulations
"""
import numpy as np
import matplotlib.pyplot as plt
from sim_pulseq_sbb.params import Params
from phantom.phantom import get_locs, get_z


def plot_example(phantom: np.array, sp: Params): #, offsets: list, pool: int = 0):
    # TODO here where o, set M{i] into according ellipse per CEST pool
    n_pools = len(sp.cest_pools)
    fig, ax = plt.subplots(figsize=(12, 9))
    tmp = ax.imshow(phantom)
    plt.title('Phantom:' + str(n_pools) + ' CEST-pools')
    plt.colorbar(tmp)
    plt.show()
    return fig


def plot_phantom(phantom):
    titles = ['T1', 'T2', 'B0 inhom.', 'B1 inhom.', 'fractions', 'noise']
    n_plots = phantom.shape[0]
    fig, ax = plt.subplots(1, n_plots)
    for p in range(len(ax)):
        temp = ax[p].imshow(phantom[p])
        ax[p].title.set_text('Phantom' + titles[p])
    plt.show()
    plt.savefig('example/test/fig.jpg')
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
        locs = all_locs[idx]
        labels = ['loc ' + str(l) for l in locs]

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
