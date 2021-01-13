import numpy as np
from scipy.signal import hanning
from pypulseq.make_gauss_pulse import make_gauss_pulse


def make_hanning_pulse(flip_angle_sat, duration, system):
    sat_pulse, _, _ = make_gauss_pulse(flip_angle=flip_angle_sat, duration=duration, system=system)
    n_signal = np.sum(np.abs(sat_pulse.signal) > 0)
    hanning_shape = hanning(n_signal + 2)
    sat_pulse.signal[:n_signal] = hanning_shape[1:-1] / np.trapz(sat_pulse.t[:n_signal], hanning_shape[1:-1]) * \
                                  (flip_angle_sat / (2 * np.pi))
    return sat_pulse
