"""
function fedinitions to pars the parameters into the C++ class
"""
import numpy as np
from pathlib import Path
from typing import Union
from setuptools import setup
from pySimPulseqSBB import SimulationParameters, WaterPool, MTPool, CESTPool
from pySimPulseqSBB import Lorentzian, SuperLorentzian, NoLineshape
from bmctool.params import Params
from bmctool.utils.seq.auxiliary import get_offsets, get_num_adc_events


def get_zspec(m_out: np.ndarray,
              sp: Params,
              offsets: np.ndarray = None,
              seq_file: Union[str, Path] = None,
              normalize_if_m0: bool = False,
              m0_offset_min: float = 190,
              return_abs: bool = False) \
        -> [np.ndarray, np.ndarray]:
    """
    returns the offsets and Z- spectra and optionally simulates noise
    :param m_out: Output magnetization from the simulation
    :param sp: Params object containing the simulation parameters
    :param offsets: array of offsets, if not given, offsets are retrieved from seq_file
    :param return_abs: Toggle to return np.abs(mz)
    :param normalize_if_m0: normalize the spectrum (Msat/M0) if an offset larger than m0_offset_min is found
    :param m0_offset_min: Offset minimum [ppm] to look for the M0 scan in the offsets
    :param seq_file: seq_file to get the offsets from. If not given and no offsets given, an array of ints in the range of len(mz) is returned as offsets
    :return: offsets and Z-spectra as np.ndarrays of the same size
    """
    offsets = np.array(offsets)
    if not offsets and not seq_file:
        offsets = np.array([])
    elif not offsets:
        offsets = get_offsets(seq_file=seq_file)
    if normalize_if_m0:
        if offsets[np.abs(offsets) >= m0_offset_min].any():
            m0 = m_out[sp.mz_loc, np.where(np.abs(offsets) >= m0_offset_min)[0]]
            m_ = m_out[sp.mz_loc, np.where(np.abs(offsets) < m0_offset_min)[0]]
            if m0.size > 1:
                mz = m_ / np.mean(m0)
            else:
                mz = m_ / m0
            offsets = offsets[np.abs(offsets) < m0_offset_min]
    else:
        mz = m_out[sp.mz_loc, :]

    if offsets.size != mz.size:
        offsets = np.arange(0, mz.size)

    if return_abs:
        mz = np.abs(mz)
    else:
        mz = np.array(mz)

    return offsets, mz


def parse_params(sp: Params,
                 seq_file: Union[str, Path]) -> SimulationParameters:
    """
    parsing python parameters into the according C++ functions
    :param sp: simulation parameter object
    :param seq_file: location of the seq-file to simulate
    :return: SWIG object for C++ object handling
    """
    sp_sim = SimulationParameters()
    # init magnetization vector
    sp_sim.InitMagnetizationVectors(sp.m_vec, get_num_adc_events(seq_file=seq_file))
    # constructwater pool
    water_pool = WaterPool(sp.water_pool['r1'], sp.water_pool['r2'], sp.water_pool['f'])
    sp_sim.SetWaterPool(water_pool)
    if sp.mt_pool:
        lineshape = set_lineshape(sp.mt_pool['lineshape'])
        mt_pool = MTPool(sp.mt_pool['r1'], sp.mt_pool['r2'], sp.mt_pool['f'], sp.mt_pool['dw'], sp.mt_pool['k'], lineshape)
        sp_sim.SetMTPool(mt_pool)
    sp_sim.InitCESTPoolMemory(len(sp.cest_pools))
    for i in range(len(sp.cest_pools)):
        cest_pool = CESTPool(sp.cest_pools[i]['r1'], sp.cest_pools[i]['r2'], sp.cest_pools[i]['f'], sp.cest_pools[i]['dw'], sp.cest_pools[i]['k'])
        sp_sim.SetCESTPool(cest_pool, i)
    sp_sim.InitScanner(sp.scanner['b0'], sp.scanner['rel_b1'], sp.scanner['b0_inhomogeneity'], sp.scanner['gamma'])
    if 'verbose' in sp.options.keys():
        sp_sim.SetVerbose(sp.options['verbose'])
    if 'reset_init_mag' in sp.options.keys():
        sp_sim.SetUseInitMagnetization(sp.options['reset_init_mag'])
    if 'max_pulse_samples' in sp.options.keys():
        sp_sim.SetMaxNumberOfPulseSamples(sp.options['max_pulse_samples'])
    return sp_sim


def set_lineshape(ls: str = None) -> (Lorentzian, SuperLorentzian, NoLineshape):
    """
    return the according lineshape object
    """
    try:
        if ls == 'Lorentzian':
            return Lorentzian
        elif ls == 'SuperLorentzian':
            return SuperLorentzian
        elif not ls:
            return NoLineshape
    except ValueError:
        print(ls + ' is not a valid lineshape for MT Pool.')
