"""
eval.py
    Tool independent functions for plotting and calculations
"""
import numpy as np
import matplotlib.pyplot as plt

from sim_pulseq_sbb.parse_params import get_offsets, check_m0


def plot_without_offsets(mz: np.array, mtr_asym: np.array = None, title: str = None) -> plt.subplots:
    """
    plots the magnetization without offsets
    :param mz: Magnetization
    :param mtr_asym: MTRasym as calculated in calc_mtr_asym
    :param title: optional title for the plot
    :return: matplotlib figure
    """
    fig, ax1 = plt.subplots()
    ax1.set_ylim([0, 1])
    ax1.set_ylabel('Z', color='b')
    ax1.set_xlabel('#')
    # plt.xlabel('Offsets')
    plt.plot(mz, '.--', label='$Z$', color='b')
    plt.gca().invert_xaxis()
    ax1.tick_params(axis='y', labelcolor='b')

    if mtr_asym.any():
        ax2 = ax1.twinx()
        ax2.set_ylim([0, round(np.max(mtr_asym) + 0.01, 2)])
        ax2.set_ylabel('$MTR_{asym}$', color='y')
        ax2.plot(mtr_asym, label='$MTR_{asym}$', color='y')
        ax2.tick_params(axis='y', labelcolor='y')
        fig.tight_layout()

    if title:
        title = title
    else:
        title = 'Z-spec'
    plt.title(title)
    plt.show()
    return fig


def plot_with_offsets(mz: np.array, offsets: np.array, mtr_asym: np.array = None, title: str = None) -> plt.subplots:
    """
    plots the magnetization with regard to the defined offsets
    :param mz: Magnetization
    :param offsets: offsets
    :param mtr_asym: MTRasym as calculated in calc_mtr_asym
    :param title: optional title for the plot
    :return: matplotlib figure
    """
    fig, ax1 = plt.subplots()
    ax1.set_ylim([0, 1])
    ax1.set_ylabel('Z', color='b')
    ax1.set_xlabel('Offsets')
    plt.plot(offsets, mz, '.--', label='$Z$', color='b')
    plt.gca().invert_xaxis()
    ax1.tick_params(axis='y', labelcolor='b')

    if mtr_asym.any():
        # TODO scale?
        ax2 = ax1.twinx()
        ax2.set_ylim([0, round(np.max(mtr_asym) + 0.01, 2)])
        ax2.set_ylabel('$MTR_{asym}$', color='y')
        ax2.plot(offsets, mtr_asym, label='$MTR_{asym}$', color='y')
        ax2.tick_params(axis='y', labelcolor='y')
        fig.tight_layout()
    if title:
        title = title
    else:
        title = 'Z-spec'
    plt.title(title)
    plt.show()
    return fig


def get_m0(mz, seq_file: str = None) -> float:
    """
    returns m0 from the magnetization vector
    :param mz: Magnetization
    :param seq_file: file to retrieve information from
    :return: M0
    """
    if seq_file:
        if check_m0(seq_file):
            return mz[0]
    elif mz[0] > 0.99:
        return mz[0]
    else:
        return None


def calc_mtr_asym(z: np.array) -> np.array:
    """
    calculating MTRasym from the magnetization vector
    :param z: magnetization
    :return: MTRasym
    """
    return np.flip(z) - z


def get_z(mz, seq_file):
    m0 = get_m0(mz, seq_file)
    if m0:
        z = mz[1:]/m0
    else:
        z = mz
    return z


def plot_z(mz: np.array, offsets: np.array = None, seq_file: str = None, plot_mtr_asym: bool = False, title: str = None):
    """
    initiating calculations and plotting functions
    :param mz: magnetization vector
    :param offsets: offsets to plot the magnetization on
    :param seq_file: sequence file to read offsets from
    :param plot_mtr_asym: boolean wether MTRasym should be plotted as well
    :param title: optional title for the plot
    """
    from_seq = False
    z = get_z(mz, seq_file)
    if plot_mtr_asym:
        mtr_asym = calc_mtr_asym(z)
    if not offsets:
        if seq_file:
            offsets = get_offsets(seq_file)
            from_seq = True
        else:
            plot_without_offsets(z, mtr_asym, title)
    if len(z) != len(offsets) and not from_seq:
        offsets = get_offsets(seq_file)
    if len(z) != len(offsets):
        plot_without_offsets(z, mtr_asym, title)
    else:
        plot_with_offsets(z, offsets, mtr_asym, title)







