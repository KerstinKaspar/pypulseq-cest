"""
class definition to store simulation parameters
"""
import numpy as np

class Params:
    def __init__(self):
        self.water_pool = {}
        self.cest_pools = []
        self.mt_pool = {}
        self.m_vec = None

    def set_mt_pool(self, r1: float = None, r2: float = None, k: int = None, f: float = None, dw: int = None, lineshape: str = None):
        mt_pool = {'r1': r1, 'r2': r2, 'k': k, 'f': f, 'dw': dw, 'lineshape': lineshape}
        self.mt_pool.update(mt_pool)
        return mt_pool

    def set_water_pool(self, r1: float = None, r2: float = None, f: float = None):
        water_pool = {'r1': r1, 'r2': r2, 'f': f}
        self.water_pool = water_pool
        return water_pool

    def set_cest_pool(self, r1: float = None, r2: float = None, k: int = None, f: float = None, dw: int = None):
        cest_pool = {'r1': r1, 'r2': r2, 'k': k, 'f': f, 'dw': dw, 'lineshape': lineshape}
        self.cest_pools.append(cest_pool)
        return cest_pool

    def set_m_vec(self, scale: float = 0.5):
        if not self.cest_pools:
            raise Exception('No cest pool defined before assignment of magnetization vector.')
        if not self.water_pool:
            raise Exception('No water pool defined before assignment of magnetization vector.')
        n_total_pools = len(self.cest_pools) + 1
        m_vec = np.zeros(n_total_pools * 3, 1)
        m_vec[n_total_pools * 2 + 1, 1] = self.water_pool['f']
        for ii in range(2, n_total_pools):
            m_vec[n_total_pools * 2 + ii, 1] = self.cest_pools[ii-1]['f']
            m_vec[n_total_pools * 2 + 1, 1] = m_vec[n_total_pools * 2 + 1, 1] - self.cest_pools[ii-1]['f']
        # TODO
        # if self.mt_pool:
            # m_vec.append(self.mt_pool['f'])

        self.m_vec = m_vec
        return m_vec




