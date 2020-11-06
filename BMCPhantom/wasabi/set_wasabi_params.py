"""
Setting the simulation parameters to wasabi after Schuenke et. al., 2017 (https://doi.org/10.1002/mrm.26133)
"""

from sim_pulseq_sbb.params import Params

# instantiate class to store the parameters
sp = Params()

# path to seq-file
seq_file = 'example/wasabi/example_wasabi.seq'

# define scanner parameters
b0 = 3  # [T]
gamma = 267.5153  # [rad / uT]
# optional
b0_inhom = 0.0  # [ppm]
rel_b1 = 1
# set the scanner parameters
sp.set_scanner(b0=b0, gamma=gamma, b0_inhom=b0_inhom, rel_b1=rel_b1)

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

# dummy pool
r1 = r1_w  # [Hz]
r2 = r2_w  # 1 / 100e-3  # [Hz]
k = 0  # exchange rate[Hz]
f = 1  # rel
dw = 0  # [ppm]
# set CEST pool parameters
sp.set_cest_pool(r1=r1, r2=r2, k=k, f=f, dw=dw)

# say you have a magnetization Mi of 50 after the readout. Scale the M vector here according to that (ca. 0.5 for FLASH)
scale = 1 # 0.5
# initiate the magnetization vector
sp.set_m_vec(scale)

# optional params
# verbose = True # for verbose output, default False
# sp.set_options(verbose=verbose)
# reset_init_mag = True # true if magnetization should be set to MEX.M after each ADC, default True
# sp.set_options(reset_init_mag=reset_init_mag)
max_pulse_samples = 300  # set the number of samples for the shaped pulses, default is 500
sp.set_options(max_pulse_samples=max_pulse_samples)