"""
calculate_phase.py
    Function to calculate phase modulation for a given frequency modulation.
"""

import numpy as np


def calculate_phase(frequency: np.ndarray,
                    duration: float,
                    samples: int,
                    shift_idx: int = -1,
                    pos_offsets: bool = False) \
        -> np.ndarray:
    """
    Calculates phase modulation for a given frequency modulation.
    :param frequency: frequency modulation of pulse
    :param duration: pulse duration [s]
    :param samples: number of sample points
    :param shift_idx: index of entry in frequency used to shift phase (default is last entry -> idx = -1)
    :param pos_offsets: flag needed to shift phase in [0 2pi] for offsets > 0
    :return:
    """
    phase = np.zeros_like(frequency)
    for i in range(1, samples):
        phase[i] = phase[i-1] + (frequency[i] * duration/samples)
    phase_shift = phase[shift_idx]
    for i in range(samples):
        phase[i] = np.fmod(phase[i]+1e-12 - phase_shift, 2 * np.pi)
    if not pos_offsets:
        phase += 2 * np.pi
    return phase
