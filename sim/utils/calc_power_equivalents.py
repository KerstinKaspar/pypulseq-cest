"""
    calc_power_equivalents.py
"""

import numpy as np
from types import SimpleNamespace


def calc_power_equivalent(rf_pulse: SimpleNamespace, tp: float, td: float, gamma_hz: float = 42.5764) -> np.ndarray:
    """

    Parameters
    ----------
    rf_pulse
    tp
    td
    gamma_hz
    """
    amp = rf_pulse.signal/gamma_hz
    duty_cycle = tp / (tp + td)

    return np.sqrt(np.trapz(amp**2, rf_pulse.t) / tp * duty_cycle)  # continuous wave power equivalent


def calc_amplitude_equivalent(rf_pulse: SimpleNamespace, tp: float, td: float) -> np.ndarray:
    """

    Parameters
    ----------
    rf_pulse
    tp
    td
    """
    gamma_hz = 42.5764
    duty_cycle = tp / (tp + td)

    alpha_rad = np.trapz(rf_pulse.signal * gamma_hz * 360, rf_pulse.t) * np.pi / 180

    return alpha_rad / (gamma_hz * 2 * np.pi * tp) * duty_cycle  # continuous wave amplitude equivalent

