"""
plot_phantom.py
    plotting functions for phantoms and simulations
"""
import numpy as np
import matplotlib.pyplot as plt
from sim.params import Params


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
    titles = ['T1', 'T2', 'B0 inhom.', 'B1 inhom.', 'fractions']
    n_plots = phantom.shape[0]
    fig, ax = plt.subplots(1, n_plots)
    for p in range(len(ax)):
        temp = ax[p].imshow(phantom[p])
        ax[p].title.set_text('Phantom' + titles[p])
    plt.show()
    plt.savefig('example/test/phantom_examples.jpg')
    return fig


def plot_simulated(phantom_sim):
    pass
