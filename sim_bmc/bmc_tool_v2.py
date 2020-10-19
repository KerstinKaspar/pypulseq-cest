import numpy as np
import math

from sim.params import Params
from pypulseq.Sequence.sequence import Sequence
from pypulseq.Sequence.read_seq import __strip_line as strip_line


class BlochMcConnellSolver:
    def __init__(self, params: Params, n_offsets: int, par_calc: bool = False):
        self.params = params
        self.n_offsets = n_offsets
        self.par_calc = par_calc
        self.first_dim = 1
        self.n_pools = len(params.cest_pools)
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

        # always expand to 3 dimensions (independent of sequential or parallel computation)
        self.A = self.A[np.newaxis, ]

        # if parallel computation is activated, repeat matrix A n_offsets times along a new axis
        if self.par_calc:
            self.A = np.repeat(self.A, self.n_offsets, axis=0)
            self.first_dim = self.n_offsets

    def _init_vector_c(self):
        n_p = self.n_pools
        self.C = np.zeros([self.size], dtype=float)
        self.C[(n_p + 1) * 2] = self.params.water_pool['f'] * self.params.water_pool['r1']
        for i, pool in enumerate(self.params.cest_pools):
            self.C[(n_p + 1) * 2 + (i + 1)] = pool['f'] * pool['r1']

        if self.is_mt_active:
            self.C[3 * (n_p + 1)] = self.params.mt_pool['f'] * self.params.mt_pool['r1']

        # always expand to 3 dimensions (independent of sequential or parallel computation)
        self.C = self.C[np.newaxis, :, np.newaxis]

        # if parallel computation is activated, repeat matrix C n_offsets times along axis 0
        if self.par_calc:
            self.C = np.repeat(self.C, self.n_offsets, axis=0)

    def update_matrix(self, rf_amp: float, rf_phase: np.ndarray, rf_freq: np.ndarray):
        j = self.first_dim  # size of first dimension (=1 for sequential, n_offsets for parallel)
        n_p = self.n_pools

        # set dw0 due to b0_inhomogeneity
        self.A[:, 0, 1 + n_p] = [-self.dw0] * j
        self.A[:, 1 + n_p, 0] = [self.dw0] * j

        # calculate omega_1
        rf_amp_2pi = rf_amp * 2 * np.pi * self.params.scanner['rel_b1']
        rf_amp_2pi_sin = rf_amp_2pi * np.sin(rf_phase)
        rf_amp_2pi_cos = rf_amp_2pi * np.cos(rf_phase)

        # set omega_1 for water_pool
        self.A[:, 0, 2 * (n_p + 1)] = -rf_amp_2pi_sin
        self.A[:, 2 * (n_p + 1), 0] = rf_amp_2pi_sin

        self.A[:, n_p + 1, 2 * (n_p + 1)] = rf_amp_2pi_cos
        self.A[:, 2 * (n_p + 1), n_p + 1] = -rf_amp_2pi_cos

        # set omega_1 for cest pools
        for i in range(1, n_p + 1):
            self.A[:, i, i + 2 * (n_p + 1)] = -rf_amp_2pi_sin
            self.A[:, i + 2 * (n_p + 1), i] = rf_amp_2pi_sin

            self.A[:, n_p + 1 + i, i + 2 * (n_p + 1)] = rf_amp_2pi_cos
            self.A[:, i + 2 * (n_p + 1), n_p + 1 + i] = -rf_amp_2pi_cos

        # set off-resonance terms for water pool
        rf_freq_2pi = rf_freq * 2 * np.pi
        self.A[:, 0, 1 + n_p] -= rf_freq_2pi
        self.A[:, 1 + n_p, 0] += rf_freq_2pi

        # set off-resonance terms for cest pools
        for i in range(1, n_p + 1):
            dwi = self.params.cest_pools[i - 1]['dw'] * self.w0 - (rf_freq_2pi + self.dw0)
            self.A[:, i, i + n_p + 1] = dwi
            self.A[:, i + n_p + 1, i] = -dwi

        # mt_pool
        if self.is_mt_active and not self.par_calc:
            self.A[3 * (n_p + 1), 3 * (n_p + 1)] = (-self.params.mt_pool['r1'] - self.params.mt_pool['k'] -
                                                    rf_amp_2pi ** 2 * self.get_mt_shape_at_offset(
                        rf_freq_2pi + self.dw0, self.w0))
        else:
            # TODO: implement for parallel computation
            pass

    def solve_equation_pade(self, mag: np.ndarray, dtp: float):

        A = np.squeeze(self.A)
        C = np.squeeze(self.C)
        mag_ = np.squeeze(mag)

        q = 6  # number of iterations

        a_inv_t = np.dot(np.linalg.pinv(A), C)
        a_t = np.dot(A, dtp)

        _, inf_exp = math.frexp(np.linalg.norm(a_t, ord=np.inf))
        j = max(0, inf_exp)
        a_t = a_t * (1/pow(2, j))

        x = a_t.copy()
        c = 0.5

        n = np.identity(A.shape[0])

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
        return mag_[np.newaxis, :, np.newaxis]

    def solve_equation_old(self, mag: np.ndarray, dtp: float):
        """Solve the BMC equation system for all offsets in parallel using the matrix representation."""
        A = self.A
        C = self.C
        M = mag

        if not A.ndim == C.ndim == M.ndim:
            raise Exception("Matrix dimensions don't match. That's not gonna work.")

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
        return M

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
        sqrt_2pi = np.sqrt(2 / np.pi)
        for i in range(n_samples):
            powcu2 = abs(3 * pow(step_size * i, 2) - 1)
            mt_line += sqrt_2pi * t2 / powcu2 * np.exp(-2 * pow(dw * t2 / powcu2, 2))
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
    def __init__(self, params: Params, seq_filename: str):
        self.params = params
        self.seq_filename = seq_filename
        self.par_calc = False
        self.run_m0_scan = None
        self.offsets_ppm = None
        self.bm_solver = None

        self.seq = Sequence()
        self.seq.read(seq_filename)

        self.n_offsets = self.seq.definitions['offsets_ppm'].size
        self.n_total_offsets = self.n_offsets
        if self.seq.definitions['run_m0_scan'][0] == 'True':
            self.n_total_offsets += 1

        self.Mi = params.m_vec.copy()
        self.Mout = np.zeros([self.Mi.shape[0], self.n_total_offsets])

    def prep_rf_simulation(self, block):
        max_pulse_samples = self.params.options['max_pulse_samples']
        amp = np.real(block.rf.signal)
        ph = np.imag(block.rf.signal)
        rf_length = amp.size
        dtp = 1e-6

        idx = np.argwhere(amp > 1E-6)
        amp = amp[idx]
        ph = ph[idx]
        delay_after_pulse = (rf_length - idx.size) * dtp
        n_unique = max(np.unique(amp).size, np.unique(ph).size)
        if n_unique == 1:
            amp_ = amp[0]
            ph_ = ph[0]
            dtp_ = dtp * amp.size
        elif n_unique > max_pulse_samples:
            sample_factor = int(np.ceil(amp.size / max_pulse_samples))
            amp_ = amp[::sample_factor]
            ph_ = ph[::sample_factor]
            dtp_ = dtp * sample_factor
        else:
            raise Exception('Case with 1 < unique samples < max_pulse_samples not implemented yet. Sorry :(')

        return amp_, ph_, dtp_, delay_after_pulse

    def run(self, par_calc=False):
        self.par_calc = par_calc
        self.bm_solver = BlochMcConnellSolver(params=self.params, n_offsets=self.n_offsets, par_calc=self.par_calc)
        if par_calc:
            self.run_parallel()
        else:
            self.run_sequential()

    def run_parallel(self):
        self.par_calc = True
        if not self.params.options['reset_init_mag']:
            raise Exception("Parallel computation not possible for 'reset_init_mag = True'.\n"
                            "Please switch 'reset_init_mag' option or change to sequential computation.")

        seq_file = open(self.seq_filename, 'r')
        event_table = dict()
        while True:
            line = strip_line(seq_file)
            if line == -1:
                break

            elif line.startswith('offsets_ppm'):
                line = line[len('offsets_ppm'):]  # remove the prefix
                self.offsets_ppm = np.fromstring(line, dtype=float, sep=' ')  # convert remaining str to numpy array

            elif line.startswith('run_m0_scan'):
                line = line[len('run_m0_scan')+1:]  # remove the prefix
                self.run_m0_scan = True if line == 'True' else False

            elif line == '[BLOCKS]':
                adc_count = 0
                line = strip_line(seq_file)
                while line != '' and line != ' ' and line != '#':
                    block_events = np.fromstring(line, dtype=int, sep=' ')
                    if block_events[6]:
                        adc_count += 1
                    event_table[block_events[0]] = block_events[1:]
                    line = strip_line(seq_file)
            else:
                pass

        # get total number of event blocks excluding m0 events
        n_total = len(self.seq.block_events)
        idx_start = 0
        if self.run_m0_scan:
            # TODO: get number of events including 1st ADC instead of hard coding the number
            n_total -= 2  # subtract m0 events (delay and ADC) if run_m0_scan is True
            idx_start += 2

        # get number of blocks per offsets
        n_ = n_total/self.n_offsets
        if not n_.is_integer():
            raise Exception('Calculated number of blocks per offset is not an integer. Aborting parallel computation.')
        else:
            n_ = int(n_)

        # get dict with all events for the 1st offset. This will be applied (with adjusted rf freq) to all offsets).
        event_table_single_offset = {k: event_table[k] for k in list(event_table)[idx_start:idx_start+n_]}

        # extract the offsets in rad from rf library
        events_hz = [self.seq.rf_library.data[k][4] for k in list(self.seq.rf_library.data)]
        events_ph = [self.seq.rf_library.data[k][5] for k in list(self.seq.rf_library.data)]

        # check if 0 ppm is in the events. Because it only appears once (independent of number of pulses per saturation
        # train), the entry/event has to be inserted until it matches the number of pulses at the other offsets.
        if 0.0 in events_hz:
            n_rf_per_offset = (len(events_hz)-1)/(self.n_offsets-1)
            if n_rf_per_offset.is_integer():
                n_rf_per_offset = int(n_rf_per_offset)
            else:
                raise Exception('Unexpected number of block events. The current scenario is probably not suitable for '
                                'the parallel computation in the current form')

            idx_zero = events_hz.index(0.0)
            events_hz[idx_zero:idx_zero] = [0.0] * (n_rf_per_offset-1)
            events_ph[idx_zero:idx_zero] = [events_hz[idx_zero]] * (n_rf_per_offset-1)

        else:
            n_rf_per_offset = len(events_hz)/self.n_offsets
            if n_rf_per_offset.is_integer():
                n_rf_per_offset = int(n_rf_per_offset)
            else:
                raise Exception('Unexpected number of block events. The current scenario is probably not suitable for '
                                'the parallel computation in the current form')

        offsets_hz = np.unique(events_hz)
        if len(offsets_hz) != len(self.offsets_ppm):
            raise Exception(f"Number of offsets from seq-file definitions ({len(self.offsets_ppm)}) don't match the "
                            f"number of unique offsets ({len(offsets_hz)}) extracted from seq-file rf library.")

        # reshape phase events
        ph_offset = np.array(events_ph).reshape(self.n_offsets, n_rf_per_offset)

        # reshape magnetization vector
        M_ = np.repeat(self.Mi[np.newaxis, :, np.newaxis], self.n_offsets, axis=0)

        # handle m0 scan separately
        if self.run_m0_scan:
            m0 = M_.copy()
            m0_block = self.seq.get_block(1)  # TODO: read index from events instead of hard coding it
            if hasattr(m0_block, 'delay') and hasattr(m0_block.delay, 'delay'):
                m0_delay = float(m0_block.delay.delay)
                self.bm_solver.update_matrix(rf_amp=0.0,
                                             rf_phase=np.zeros(self.n_offsets),
                                             rf_freq=np.zeros(self.n_offsets))
                m0 = self.bm_solver.solve_equation(mag=m0, dtp=m0_delay)

        # perform parallel computation
        rf_count = 0
        accumm_phase = np.zeros(self.n_offsets)
        for x in event_table_single_offset:
            block = self.seq.get_block(x)

            if hasattr(block, 'adc'):
                Mout = np.swapaxes(np.squeeze(M_), 0, 1)
                if self.run_m0_scan:
                    Mout = np.concatenate((m0[0], Mout), axis=1)
                self.Mout = Mout

            elif hasattr(m0_block, 'delay') and hasattr(m0_block.delay, 'delay'):
                dtp_ = float(block.delay.delay)
                self.bm_solver.update_matrix(rf_amp=0.0,
                                             rf_phase=np.zeros(self.n_offsets),
                                             rf_freq=np.zeros(self.n_offsets))
                M_ = self.bm_solver.solve_equation(mag=M_, dtp=dtp_)

            elif hasattr(block, 'rf'):
                amp_, ph_, dtp_, delay_after_pulse = self.prep_rf_simulation(block)
                for i in range(amp_.size):
                    ph_i = ph_[i] + ph_offset[:, rf_count] - accumm_phase
                    self.bm_solver.update_matrix(rf_amp=amp_[i],
                                                 rf_phase=ph_i,
                                                 rf_freq=np.array(offsets_hz))
                    M_ = self.bm_solver.solve_equation(mag=M_, dtp=dtp_)

                if delay_after_pulse > 0:
                    self.bm_solver.update_matrix(rf_amp=0.0,
                                                 rf_phase=np.zeros(self.n_offsets),
                                                 rf_freq=np.zeros(self.n_offsets))
                    M_ = self.bm_solver.solve_equation(mag=M_, dtp=delay_after_pulse)

                phase_degree = dtp_*amp_.size * 360 * np.array(offsets_hz)
                phase_degree = np.mod(phase_degree, np.ones_like(phase_degree)*360)  # this is x % 360 for an array
                accumm_phase = accumm_phase + (phase_degree / 180 * np.pi)
                rf_count += 1

            elif hasattr(block, 'gx') and hasattr(block, 'gy') and hasattr(block, 'gz'):
                M_[:, 0:(len(self.params.cest_pools)+1)*2] = 0.0  # assume complete spoiling
            else:
                pass

    def run_sequential(self):
        current_adc = 0
        accumm_phase = 0
        M_ = self.Mi[np.newaxis, :, np.newaxis]
        for n_sample in range(1, len(self.seq.block_events)+1):
            block = self.seq.get_block(n_sample)
            if hasattr(block, 'adc'):
                print(f'Simulating block {n_sample} / {len(self.seq.block_events) + 1} (ADC)')
                self.Mout[:, current_adc] = np.squeeze(M_)  # write current mag in output array
                accumm_phase = 0
                current_adc += 1
                if current_adc <= self.n_offsets and self.params.options['reset_init_mag']:
                    M_ = self.Mi[np.newaxis, :, np.newaxis]

            elif hasattr(block, 'gx') and hasattr(block, 'gy') and hasattr(block, 'gz'):
                print(f'Simulating block {n_sample} / {len(self.seq.block_events) + 1} (SPOILER)')
                for j in range((len(self.params.cest_pools) + 1) * 2):
                    M_[0, j, 0] = 0.0  # assume complete spoiling

            elif hasattr(block, 'rf'):
                print(f'Simulating block {n_sample} / {len(self.seq.block_events) + 1} (RF PULSE)')
                amp_, ph_, dtp_, delay_after_pulse = self.prep_rf_simulation(block)
                for i in range(amp_.size):
                    self.bm_solver.update_matrix(rf_amp=amp_[i],
                                                 rf_phase=ph_[i] + block.rf.phase_offset - accumm_phase,
                                                 rf_freq=block.rf.freq_offset)
                    M_ = self.bm_solver.solve_equation(mag=M_, dtp=dtp_)

                if delay_after_pulse > 0:
                    self.bm_solver.update_matrix(0, 0, 0)
                    M_ = self.bm_solver.solve_equation(mag=M_, dtp=delay_after_pulse)

                phase_degree = dtp_ * amp_.size * 360 * block.rf.freq_offset
                phase_degree = phase_degree % 360
                accumm_phase += phase_degree / 180 * np.pi

            elif hasattr(block, 'delay') and hasattr(block.delay, 'delay'):
                print(f'Simulating block {n_sample} / {len(self.seq.block_events) + 1} (DELAY)')
                delay = float(block.delay.delay)
                self.bm_solver.update_matrix(0, 0, 0)
                M_ = self.bm_solver.solve_equation(mag=M_, dtp=delay)

            else:  # single gradient -> simulated as delay
                pass
