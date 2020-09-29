"""
class definition to store simulation parameters
"""
import numpy as np


class Params:
    """
    Class to store simulation parameters
    Default parameters are for a Z-spectrum for gray matter at 3T
    with an amide CEST pool and a Lorentzian shaped MT pool
    """
    def __init__(self, set_defaults: bool = False):
        """
        :param set_defaults: if True, class initializes with parameters for a Z-spectrum for gray matter at 3T with an
        amide CEST pool and a Lorentzian shaped MT pool
        """
        self.water_pool = {}
        self.cest_pools = []
        self.mt_pool = {}
        self.m_vec = None
        self.scanner = None
        self.options = {}
        self._set_defaults(set_defaults)

    def set_mt_pool(self, r1: float = 1, r2: float = 1e5, k: int = 23, f: float = 0.05, dw: int = 0,
                    lineshape: str = 'SuperLorentzian') -> dict:
        """
        Defaults for a Super-Lorentzian MT pool
        :param r1: relaxation rate R1 = 1/ T1 [Hz]
        :param r2: relaxation rate R2 = 1/T2 [Hz]
        :param k: exchange rate [Hz]
        :param f: proton fraction
        :param dw: chemical shift from water [ppm]
        :param lineshape: shape of MT pool ("Lorentzian", "SuperLorentzian" or "None")
        :return:
        """
        mt_pool = {'r1': r1, 'r2': r2, 'k': k, 'f': f, 'dw': dw, 'lineshape': lineshape}
        self.mt_pool.update(mt_pool)
        return mt_pool

    def set_water_pool(self, r1: float = 1/1.31, r2: float = 1 / 71e-3, f: float = 1) -> dict:
        """
        Defaults for standard 3T water properties
        :param r1: relaxation rate R1 = 1/ T1 [Hz]
        :param r2: relaxation rate R2 = 1/T2 [Hz]
        :param f: proton fraction
        :return: dict of water pool parameters
        """
        water_pool = {'r1': r1, 'r2': r2, 'f': f}
        self.water_pool = water_pool
        return water_pool

    def set_cest_pool(self, r1: float = 1/1.31, r2: float = 1/ 100e-3, k: int = 30, f: float = 72e-3 / 111, dw: int = 3.5) -> dict:
        """
        TODO possibly implment other standard CEST parameters
        Defaults for amide CEST pool
        :param r1: relaxation rate R1 = 1/T1 [Hz]
        :param r2: relaxation rate R2 = 1/T2 [Hz]
        :param k: exchange rate [Hz]
        :param f: proton fraction
        :param dw: chemical shift from water [ppm]
        :return: dict of CEST pool parameters
        """
        cest_pool = {'r1': r1, 'r2': r2, 'k': k, 'f': f, 'dw': dw}
        self.cest_pools.append(cest_pool)
        return cest_pool

    def set_m_vec(self, scale: float = 0.5) -> np.array:
        """
        Sets the initial magnetization vector (fully relaxed) from the defined pools
        e. g. for 2 CEST pools: [MxA, MxB, MxD, MyA, MyB, MyD, MzA, MzB, MzD, MzC]
        with A: water pool, B: 1st CEST pool, D: 2nd CEST pool, C: MT pool
        with possible inclusion of more CEST pools in the same way
        :param scale: scales the initial vector according to the magnetization Mi after readout (e. g. 50% for FLASH)
        :return: array of the initial magnetizations
        """
        if not self.water_pool:
            raise Exception('No water pool defined before assignment of magnetization vector.')
        if self.cest_pools:
            n_total_pools = len(self.cest_pools) + 1
        else:
            n_total_pools = 1
        m_vec = np.zeros(n_total_pools * 3)
        m_vec[n_total_pools * 2] = self.water_pool['f']
        if self.cest_pools:
            for ii in range(1, n_total_pools):
                m_vec[n_total_pools * 2 + ii] = self.cest_pools[ii - 1]['f']
                m_vec[n_total_pools * 2] = m_vec[n_total_pools * 2] - self.cest_pools[ii - 1]['f']
        if self.mt_pool:
            m_vec = np.append(m_vec, self.mt_pool['f'])
        if scale:
            try:
                m_vec = m_vec * scale
            except Exception:
                print('Scaling of magnetization vector not possible with scale ', scale)
        self.m_vec = m_vec
        return m_vec

    def set_scanner(self, b0: float = 3, gamma: float = 267.5153, b0_inhomogeneity: float = None, rel_b1: float = 1.0) \
            -> dict:
        scanner = {'b0': b0, 'gamma': gamma, 'b0_inhomogeneity': b0_inhomogeneity, 'rel_b1': rel_b1}
        self.scanner = scanner
        return scanner

    def set_options(self, verbose: bool = None, reset_init_mag: bool = None, max_pulse_samples: int = None):
        options = {}
        if type(verbose) == bool:
            options.update({'verbose': verbose})
        if type(reset_init_mag) == bool:
            options.update({'reset_init_mag': reset_init_mag})
        if max_pulse_samples:
            options.update({'max_pulse_samples': max_pulse_samples})
        self.options.update(options)
        return options

    def print_settings(self):
        print("Current parameter settings:\n")
        print("\t water pool:\n", self.water_pool)
        print("\t CEST pools: \n", self.cest_pools)
        print("\t MT pool:\n", self.mt_pool)
        print("\t M:\n", self.m_vec)
        print("\t Scanner:\n", self.scanner)
        print("\t Options:\n", self.options)

    def _set_defaults(self, set_defaults):
        self.set_options(verbose=False, reset_init_mag=True, max_pulse_samples=100)
        if set_defaults:
            self.set_water_pool()
            self.set_mt_pool()
            self.set_cest_pool()
            self.set_m_vec()
            self.set_scanner()


# test main functionality
if __name__ == "__main__":
    params = Params(set_defaults=True)
    params.print_settings()




