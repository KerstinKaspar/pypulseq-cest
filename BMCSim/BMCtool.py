import numpy as np
import PulseShapes


class BMCTool:
    def __init__(self, b0: float, n_pools: int, t1_values: np.ndarray, t2_values: np.ndarray, poolsizes: np.ndarray,
                 resonances: np.ndarray, exchange_rates: np.ndarray, track: bool = False):
        self.B0 = b0
        self.n_pools = n_pools
        self.T1 = t1_values
        self.T2 = t2_values
        self.f = poolsizes
        self.dw = resonances * 42.577 * 2 * np.pi * self.B0
        self.k = exchange_rates
        self.track = track 

        self.b0shift = 0
        self.b = np.zeros([1, 3*n_pools, 1], dtype=float)
        self.M = np.zeros([1, 3*n_pools, 1], dtype=float)
        self.M_ = np.array([])
        self.amp = np.array([])
        self.phase = np.array([])

        self._create_arrays()
        
    def _create_arrays(self):
        """Create all necessary arrays."""
        self._create_A()
        self._create_b()

    def _create_A(self):
        """Create relaxation matrix depending on the number of CEST pools."""
    
        self.A = np.zeros([3*self.n_pools, 3*self.n_pools], dtype=float)   
        for n in range(self.n_pools):
            # write parameters of pool n
            self.A[3*n+0, 3*n+0] = -(1/self.T2[n]+self.k[n])
            self.A[3*n+1, 3*n+1] = -(1/self.T2[n]+self.k[n])
            self.A[3*n+2, 3*n+2] = -(1/self.T1[n]+self.k[n])
            self.A[3*n+0, 3*n+1] = -self.dw[n]
            self.A[3*n+1, 3*n+0] = self.dw[n]
            
            if n > 0:
                # add the exchange rate A->n to the relaxation rate of pool A
                self.A[0, 0] -= self.k[n]*self.f[n]
                self.A[1, 1] -= self.k[n]*self.f[n]
                self.A[2, 2] -= self.k[n]*self.f[n]

                # add the exchange terms for A->n and n->A
                self.A[0, 3*n+0] = self.k[n]
                self.A[1, 3*n+1] = self.k[n]
                self.A[2, 3*n+2] = self.k[n]
                self.A[3*n+0, 0] = self.k[n]*self.f[n]
                self.A[3*n+1, 1] = self.k[n]*self.f[n]
                self.A[3*n+2, 2] = self.k[n]*self.f[n]
                
    def _create_b(self):
        """Create equilibrium vector."""
        for n in range(self.n_pools):
            self.b[:, 3*n+2] = 1/self.T1[n]*self.f[n]
            
    def _create_M(self):
        """Create magnetization vector."""
        for n in range(self.n_pools):
            self.M[:, 3*n+2] = self.f[n]

    def _flip_mag(self, case: str = 'down'):
        """Flip magnetization in SL scenario."""
        tmp = self.M_.copy()
        for dw in range(tmp.shape[0]):
            for n in range(self.n_pools):
                if case == 'down':
                    self.M_[dw, 3*n+0, 0] = tmp[dw, 3*n+2, 0]
                    self.M_[dw, 3*n+2, 0] = tmp[dw, 3*n+0, 0]
                elif case == 'up':
                    self.M_[dw, 3*n+0, 0] = tmp[dw, 3*n+2, 0]
                    self.M_[dw, 3*n+2, 0] = tmp[dw, 3*n+0, 0]

    def _get_pulse_shape(self, steps: int, shape: str):
        """"""
        if steps == 1:
            self.amp = np.asarray(1).reshape(1,)
            self.phase = np.asarray(0).reshape(1,)
            return

        if shape.upper() in ['BLOCK', 'CW', 'RECT', 'RECTANGLE', 'PAUSE', 'DELAY', 'SL', 'SPIN-LOCK']:
            self.amp, self.phase = PulseShapes.block(steps)
        elif shape.upper() in ['SIEMENS_GAUSS', 'GAUSS_SIEMENS']:
            self.amp, self.phase = PulseShapes.gauss_siemens(steps)
        else:
            raise NameError(f'Unknown shape "{shape}"! ')
        
    def _repeat_A(self, n_off: int):
        """Create an array with copies of the relaxation matrix (A) for every offset."""
        self.A_ = np.repeat(self.A[np.newaxis, :, :], n_off, axis=0)
        
    def _repeat_b(self, n_off: int):
        """Create an array with copies of the equilibrium vector (b) for every offset."""
        self.b_ = np.repeat(self.b, n_off, axis=0)
        
    def _repeat_M(self, n_off: int):
        """Create an array with copies of the magnetization vector (M) for every offset."""
        self.M_ = np.repeat(self.M, n_off, axis=0)
        
    def _set_offsets(self, offsets: np.ndarray):
        """Set the frequency shift of every pool to the resonance frequency minus the given offset."""
        self.offsets = offsets
        for n in range(self.n_pools):
            dw = 0 if n == 0 else self.dw[0]
            self.A_[:, 3*n+0, 3*n+1] = -(self.dw[n] + self.b0shift + dw - offsets)
            self.A_[:, 3*n+1, 3*n+0] = +(self.dw[n] + self.b0shift + dw - offsets)

    def _set_phase(self, phase: float):
        """Set the off-resonance due to phase-modulated pulses."""
        for n in range(self.n_pools):
            self.A_[:, 3*n+0, 3*n+1] -= phase
            self.A_[:, 3*n+1, 3*n+0] += phase

    def _set_rf_amp(self, b1: float):
        """Set the RF amplitude (more precise: the rf frequency 'omega_1') to the given value."""
        w1 = 42.577e6 * 2 * np.pi * b1
        for n in range(self.n_pools):
            self.A_[:, 3*n+2, 3*n+1] = np.repeat(-w1, self.offsets.size)
            self.A_[:, 3*n+1, 3*n+2] = np.repeat(w1, self.offsets.size)
        
    def _solve(self, b1: float, pulse_dur: float, n_timesteps: int):
        """Solve the BMC equation system for all offsets in parallel using the matrix representation."""
        dtp = pulse_dur/n_timesteps
        for t in np.arange(n_timesteps):
            self._set_rf_amp(self.amp[t] * b1)

            # solve matrix exponential for current timestep
            ex = self._solve_expm(self.A_, dtp)

            # because np.linalg.lstsq(A_,b_) doesn't work for stacked arrays, it is calculated as np.linalg.solve(
            # A_.T.dot(A_), A_.T.dot(b_)). For speed reasons, the transpose of A_ (A_.T) is pre-calculated and the
            # .dot notation is replaced by the Einstein summation (np.einsum).
            AT = self.A_.T
            tmps = np.linalg.solve(np.einsum('kji,ikl->ijl', AT, self.A_), np.einsum('kji,ikl->ijl', AT, self.b_))

            # solve equation for magnetization M: np.einsum('ijk,ikl->ijl') is used to calculate the matrix
            # multiplication for each element along the first (=offset) axis.
            self.M_ = np.real(np.einsum('ijk,ikl->ijl', ex, self.M_ + tmps) - tmps)

            if self.track:
                try:
                    self.t = np.append(self.t, self.t[-1]+dtp)
                except AttributeError:
                    self.t = np.array([0])

                try:
                    self.amp_ = np.append(self.amp_, self.amp[t] * b1)
                except AttributeError:
                    self.amp_ = np.array([self.amp[t] * b1])

                try:
                    self.Mt = np.concatenate((self.Mt, self.M_[np.newaxis, ]))
                except AttributeError:
                    self.Mt = self.M_[np.newaxis, ]
        
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
             
    def set_M(self, m: int, mag=np.array([])):
        """Create magnetization vector M or set given M vector as current magnetization."""
        if mag.size == 0:
            self._create_M()
            self._repeat_M(m)
        else:
            self.M_ = mag

    def set_b0shift(self, shift: float):
        """Set B0-shift to given value."""
        self.b0shift = shift * 42.577 * 2 * np.pi * self.B0

    def set_t1(self, t1: float):
        """Set T1 value of pool A to given value."""
        # remove old T1 entry of pool A from matrix A
        self.A[2, 2] -= -(1 / self.T1[0])

        # add new T1 entry of pool A from matrix A
        self.A[2, 2] += -(1 / t1)

        # set new value in b vector
        self.b[:, 2] = 1 / t1 * self.f[0]

        # set given T1 as new T1 value
        self.T1[0] = t1

    def solve(self, offsets_ppm: np.ndarray, b1: float, pulse_dur: float, steps: int, shape: str = 'CW'):
        """Create required arrays and set values to solve the BMC equations."""
        offsets = offsets_ppm * 42.577 * 2 * np.pi * self.B0
        self._repeat_A(offsets.size)
        self._repeat_b(offsets.size)
        self._set_offsets(offsets)
        if shape.upper() in ['SL', 'SPIN-LOCK']:
            self._flip_mag(case='down')
        self._get_pulse_shape(steps, shape)
        self._solve(b1, pulse_dur, steps)
        if shape.upper() in ['SL', 'SPIN-LOCK']:
            self._flip_mag(case='up')
