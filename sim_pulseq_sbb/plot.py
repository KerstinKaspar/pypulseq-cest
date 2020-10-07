"""TODO"""
import numpy as np
import matplotlib.pyplot as plt

from sim_pulseq_sbb.parse_params import get_offsets, check_m0


def plot_without_offsets(mz: np.array, mtr_asym: np.array = None, title: str = None):
    """TODO"""
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


def plot_with_offsets(mz: np.array, offsets: np.array, mtr_asym: np.array = None, title: str = None):
    """TODO"""
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


def get_m0(mz, seq_file: str = None):
    """TODO"""
    if seq_file:
        if check_m0(seq_file):
            return mz[0]
    elif mz[0] > 0.99:
        return mz[0]
    else:
        return None


def plot_z(mz: np.array, offsets: np.array = None, seq_file: str = None, plot_mtr_asym: bool = False, title: str = None):
    """TODO"""
    from_seq = False
    m0 = get_m0(mz, seq_file)
    if m0:
        z = mz[1:]/m0
    else:
        z = mz
    if plot_mtr_asym:
        mtr_asym = np.flip(z) - z
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







