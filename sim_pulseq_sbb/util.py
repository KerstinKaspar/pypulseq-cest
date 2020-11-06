"""
sim.util.py
    useful additional functions for simulation
"""
import numpy as np


def get_noise_params(mean: float = None, std: float = None):
    if not mean:
        mean = 0
    if not std:
        mean = 0.005
    return mean, std


def sim_noise(data: (float, np.ndarray, dict), mean: float = 0, std: float = 0.005, set: (bool, tuple) = True):
        if type(set) is tuple:
            mean = set[0]
            std = set[1]
        elif not mean or not std:
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
        else:
            return output


# def sim_phantom_noise():
    # elif is_phantom and sim.ndim > 1:
    #     locator = np.zeros(sim.shape[1:])
    #     idces = list(np.ndindex(locator.shape))  # [128*60:128*62]
    #     for loc in idces:
    #         if sim[0][loc] != 0:
    #             locator[loc] = 1
    #     noise = np.random.normal(mean, std, sim.shape) * locator
    #     return sim + noise

