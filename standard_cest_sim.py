"""
function to run a standard CEST simulation
"""

from SimPulseqSBB import SimPulseqSBB
from parse_params import parse_sp, get_offsets
from params import Params

from plot import plot_z


def run_standard_cest_sim():
    # path to seq-file
    seq_file = 'example/example_APTw_m.seq'
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
            r1_w = 1 / 1.3  # Hz 1.31
            r2_w = 1 / (75e-3)  # Hz 71e-3
        elif 4 < round(b0) < 9:  # 7T
            r1_w = 1 / 1.67  # Hz
            r2_w = 1 / (43e-3)  # Hz
        elif round(b0) >= 9:  # 9.4 T and above
            r1_w = 1 / 2.0  # Hz
            r2_w = 1 / (35e-3)  # Hz
    except ValueError:
        print('B0 field strength of ' + str(b0) + 'T: No implementation possible.')

    # CEST pools according to https: // doi.org / 10.1016 / j.neuroimage.2017.04.045,
    # pool 1 Amide
    r1_a = r1_w
    r2_a = 1 / 100e-3
    f_a = 72e-3 / 111  # fraction
    dw_a = 3.5  # chemical shift from water [ppm]
    k_a = 30  # exchange rate[Hz]

    # # pool 2 creatine
    r1_c = r1_w
    r2_c = 1 / 100e-3# 1 / 170e-3
    f_c = 20e-3 / 111  # fraction
    dw_c = 2  # chemical shift from water [ppm]
    k_c = 1100  # exchange rate[Hz]

    # #pool 3 glutamate
    # r1_g = r1_w
    # r2_g = 1 / 200e-3
    # f_g = 20e-3 / 111  # fraction
    # dw_g = 3  # chemical shift from water [ppm]
    # k_g = 5500  # exchange rate[Hz]
    #
    # #pool 4 NOE(until now, all 4 pools of the paper combined in one at - 3.5 ppm with 5 fold concentration, originally 5x 100 mM each at[-1.75 -2.25 -2.75 -3.25 -3.75] ppm
    # r1_n = r1_w
    # r2_n = 1 / 5e-3
    # f_n = 500e-3 / 111  # fraction
    # dw_n = -3.5  # chemical shift from water[ppm]
    # k_n = 16  # exchange rate[Hz]

    # OPTIONAL MT pool
    r1_mt = 1
    r2_mt = 1e5
    k_mt = 23
    f_mt = 0.0500
    dw_mt = -2
    lineshape_mt = 'Lorentzian'

    # say you have a magnetization Mi of 50 after the readout. Scale the M vector here according to that (ca. 0.5 for FLASH)
    scale = 0.5

    # set parameter values
    sp = Params()
    sp.set_water_pool(r1_w, r2_w, f_w)
    # for each cest pool set a pool in the params
    r1 = [x for x in dir() if x[:2] == 'r1' and x != 'r1_w' and x != 'r1_mt']
    r2 = [x for x in dir() if x[:2] == 'r2' and x != 'r2_w' and x != 'r2_mt']
    k = [x for x in dir() if x[0] == 'k' and x != 'k_w' and x != 'k_mt']
    f = [x for x in dir() if x[0] == 'f' and x != 'f_w' and x != 'f_mt']
    dw = [x for x in dir() if x[:2] == 'dw' and x != 'dw_w' and x != 'dw_mt']
    for pool in range(len(r1)):
        sp.set_cest_pool(eval(r1[pool]), eval(r2[pool]), eval(k[pool]), eval(f[pool]), eval(dw[pool]))
    if 'r1_mt' in dir():
        sp.set_mt_pool(r1_mt, r2_mt, k_mt, f_mt, dw_mt, lineshape_mt)
    sp.set_m_vec(scale)
    sp.set_scanner(b0, gamma, b0_inhom, rel_b1)
    if 'verbose' in dir():
        sp.set_options(verbose=verbose)
    if 'reset_init_mag' in dir():
        sp.set_options(reset_init_mag=reset_init_mag)
    if 'max_pulse_samples' in dir():
        sp.set_options(max_pulse_samples=max_pulse_samples)

    sp_sim = parse_sp(sp, seq_file)

    SimPulseqSBB(sp_sim, seq_file)
    m_out = sp_sim.GetFinalMagnetizationVectors()
    mz = m_out[6, :]

    fig = plot_z(mz, seq_file=seq_file, plot_mtr_asym=True)
    return mz, m_out, fig

mz, m_out, fig = run_standard_cest_sim()
