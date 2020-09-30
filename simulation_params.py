from params import Params
# path to seq-file
seq_file = 'example/example_APTw_small.seq'
# scanner parameters
b0 = 3  # field strength [T]
gamma = 267.5153  # gyromagnetic ratio [rad / uT]
# optional
b0_inhom = 0.0
rel_b1 = 1.0

# # Water properties(standard 3 T)
f_w = 1  # proton fraction
try:
    if round(b0) < 4:
        r1_w = 1 / 1.31  # Hz
        r2_w = 1 / (71e-3)  # Hz
    elif 4 < round(b0) < 9:  # 7T
        r1_w = 1 / 1.67  # Hz
        r2_w = 1 / (43e-3)  # Hz
    elif round(b0) >= 9:  # 9.4 T and above
        r1_w = 1 / 2.0  # Hz
        r2_w = 1 / (35e-3)  # Hz
except ValueError:
    print('B0 field strength of ' + str(b0) + 'T: No implementation possible.')

# # CEST pools according to https: // doi.org / 10.1016 / j.neuroimage.2017.04.045,
# pool 1 Amide
r1_a = r1_w
r2_a = 1 / 100e-3
f_a = 72e-3 / 111  # fraction
dw_a = 3.5  # chemical shift from water [ppm]
k_a = 30  # exchange rate[Hz]

# pool 2 creatine
r1_c = r1_w
r2_c = 1 / 170e-3
f_c = 20e-3 / 111  # fraction
dw_c = 2  # chemical shift from water [ppm]
k_c = 1100  # exchange rate[Hz]

# pool 3 glutamate
#  r1_g =  sp.WaterPool.R1
#  r2_g = 1 / 200e-3
#  f_g = 20e-3 / 111  # fraction
#  dw_g = 3  # chemical shift from water [ppm]
#  k_g = 5500  # exchange rate[Hz]

# pool 4 NOE(until now, all 4 pools of the paper combined in one at - 3.5 ppm with 5 fold concentration, originally 5x 100 mM each at[-1.75 -2.25 -2.75 -3.25 -3.75] ppm
#  r1_n =  sp.WaterPool.R1
#  r2_n = 1 / 5e-3
#  f_n  = 500e-3 / 111  # fraction
#  dw_n = -3.5  # chemical shift from water[ppm]
#  k_n  = 16  # exchange rate[Hz]

# OPTIONAL MT pool
# r1_mt = 1
# r2_mt = 1e5
# k_mt = 23
# f_mt = 0.0500
# dw_mt = 0
# lineshape_mt = 'SuperLorentzian'

# say you have a magnetization Mi of 50 after the readout. Scale the M vector here according to that(ca. 0.5 for FLASH)
scale = 0.5

# optional params
# verbose = False # for verbose output, defalut false
# reset_init_mag = True # true if magnetization should be set to MEX.M after each ADC, defaultrue
# max_pulse_samples = 500 # max samples for shaped pulses

