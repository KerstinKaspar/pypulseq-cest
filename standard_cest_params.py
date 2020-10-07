"""
set_params.py
    Script to use standard CEST parameters for the simulation:
    Example for a Z-spectrum for gray matter at 3T with
        - 2 CEST pools
        - a Lorentzian shaped MT pool
CEST pools according to https://doi.org/10.1016/j.neuroimage.2017.04.045

If the simulation is started from simulate_sbb.py, this file does not need to be run separately, the setting of the
parameters into the class instance will be handled automatically.

PARAMETERS:
    b0: field strength [T]
    gamma: gyromagnetic ratio [rad / uT]
    b0_inhom: field inhomogeneity [ppm]
    rel_b1: relative b1
    f: proton fraction (relative)
    dw: chemical shift from water [ppm]
    k: exchange rate [Hz]
    lineshape_mt: lineshape of the MT Pool ('Lorentzian', 'SuperLorentzian' or 'None')
"""

from sim.params import Params

# instantiate class to store the parameters
sp = Params()

# path to seq-file
seq_file = 'example/example_APTw_m.seq'

# define scanner parameters
b0 = 3  # [T]
gamma = 267.5153  # [rad / uT]
# optional
b0_inhom = 0.0  # [ppm]
rel_b1 = 1
# set the scanner parameters
sp.set_scanner(b0=b0, gamma=gamma, b0_inhomogeneity=b0_inhom, rel_b1=rel_b1)

# define water properties according to the field strength
f_w = 1
try:
    if round(b0) < 4:
        r1_w = 1 / 1.3  # [Hz]
        r2_w = 1 / 75e-3  # [Hz]
    elif 4 < round(b0) < 9:  # 7T
        r1_w = 1 / 1.67  # [Hz]
        r2_w = 1 / 43e-3  # [Hz]
    elif round(b0) >= 9:  # 9.4 T and above
        r1_w = 1 / 2.0  # [Hz]
        r2_w = 1 / 35e-3  # [Hz]
except ValueError:
    print('B0 field strength of ' + str(b0) + 'T: No implementation possible.')
# set the water parameters
sp.set_water_pool(r1_w, r2_w, f_w)

# CEST pools
# pool 1: Amide
r1 = r1_w  # [Hz]
r2 = 1 / 100e-3  # [Hz]
k = 30  # exchange rate[Hz]
f = 72e-3 / 111  # rel
dw = 3.5  # [ppm]
# set CEST pool parameters
sp.set_cest_pool(r1=r1, r2=r2, k=k, f=f, dw=dw)

# pool 2: Creatine
r1 = r1_w  # [Hz]
r2 = 1 / 100e-3  # [Hz]
k = 1100  # [Hz]
f = 20e-3 / 111  # rel
dw = 2  # [ppm]
# set CEST pool parameters
sp.set_cest_pool(r1=r1, r2=r2, k=k, f=f, dw=dw)

# define MT pool
r1_mt = 1  # [Hz]
r2_mt = 1e5  # [Hz]
k_mt = 23  # [Hz]
f_mt = 0.0500  # rel
dw_mt = -2  # [ppm]
lineshape_mt = 'Lorentzian'
sp.set_mt_pool(r1=r1_mt, r2=r2_mt, k=k_mt, f=f_mt, dw=dw_mt, lineshape=lineshape_mt)

# Scale the M vector here according to FLASH)
scale = 0.5
# initiate the magnetization vector
sp.set_m_vec(scale)

# optional params
# verbose = True # for verbose output, default False
# sp.set_options(verbose=verbose)
# reset_init_mag = True # true if magnetization should be set to MEX.M after each ADC, default True
# sp.set_options(reset_init_mag=reset_init_mag)
max_pulse_samples = 300  # set the number of samples for the shaped pulses, default is 500
sp.set_options(max_pulse_samples=max_pulse_samples)
