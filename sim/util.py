"""
sim.util.py
    useful additional functions for simulation
"""
import numpy as np


def sim_noise(sim: (float, np.array), is_zspec: bool = False, is_phantom: bool = False, mean: float = 0, std: float = 0.005):
    try:
        if not is_zspec and not is_phantom and type(sim) == float:
            sim += float(np.random.normal(mean, std))
            return sim
        elif is_zspec and sim.ndim == 1:
            noise = np.random.normal(mean, std, sim.shape)
            return sim + noise
        elif is_phantom and sim.ndim > 1:
            locator = np.zeros(sim.shape[1:])
            idces = list(np.ndindex(locator.shape))  # [128*60:128*62]
            for loc in idces:
                if sim[0][loc] != 0:
                    locator[loc] = 1
            noise = np.random.normal(mean, std, sim.shape) * locator
            return sim + noise
    except ValueError:
        print("You need to define an array and declare either is_zspec or is_phantom as True to simulate noise on "
              "anything other than a single float.")

