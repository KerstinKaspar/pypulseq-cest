import numpy as np
from scipy.signal import hanning
from pypulseq.make_gauss_pulse import make_gauss_pulse


def make_hanning_pulse(flip_angle_sat, duration, system):
    sat_pulse, _, _ = make_gauss_pulse(flip_angle=flip_angle_sat, duration=duration, system=system)
    hanning_shape = hanning(len(sat_pulse.signal))
    sat_pulse.signal = hanning_shape / np.trapz(sat_pulse.t, hanning_shape) * (flip_angle_sat / (2 * np.pi))
    return sat_pulse
