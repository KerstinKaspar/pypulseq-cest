import numpy as np
import matplotlib.pyplot as plt
from parse_params import get_offsets, check_m0


def plot_without_offsets(mz: np.array, mtr_asym: bool = False):
    fig = plt.figure()
    plt.title('Z-spec')
    plt.ylabel('M')
    plt.xlabel('Offsets')
    plt.plot(offsets, mz, '.--')

    if check_m0:
        m0 = mz[0]
        z = mz[1:] / m0
    else:
        z = mz
    mtr_asym = z[::-1] - z

    fig = plt.figure()
    plt.plot(offsets, z, label='$Z$')
    plt.gca().invert_xaxis()
    plt.plot(offsets, mtr_asym, label='$MTR_{asym}$')
    plt.legend()
    plt.xlabel('Offset')
    return fig


def plot_with_offsets(mz: np.array, offsets: np.array, mtr_asym: bool = False):
    pass


def plot_z(mz: np.array, offsets: np.array = None, seq_file: str = None, mtr_asym: bool = False):
    from_seq = False
    if not offsets:
        if seq_file:
            offsets = get_offsets(seq_file)
            from_seq = True
        else:
            plot_without_offsets(mz, mtr_asym)
    if len(mz) != len(offsets) and not from_seq:
        offsets = get_offsets(seq_file)
        from_seq = True
    if len(mz) != len(offsets):
        plot_without_offsets(mz, mtr_asym)
    else:
        plot_with_offsets(mz, offsets, mtr_asym)







