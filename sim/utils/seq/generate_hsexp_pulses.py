"""
generate_hsexp_pulses.py
    Function to create all possible HSExp pulses (tip-down/tip-up & pos/neg offset)
"""

import numpy as np
import matplotlib.pyplot as plt
from pypulseq.opts import Opts
from sim.utils.seq.make_arbitrary_rf_with_phase import make_arbitrary_rf_with_phase
from sim.utils.seq.make_hypsec_half_passage import calculate_hypsec_amplitude as hypsec_amp
from sim.utils.seq.calculate_phase import calculate_phase


def calculate_window_modulation(t: np.ndarray,
                                t0: float) \
        -> np.ndarray:
    """
    Calculates modulation function for HSExp pulses.
    :param t: time points of the different sample points [s]
    :param t0: reference time point (= last point for half passage pulse) [s]
    :return:
    """
    return 0.42 - 0.5 * np.cos(np.pi * t / t0) + 0.08 * np.cos(2 * np.pi * t / t0)


def calculate_hsexp_freq(t: np.ndarray,
                         t0: float,
                         bandwidth: float,
                         ef: float,
                         freq_factor: int) \
        -> np.ndarray:
    """
    Calculates modulation function for HSExp pulses.
    :param t: time points of the different sample points [s]
    :param t0: reference time point (= last point for half passage pulse) [s]
    :param bandwidth: bandwidth of the pulse [Hz]
    :param ef: dimensionless parameter to control steepness of the exponential curve
    :param freq_factor: factor (-1 or +1) to switch between positive and negative offsets
    :return:
    """

    return -freq_factor * bandwidth * np.pi * np.exp(-t / t0 * ef)


def generate_hsexp_pulses(amp: float = 1.0,
                          t_p: float = 12e-3,
                          mu: float = 65,
                          bandwidth: float = 2500,
                          t_window: float = 3.5e-3,
                          ef: float = 3.5,
                          system: Opts = Opts(),
                          gamma_hz: float = 42.5764) \
        -> dict:
    """
    Creates a radio-frequency pulse event with arbitrary pulse shape and phase modulation
    :param amp: maximum amplitude value [µT]
    :param t_p: pulse duration [s]
    :param mu: parameter µ of hyperbolic secant pulse
    :param bandwidth: bandwidth of hyperbolic secant pulse [Hz]
    :param t_window: duration of window function
    :param ef: dimensionless parameter to control steepness of the exponential curve
    :param system: system limits of the MR scanner
    :param gamma_hz: gyromagnetic ratio [Hz]
    :return:
    """

    pulse_dict = {}  # create empty dict for the 4 different pulses
    samples = int(t_p * 1e6)
    t_pulse = np.divide(np.arange(1, samples + 1), samples) * t_p  # time point array

    ############################
    # tip-down positive offset
    ############################
    t0 = t_pulse[-1]
    idx_window = np.argmin(np.abs(t_pulse-t_window))  # find start index for window

    # calculate amplitude of hyperbolic secant (HS) pulse
    w1 = hypsec_amp(t_pulse, t0, amp, mu, bandwidth)

    # calculate and apply modulation function to convert HS into HSExp pulse
    window_mod = calculate_window_modulation(t_pulse[:idx_window], t_pulse[idx_window])
    w1[:idx_window] = w1[:idx_window] * window_mod

    # calculate freq modulation of pulse
    dfreq = calculate_hsexp_freq(t_pulse, t0, bandwidth, ef, 1)

    # make freq modulation end (pre-pulse) or start (post-pulse) with dw = 0
    diff_idx = np.argmin(np.abs(dfreq))
    dfreq -= dfreq[diff_idx]

    # calculate phase (= integrate over dfreq)
    dphase = calculate_phase(dfreq, t_p, samples, shift_idx=-1, pos_offsets=True)

    # create pypulseq rf pulse object
    signal = w1 * np.exp(1j * dphase)  # create complex array with amp and phase
    flip_angle = gamma_hz * 2 * np.pi
    hsexp, _ = make_arbitrary_rf_with_phase(signal=signal, flip_angle=flip_angle, system=system)

    pulse_dict.update({'pre_pos': hsexp})

    ############################
    # tip-down negative offset
    ############################
    t0 = t_pulse[-1]
    idx_window = np.argmin(np.abs(t_pulse - t_window))  # find start index for window

    # calculate amplitude of hyperbolic secant (HS) pulse
    w1 = hypsec_amp(t_pulse, t0, amp, mu, bandwidth)

    # calculate and apply modulation function to convert HS into HSExp pulse
    window_mod = calculate_window_modulation(t_pulse[:idx_window], t_pulse[idx_window])
    w1[:idx_window] = w1[:idx_window] * window_mod

    # calculate freq modulation of pulse
    dfreq = calculate_hsexp_freq(t_pulse, t0, bandwidth, ef, -1)

    # make freq modulation end (pre-pulse) or start (post-pulse) with dw = 0
    diff_idx = np.argmin(np.abs(dfreq))
    dfreq -= dfreq[diff_idx]

    # calculate phase (= integrate over dfreq)
    dphase = calculate_phase(dfreq, t_p, samples, shift_idx=-1, pos_offsets=False)

    # create pypulseq rf pulse object
    signal = w1 * np.exp(1j * dphase)  # create complex array with amp and phase
    flip_angle = gamma_hz * 2 * np.pi
    hsexp, _ = make_arbitrary_rf_with_phase(signal=signal, flip_angle=flip_angle, system=system)

    pulse_dict.update({'pre_neg': hsexp})

    ############################
    # tip-up positive offset
    ############################
    t0 = 0
    idx_window = np.argmin(np.abs(t_pulse - t_window))  # find start index for window

    # calculate amplitude of hyperbolic secant (HS) pulse
    w1 = hypsec_amp(t_pulse, t0, amp, mu, bandwidth)

    # calculate and apply modulation function to convert HS into HSExp pulse
    window_mod = calculate_window_modulation(t_pulse[:idx_window], t_pulse[idx_window])
    w1[-idx_window:] = w1[-idx_window:] * np.flip(window_mod)

    # calculate freq modulation of pulse
    dfreq = calculate_hsexp_freq(np.flip(t_pulse), t_pulse[-1], bandwidth, ef, 1)

    # make freq modulation end (pre-pulse) or start (post-pulse) with dw = 0
    diff_idx = np.argmin(np.abs(dfreq))
    dfreq -= dfreq[diff_idx]

    # calculate phase (= integrate over dfreq)
    dphase = calculate_phase(dfreq, t_p, samples, shift_idx=0, pos_offsets=True)

    # create pypulseq rf pulse object
    signal = w1 * np.exp(1j * dphase)  # create complex array with amp and phase
    flip_angle = gamma_hz * 2 * np.pi
    hsexp, _ = make_arbitrary_rf_with_phase(signal=signal, flip_angle=flip_angle, system=system)

    pulse_dict.update({'post_pos': hsexp})

    ############################
    # tip-up negative offset
    ############################
    t0 = 0
    idx_window = np.argmin(np.abs(t_pulse - t_window))  # find start index for window

    # calculate amplitude of hyperbolic secant (HS) pulse
    w1 = hypsec_amp(t_pulse, t0, amp, mu, bandwidth)

    # calculate and apply modulation function to convert HS into HSExp pulse
    window_mod = calculate_window_modulation(t_pulse[:idx_window], t_pulse[idx_window])
    w1[-idx_window:] = w1[-idx_window:] * np.flip(window_mod)

    # calculate freq modulation of pulse
    dfreq = calculate_hsexp_freq(np.flip(t_pulse), t_pulse[-1], bandwidth, ef, -1)

    # make freq modulation end (pre-pulse) or start (post-pulse) with dw = 0
    diff_idx = np.argmin(np.abs(dfreq))
    dfreq -= dfreq[diff_idx]

    # calculate phase (= integrate over dfreq)
    dphase = calculate_phase(dfreq, t_p, samples, shift_idx=0, pos_offsets=False)

    # create pypulseq rf pulse object
    signal = w1 * np.exp(1j * dphase)  # create complex array with amp and phase
    flip_angle = gamma_hz * 2 * np.pi
    hsexp, _ = make_arbitrary_rf_with_phase(signal=signal, flip_angle=flip_angle, system=system)

    pulse_dict.update({'post_neg': hsexp})

    return pulse_dict


if __name__ == '__main__':
    pulse_dict = generate_hsexp_pulses()

    fig, ax = plt.subplots(2, 4)

    for n, key in enumerate(pulse_dict):
        real_ = np.real(pulse_dict[key].signal)
        imag_ = np.imag(pulse_dict[key].signal)
        ax[0, n].plot(np.abs(pulse_dict[key].signal))
        ax[0, n].set_title(key, fontsize=14)
        ax[1, n].plot(np.arctan2(imag_, real_))

    plt.show()
