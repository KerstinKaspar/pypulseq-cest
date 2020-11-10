"""
eval.py
    Tool independent functions for plotting and calculations
"""
import numpy as np

from sim_pulseq_sbb.params import Params
from sim_pulseq_sbb.util import sim_noise


def calc_mtr_asym(z: np.ndarray) \
        -> np.ndarray:
    """
    calculating MTRasym from the magnetization vector
    :param z: magnetization
    :return: MTRasym
    """
    return np.flip(z) - z


def get_zspec(m_out: np.ndarray,
              sp: Params,
              noise: (bool, tuple) = False) \
        -> np.ndarray:
    """
    returns the Z- spectra and optionally simulates noise
    :param m_out: Output magnetization from the simulation
    :param m0: bool, True if m_out contains m0 at the first position
    :param noise: bool or tuple, toggle to simulate standard gaussian noise on the spectra or set values (mean, std)
    """
    if np.any(m_out):
        if sp.m0_scan:
            zspec = np.abs(m_out[sp.mz_loc, 1:]/m_out[sp.mz_loc, 0])
        else:
            zspec = np.abs(m_out[sp.mz_loc, :])
        if noise:
            zspec = sim_noise(zspec, set_vals=noise)
        else:
            z_spec = zspec
    else:
        raise ValueError('No valid M0 defined.')
    return zspec









