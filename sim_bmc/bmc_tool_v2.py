import numpy as np
import math
import scipy
from types import SimpleNamespace
from sim.params import Params
from pypulseq.Sequence.sequence import Sequence


class BlochMcConnellSolver:
    def __init__(self, params: Params):
        self.params = params
        self.n_pools = len(params.cest_pools)
        #self.M = params.m_vec  # TODO: correct?!
        self.is_mt_active = bool(params.mt_pool)
        self.size = params.m_vec.size
        self.w0 = params.scanner['b0'] * params.scanner['gamma']
        self.dw0 = self.w0 * params.scanner['b0_inhomogeneity']

        self._init_matrix_a()
        self._init_vector_c()

    def _init_matrix_a(self):
        n_p = self.n_pools
        self.A = np.zeros([self.size, self.size], dtype=float)

        # set mt_pool parameters
        k_ac = 0.0
        if self.is_mt_active:
            k_ca = self.params.mt_pool['k']
            k_ac = k_ca * self.params.mt_pool['f']
            self.A[2 * (n_p + 1), 3 * (n_p + 1)] = k_ca
            self.A[3 * (n_p + 1), 2 * (n_p + 1)] = k_ac

        # set water_pool parameters
        k1a = self.params.water_pool['r1'] + k_ac
        k2a = self.params.water_pool['r2']
        for pool in self.params.cest_pools:
            k_ai = pool['f'] * pool['k']
            k1a += k_ai
            k2a += k_ai

        self.A[0, 0] = -k2a
        self.A[1 + n_p, 1 + n_p] = -k2a
        self.A[2 + 2 * n_p, 2 + 2 * n_p] = -k1a

        # set cest_pools parameters
        for i, pool in enumerate(self.params.cest_pools):
            k_ia = pool['k']
            k_ai = k_ia * pool['f']
            k_1i = k_ia + pool['r1']
            k_2i = k_ia + pool['r2']

            self.A[0, i + 1] = k_ia
            self.A[i + 1, 0] = k_ai
            self.A[i + 1, i + 1] = -k_2i

            self.A[1 + n_p, i + 2 + n_p] = k_ia
            self.A[i + 2 + n_p, 1 + n_p] = k_ai
            self.A[i + 2 + n_p, i + 2 + n_p] = -k_2i

            self.A[2 * (n_p + 1), i + 1 + 2 * (n_p + 1)] = k_ia
            self.A[i + 1 + 2 * (n_p + 1), 2 * (n_p + 1)] = k_ai
            self.A[i + 1 + 2 * (n_p + 1), i + 1 + 2 * (n_p + 1)] = -k_1i

    def _init_vector_c(self):
        n_p = self.n_pools
        self.C = np.zeros([self.size], dtype=float)
        self.C[(n_p + 1) * 2] = self.params.water_pool['f'] * self.params.water_pool['r1']
        for i, pool in enumerate(self.params.cest_pools):
            self.C[(n_p + 1) * 2 + (i + 1)] = pool['f'] * pool['r1']

        if self.is_mt_active:
            self.C[3 * (n_p + 1)] = self.params.mt_pool['f'] * self.params.mt_pool['r1']

    def update_matrix(self, rf_amp: float, rf_phase: float, rf_freq: float):
        n_p = self.n_pools

        # set dw0 due to b0_inhomogeneity
        self.A[0, 1 + n_p] = -self.dw0  # value checked (not position)
        self.A[1 + n_p, 0] = self.dw0  # value checked (not position)

        # set omega_1
        rf_amp_2pi = rf_amp * 2 * np.pi * self.params.scanner['rel_b1']
        rf_amp_2pi_sin = rf_amp_2pi * np.sin(rf_phase)
        rf_amp_2pi_cos = rf_amp_2pi * np.cos(rf_phase)

        # water_pool
        self.A[0, 2 * (n_p + 1)] = -rf_amp_2pi_sin  # -rf_amp_2pi_sin
        self.A[2 * (n_p + 1), 0] = rf_amp_2pi_sin  # rf_amp_2pi_sin

        self.A[n_p + 1, 2 * (n_p + 1)] = rf_amp_2pi_cos  # rf_amp_2pi_cos
        self.A[2 * (n_p + 1), n_p + 1] = -rf_amp_2pi_cos  # -rf_amp_2pi_cos

        # cest_pools
        for i in range(1, n_p+1):
            self.A[i, i + 2 * (n_p + 1)] = -rf_amp_2pi_sin  # -rf_amp_2pi_sin
            self.A[i + 2 * (n_p + 1), i] = rf_amp_2pi_sin  # rf_amp_2pi_sin

            self.A[n_p + 1 + i, i + 2 * (n_p + 1)] = rf_amp_2pi_cos  # rf_amp_2pi_cos
            self.A[i + 2 * (n_p + 1), n_p + 1 + i] = -rf_amp_2pi_cos  # -rf_amp_2pi_cos

        # set off-resonance terms
        # water_pool
        rf_freq_2pi = rf_freq * 2 * np.pi
        self.A[0, 1 + n_p] -= rf_freq_2pi  # value checked (not position)
        self.A[1 + n_p, 0] += rf_freq_2pi  # value checked (not position)

        # cest_pools
        for i in range(1, n_p+1):
            dwi = self.params.cest_pools[i - 1]['dw'] * self.w0 - (rf_freq_2pi + self.dw0)
            self.A[i, i + n_p + 1] = dwi  # value checked (not position)
            self.A[i + n_p + 1, i] = -dwi  # value checked (not position)

        # mt_pool
        if self.is_mt_active:
            self.A[3 * (n_p + 1), 3 * (n_p + 1)] = (-self.params.mt_pool['r1'] - self.params.mt_pool['k'] -
                                                    rf_amp_2pi**2 * self.get_mt_shape_at_offset(rf_freq_2pi + self.dw0, self.w0))

    def solve_equation_pade(self, mag: np.ndarray, dtp: float):
      
        q = 6

        mag_ = mag[:]

        a_inv_t = np.dot(np.linalg.pinv(self.A), self.C)
        a_t = np.dot(self.A, dtp)

        _, inf_exp = math.frexp(np.linalg.norm(a_t, ord=np.inf))
        j = max(0, inf_exp)
        a_t = a_t * (1/pow(2, j))

        x = a_t.copy()
        c = 0.5
        n = np.identity(a_t.shape[0])
        d = n - c * a_t
        n = n + c * a_t

        p = True

        for k in range(2, q+1):
            c = c * (q - k + 1) / (k * (2 * q - k + 1))
            x = np.dot(a_t, x)
            c_x = c * x
            n = n + c_x
            if p:
                d = d + c_x
            else:
                d = d - c_x
            p = not p

        f = np.dot(np.linalg.pinv(d), n)
        for k in range(1, j+1):
            f = np.dot(f, f)
        mag_ = np.dot(f, (mag_ + a_inv_t)) - a_inv_t
        return mag_

    def solve_equation_old(self, mag: np.ndarray, dtp: float):
        """Solve the BMC equation system for all offsets in parallel using the matrix representation."""
        _tmp = True
        if _tmp:  # TODO: implement parallel computation of all offsets
            A = self.A[np.newaxis, :, :]
            C = self.C[np.newaxis, :, np.newaxis]
            M = mag[np.newaxis, :, np.newaxis]
        else:
            n_offsets = 20
            A = np.repeat(self.A[np.newaxis, :, :], n_offsets, axis=0)

        # solve matrix exponential for current timestep
        ex = self._solve_expm(A, dtp)

        # because np.linalg.lstsq(A_,b_) doesn't work for stacked arrays, it is calculated as np.linalg.solve(
        # A_.T.dot(A_), A_.T.dot(b_)). For speed reasons, the transpose of A_ (A_.T) is pre-calculated and the
        # .dot notation is replaced by the Einstein summation (np.einsum).
        AT = A.T
        tmps = np.linalg.solve(np.einsum('kji,ikl->ijl', AT, A), np.einsum('kji,ikl->ijl', AT, C))

        # solve equation for magnetization M: np.einsum('ijk,ikl->ijl') is used to calculate the matrix
        # multiplication for each element along the first (=offset) axis.

        M = np.real(np.einsum('ijk,ikl->ijl', ex, M + tmps) - tmps)
        #self.M = np.squeeze(M)
        return np.squeeze(M)

    @staticmethod
    def _solve_expm(matrix: np.ndarray, dtp: float):
        """
        Solve the matrix exponential. This version is faster than scipy expm for typical BMC matrices.
        :rtype: np.ndarray
        """
        vals, vects = np.linalg.eig(matrix * dtp)
        tmp = np.einsum('ijk,ikl->ijl', vects, np.apply_along_axis(np.diag, -1, np.exp(vals)))
        inv = np.linalg.inv(vects)  # np.linalg.inv is about 10 times faster than np.linalg.pinv
        return np.einsum('ijk,ikl->ijl', tmp, inv)

    def get_mt_shape_at_offset(self, offset: float, w0: float):
        ls = self.params.mt_pool['lineshape'].lower()
        dw = self.params.mt_pool['dw']
        t2 = 1 / self.params.mt_pool['r2']
        if ls == 'lorentzian':
            mt_line = t2 / (1 + pow((offset - dw * w0) * t2, 2.0))
        elif ls == 'superlorentzian':
            # TODO not yet working!
            dw_pool = offset - self.dw0
            if abs(dw_pool) >= w0:
                mt_line = self.interpolate_sl(dw_pool)
            else:
                mt_line = self.interpolate_chs(dw_pool, w0)
        else:
            mt_line = 0
        return mt_line

    def interpolate_sl(self, dw_pool: float):
        """
        Interpolate Super Lorentzian Shape
        """
        mt_line = 0
        dw = self.params.mt_pool['dw']
        t2 = 1 / self.params.mt_pool['r2']
        n_samples = 101
        step_size = 0.01
        sqrt_2pi = np.sqrt(2/ np.pi)
        for i in range(n_samples):
            powcu2 = abs(3 * pow(step_size * i, 2) -1)
            mt_line += sqrt_2pi * t2 / powcu2 * np.exp(-2 * pow(dw * t2 /powcu2, 2))
        return mt_line * np.pi * step_size

    def interpolate_chs(self, dw_pool: float, w0: float):
        """
        Cubic Hermite Spline Interpolation
        """
        mt_line = 0
        px = np.array([-300 - w0, -100 - w0, 100 + w0, 300 + w0])
        py = np.zeros(px.size)
        for i in range(px.size):
            py[i] = self.interpolate_sl(px[i])
        if px.size != 4 or py.size != 4:
            return mt_line
        else:
            tan_weight = 30
            d0y = tan_weight * (py[0] - py[0])
            d1y = tan_weight * (py[3] - py[2])
            c_step = abs((dw_pool - px[1] + 1) / (px[2] - px[1] + 1))
            h0 = 2 * (c_step ** 3) - 3 * (c_step ** 2) + 1
            h1 = -2 * (c_step ** 3) + 3 * (c_step ** 2)
            h2 = (c_step ** 3) - 2 * (c_step ** 2) + c_step
            h3 = (c_step ** 3) - (c_step ** 2)

            mt_line = h0 * py[0] + h1 * py[2] + h2 * d0y + h3 * d1y
            return mt_line


class BMCTool:
    def __init__(self, params: Params, seq_filename: str, seq_readmode: str = 'pypulseq'):
        self.params = params
        self.seq_filename = seq_filename
        self.seq_readmode = seq_readmode
        self.current_adc = 0
        self.accumm_phase = 0

        self.seq = Sequence()
        self.seq.read(seq_filename)

        self.n_offsets = self.seq.definitions['offsets_ppm'].size
        if self.seq.definitions['run_m0_scan'][0] == 'True':
            self.n_offsets += 1

        self.Mi = params.m_vec.copy()
        self.Mout = np.zeros([self.Mi.shape[0], self.n_offsets])

        self.bm_solver = BlochMcConnellSolver(params=params)

    def run(self):
        M_ = self.Mi
        for n_sample in range(1, len(self.seq.block_events)+1):
            block = self.seq.get_block(n_sample)
            if hasattr(block, 'adc'):
                print(f'Simulating block {n_sample} / {len(self.seq.block_events) + 1} (ADC)')
                self.Mout[:, self.current_adc] = M_  # write current mag in output array
                self.current_adc += 1
                if self.current_adc <= self.n_offsets and self.params.options['reset_init_mag']:
                    M_ = self.Mi

            elif hasattr(block, 'gx') and hasattr(block, 'gy') and hasattr(block, 'gz'):
                print(f'Simulating block {n_sample} / {len(self.seq.block_events) + 1} (SPOILER)')
                for i in range((len(self.params.cest_pools) + 1) * 2):
                    M_[i] = 0.0  # assume complete spoiling

            elif hasattr(block, 'rf'):
                print(f'Simulating block {n_sample} / {len(self.seq.block_events) + 1} (RF PULSE)')
                max_pulse_samples = self.params.options['max_pulse_samples']
                amp = np.real(block.rf.signal)
                ph = np.imag(block.rf.signal)
                rf_length = amp.size
                dtp = 1e-6

                idx = np.argwhere(amp>1E-6)
                amp = amp[idx]
                ph = ph[idx]

                delay_after_pulse = (rf_length - idx.size) * dtp

                n_unique = max(np.unique(amp).size, np.unique(ph).size)

                if n_unique == 1:
                    amp_ = amp[0]
                    ph_ = ph[0]
                    self.bm_solver.update_matrix(rf_amp=amp_, rf_phase=ph_, rf_freq=block.rf.freq_offset)
                    M_ = self.bm_solver.solve_equation(mag=M_, dtp=dtp*amp.size)

                elif n_unique > max_pulse_samples:

                    sample_factor = int(np.ceil(amp.size/max_pulse_samples))
                    pulse_samples = int(amp.size/sample_factor)
                    amp2 = amp[::sample_factor]
                    ph2 = ph[::sample_factor]

                    for i in range(pulse_samples):
                        amp_i = amp2[i]
                        ph_i = ph2[i] + block.rf.phase_offset
                        self.bm_solver.update_matrix(rf_amp=amp_i,
                                                     rf_phase=ph_i-self.accumm_phase,
                                                     rf_freq=block.rf.freq_offset)
                        M_ = self.bm_solver.solve_equation(mag=M_, dtp=dtp*sample_factor)
                else:
                    pass

                if delay_after_pulse > 0:
                    self.bm_solver.update_matrix(0, 0, 0)
                    M_ = self.bm_solver.solve_equation(mag=M_, dtp=delay_after_pulse)

                phase_degree = rf_length * dtp * 360 * block.rf.freq_offset
                phase_degree = phase_degree % 360
                self.accumm_phase += phase_degree/180*np.pi

            elif hasattr(block, 'delay'):
                print(f'Simulating block {n_sample} / {len(self.seq.block_events) + 1} (DELAY)')
                delay = float(block.delay.delay)
                self.bm_solver.update_matrix(0, 0, 0)
                M_ = self.bm_solver.solve_equation(mag=M_, dtp=delay)

            else:  # single gradient -> simulated as delay
                pass
