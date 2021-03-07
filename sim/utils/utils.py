"""
utils.py
    Useful additional functions
"""
import numpy as np
from pathlib import Path
from typing import Union
from bmctool.utils.seq.read import read_any_version
from bmctool.params import Params
from pypulseq.Sequence.sequence import Sequence


def get_noise_params(mean: float = None,
                     std: float = None):
    """
    function to define standard noise parameters of mean=0 and std=0.005 for the missing parameters
    :param mean: the mean value of the gaussian function or None
    :param std: the standard deviation of the gaussian function or None
    :return (mean, std): previously defined values or the standard values
    """
    if not mean:
        mean = 0
    if not std:
        mean = 0.005
    return mean, std


def sim_noise(data: Union[float, np.ndarray, dict],
              mean: float = 0,
              std: float = 0.005,
              set_vals: Union[bool, tuple] = True):
    """
    simulating gaussian noise onto data
    :param data: the desired data to simulate noise on
    :param mean: the mean value of the gaussian function
    :param std: the standard deviation of the gaussian function
    :param set_vals: tuple to set (mean, std) or bool to set standard noise params of mean=0 and std=0.005
    :return output: data with added noise
    """
    if type(set_vals) is tuple:
        mean = set_vals[0]
        std = set_vals[1]
    elif set_vals:
        mean, std = get_noise_params(mean, std)
    ret_float = False
    if type(data) is dict:
        output = {}
        output.update({k: sim_noise(data=v, mean=mean, std=std) for k, v in data.items()})
    elif type(data) is list:
        output = [sim_noise(v) for v in data]
    else:
        if type(data) is float:
            data = np.array(data)
            ret_float = True
        elif type(data) is np.ndarray:
            data = data
        else:
            raise ValueError('Can only simulate noise on floats, arrays or lists/ dicts containing floats or arrays')
        noise = np.random.normal(mean, std, data.shape)
        output = data + noise
    if ret_float:
        output = float(output)
    return output


def get_offsets(seq: Sequence = None,
                seq_file: str = None) \
        -> list:
    """
    read the offsets either from the sequence file or from the Sequence object
    :param seq_file: sequence file to read the offsets from
    :param seq: Sequence object to get the offsets from
    :return: list of offsets
    """
    if not seq and not seq_file:
        raise ValueError('You need to pass either the sequence filename or the Sequence object to get offsets.')
    if not seq:
        seq = read_any_version(seq_file=seq_file)
    offsets = seq.definitions['offsets_ppm']
    return offsets


def get_num_adc_events(seq: Sequence = None,
                       seq_file: str = None) \
        -> int:
    """
    Reads number of ADC events (should equal number of offsets)
    :param seq: Sequence object to get the offsets from
    :param seq_file: sequence file to read the offsets from
    :return: num_adc_events
    """
    if not seq and not seq_file:
        raise ValueError('You need to pass either the sequence filename or the Sequence object to get offsets for the '
                         'ADC events.')
    offsets = get_offsets(seq_file=seq_file)
    num_adc_events = len(offsets)
    return num_adc_events


def get_zspec(m_out: np.ndarray,
              sp: Params,
              offsets: np.ndarray = None,
              seq_file: Union[str, Path] = None,
              return_abs: bool = False,
              noise: Union[bool, tuple] = False) \
        -> [np.ndarray, np.ndarray]:
    """
    returns the offsets and Z- spectra and optionally simulates noise
    :param m_out: Output magnetization from the simulation
    :param sp: Params object containing the simulation parameters
    :param offsets: array of offsets, if not given, offsets are retrieved from seq_file
    :param return_abs: Toggle to return np.abs(mz)
    :param seq_file: seq_file to get the offsets from. If not given and no offsets given, an array of ints in the range of len(mz) is returned as offsets
    :param noise: bool or tuple, toggle to simulate standard gaussian noise on the spectra or set values (mean, std)
    :return: offsets and Z-spectra as np.ndarrays of the same size
    """
    offsets = np.array(offsets)
    if not offsets and not seq_file:
        offsets = np.array([])
    elif not offsets:
        offsets = get_offsets(seq_file=seq_file)

    if offsets[np.abs(offsets) > 190].any():
        m0 = m_out[sp.mz_loc, np.where(np.abs(offsets) > 190)[0]]
        m_ = m_out[sp.mz_loc, np.where(np.abs(offsets) <= 190)[0]]
        mz = m_ / m0
        offsets = offsets[np.abs(offsets) <= 190]
    else:
        mz = m_out[sp.mz_loc, :]

    if offsets.size != mz.size:
        offsets = np.arange(0, mz.size)

    if noise:
        mz = sim_noise(mz, set_vals=noise)

    if return_abs:
        mz = np.abs(mz)
    else:
        mz = np.array(mz)

    return offsets, mz

