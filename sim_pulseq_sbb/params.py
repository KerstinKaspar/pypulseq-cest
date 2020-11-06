"""
class definition to store simulation parameters
"""
import numpy as np
from sim_pulseq_sbb.util import sim_noise


class Params:
    """
    Class to store simulation parameters
    Default parameters are for a Z-spectrum for gray matter at 3T
    with an amide CEST pool and a Lorentzian shaped MT pool
    """
    def __init__(self, set_defaults: bool = False, config: dict = None):
        """
        :param set_defaults: if True, class initializes with parameters for a standard APT weightedCEST simulation of
        gray matter at 3T with an amide CEST pool, a creatine CEST pool and a Lorentzian shaped MT pool
        """
        self.water_pool = {}
        self.cest_pools = []
        self.mt_pool = {}
        self.m_vec = None
        self.scanner = None
        self.options = {}
        self._set_defaults(set_defaults)
        self.mz_loc = 0
        self.scale = 1
        self.zspec = None
        self.b1_nom = None
        self.config = config

    def set_water_pool(self, r1: float = None, r2: float= None, f: float = 1, set_gm_3t_default: bool = False) -> dict:
        """
        defining the water pool for simulation
        :param r1: relaxation rate R1 = 1/ T1 [Hz]
        :param r2: relaxation rate R2 = 1/T2 [Hz]
        :param f: proton fraction (default = 1)
        :param set_gm_3t_default: Sets R1 and R2 to standard 3T water properties
        :return: dict of water pool parameters
        """
        if not set_gm_3t_default and None in [r1, r2]:
            raise ValueError('Not enough parameters given for water pool definition.')
        elif set_gm_3t_default:
            r1 = 1/1.31
            r2 = 1 / 71e-3
            print('Setting a water pool for GM at 3T. No externally defined parameters considered.')
        water_pool = {'r1': r1, 'r2': r2, 'f': f}
        self.water_pool = water_pool
        self.mz_loc += 2
        return water_pool

    def set_cest_pool(self, r1: float = None, r2: float = None, k: int = None, f: float = None, dw: float = None,
                      set_amide_defaults: bool = False, set_creatine_defaults: bool = False) -> dict:
        """
        defines a CEST pool for simulation
        :param r1: relaxation rate R1 = 1/T1 [Hz]
        :param r2: relaxation rate R2 = 1/T2 [Hz]
        :param k: exchange rate [Hz]
        :param f: proton fraction
        :param dw: chemical shift from water [ppm]
        :param set_amide_defaults: sets an amide CEST pool
        :param set_creatine_defaults: sets an amide CEST pool
        :return: dict of CEST pool parameters
        """
        if not set_amide_defaults and not set_creatine_defaults and None in [r1, r2, k, f, dw]:
            raise ValueError('Not enough parameters given for CEST pool definition.')
        elif set_amide_defaults and set_creatine_defaults:
            raise ValueError('Can\'t define CEST pool for both Amide and Creatine default values. Set separately.')
        elif set_amide_defaults:
            r1 = self.water_pool['r1']
            r2 = 1 / 100e-3
            k = 30
            f = 72e-3 / 111
            dw = 3.5
            print('Setting an amide CEST pool. No externally defined parameters considered.')
        elif set_creatine_defaults:
            r1 = self.water_pool['r1']
            r2 = 1 / 100e-3
            k = 1100
            f = 20e-3 / 111
            dw = 2
            print('Setting an creatine CEST pool. No externally defined parameters considered.')
        cest_pool = {'r1': r1, 'r2': r2, 'k': k, 'f': f, 'dw': dw}
        self.cest_pools.append(cest_pool)
        self.mz_loc += 2
        return cest_pool

    def set_mt_pool(self, r1: float = 1, r2: float = 1e5, k: int = 23, f: float = 0.05, dw: int = 0,
                    lineshape: str = 'SuperLorentzian', set_lorentzian_default: bool = False) -> dict:
        """
        defines an MT pool for simulation
        :param r1: relaxation rate R1 = 1/ T1 [Hz]
        :param r2: relaxation rate R2 = 1/T2 [Hz]
        :param k: exchange rate [Hz]
        :param f: proton fraction
        :param dw: chemical shift from water [ppm]
        :param lineshape: shape of MT pool ("Lorentzian", "SuperLorentzian" or "None")
        :param set_lorentzian_default: sets defaults for a standard Lorentzian MT pool at dw = -2
        :return:
        """
        if not set_lorentzian_default and None in [r1, r2, k, f, dw, lineshape]:
            raise ValueError('Not enough parameters given for MT pool definition.')
        elif set_lorentzian_default:
            r1 = 1  # [Hz]
            r2 = 1e5  # [Hz]
            k = 23  # [Hz]
            f = 0.0500  # rel
            dw = -2  # [ppm]
            lineshape = 'Lorentzian'
            print('Setting a standard Lorentzian MT pool. No externally defined parameters considered.')
        mt_pool = {'r1': r1, 'r2': r2, 'k': k, 'f': f, 'dw': dw, 'lineshape': lineshape}
        self.mt_pool.update(mt_pool)
        # self.mz_loc += 2
        return mt_pool

    def set_m_vec(self, scale: float = 1, set_flash_default: bool = False) -> np.array:
        """
        Sets the initial magnetization vector (fully relaxed) from the defined pools
        e. g. for 2 CEST pools: [MxA, MxB, MxD, MyA, MyB, MyD, MzA, MzB, MzD, MzC]
        with A: water pool, B: 1st CEST pool, D: 2nd CEST pool, C: MT pool
        with possible inclusion of more CEST pools in the same way
        :param scale: scales the initial vector according to the magnetization Mi after readout
        :param set_flash_default: sets scale to 50% for FLASH
        :return: array of the initial magnetizations
        """
        if set_flash_default:
            scale = 0.5
            print('Setting magnetization scale to 50% (FLASH). No externally defined parameters considered.')
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
                m_vec[n_total_pools * 2] = m_vec[n_total_pools * 2] # - self.cest_pools[ii - 1]['f']
        if self.mt_pool:
            m_vec = np.append(m_vec, self.mt_pool['f'])
        if scale:
            try:
                m_vec = m_vec * scale
            except Exception:
                print('Scaling of magnetization vector not possible with scale ', scale)
        self.m_vec = m_vec
        self.scale = scale
        return m_vec

    def set_scanner(self, b0: float = 3, gamma: float = 267.5153, b0_inhom: float = None, rel_b1: float = 1.0) \
            -> dict:
        """
        Sets the scanner values
        :param b0: field strength [T]
        :param gamma: gyromagnetic ratio [rad/uT]
        :param b0_inhom: field ihnomogeneity [ppm]
        :param rel_b1: relative B1 field
        :return: dictionary containing the parameter values
        """
        scanner = {'b0': b0, 'gamma': gamma, 'b0_inhomogeneity': b0_inhom, 'rel_b1': rel_b1}
        self.scanner = scanner
        return scanner

    def set_options(self, **kwargs):
        """
        Setting additional options
        :param verbose: Verbose output, default False
        :param reset_init_mag: true if magnetization should be set to MEX.M after each ADC, default True
        :param max_pulse_samples: set the number of samples for the shaped pulses, default is 500
        :param par_calc: toggles parallel calculation for BMC Tool
        :return:
        """
        options = {k: v for k, v in kwargs.items()}
        self.options.update(options)
        return options

    def get_zspec(self, m_out: np.array = None, m0: bool = False, noise: (bool, tuple) = True):
        """
        returns the Z- spectra and optionally simulates noise
        :param m_out: Output magnetization from the simulation
        :param m0: bool, True if m_out contains m0 at the first position
        :param noise: bool or tuple, toggle to simulate standard gaussian noise on the spectra or set values (mean, std)
        """
        if not np.any(m_out) and not np.any(self.zspec):
            print("mz not yet retrieved from m_out. Use Params.get_mz(m_out).")
        elif np.any(m_out):
            if m0:
                zspec = np.abs(m_out[self.mz_loc, 1:]) # TODO *M0? Move into simulation!
            else:
                zspec = np.abs(m_out[self.mz_loc, :])
            if noise:
                self.zspec = sim_noise(zspec, set=noise)
            else:
                self.z_spec = zspec
        return self.zspec

    def print_settings(self):
        """
        function to print the current parameter settings
        """
        print("Current parameter settings:\n")
        print("\t water pool:\n", self.water_pool)
        print("\t CEST pools: \n", self.cest_pools)
        print("\t MT pool:\n", self.mt_pool)
        print("\t M:\n", self.m_vec)
        print("\t Scanner:\n", self.scanner)
        print("\t Options:\n", self.options)

    def _set_defaults(self, set_defaults):
        self.set_options(verbose=False, reset_init_mag=True, max_pulse_samples=500)
        if set_defaults:
            self.set_water_pool(set_gm_3t_default=True)
            self.set_mt_pool(set_lorentzian_default=True)
            self.set_cest_pool(set_amide_defaults=True)
            self.set_cest_pool(set_creatine_defaults=True)
            self.set_m_vec(set_flash_default=True)
            self.set_scanner()





