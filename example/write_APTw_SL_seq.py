"""
Script to output a seq file for an APTw protocol with Spin-Lock experiment
source: https://cest-sources.org/doku.php?id=standard_cest_protocols
APTw_1 : APT-weighted, low DC, t_sat=1.8s (//GLINT//)
     pulse shape = Gaussian
     B1 = 2.22 uT
     n = 20
     t_p = 50 ms
     t_d = 40 ms
     DC = 0.55 and t_sat = n*(t_p+t_d) = 1.8 s
     T_rec = 2.4/12 s (saturated/M0)
"""

import math
import numpy as np

from pypulseq.Sequence.sequence import Sequence
# from pypulseq.calc_duration import calc_duration
from pypulseq.make_adc import make_adc
from pypulseq.make_delay import make_delay
# from pypulseq.make_sinc_pulse import make_sinc_pulse
from pypulseq.make_trap_pulse import make_trapezoid
from pypulseq.make_gauss_pulse import make_gauss_pulse
from pypulseq.make_block_pulse import make_block_pulse
from pypulseq.opts import Opts
from example.sl_functions import write_sl_pulses

seq = Sequence()

offset_range = 4  # [ppm]
num_offsets = 24  # number of measurements (not including M0)
run_m0_scan = False  # if you want an M0 scan at the beginning
t_rec = 5  # recovery time between scans [s]
m0_t_rec = 5  # recovery time before m0 scan [s]
sat_b1 = 4  # mean sat pulse b1 [uT]
t_p = 100e-3  # sat pulse duration [ms]
n_pulses = 1  # number of sat pulses per measurement
b0 = 2.89  # B0 [T]
spoiling = 1  # 0=no spoiling, 1=before readout, Gradient in x,y,z

seq_filename = 'example_SLExp.seq'  # filename

# scanner limits
sys = Opts(max_grad=40, grad_unit='mT/m', max_slew=130, slew_unit='T/m/s', rf_ringdown_time=30e-6, rf_dead_time=100e-6,
           rf_raster_time=1e-6)
gamma = sys.gamma * 1e-6

# scanner events
# sat pulse
flip_angle_sat = sat_b1 * gamma * 2 * np.pi * t_p  # rad
rf_sat, _, _ = make_block_pulse(flip_angle=flip_angle_sat, duration=t_p, system=sys)

# make SL Pulses
adia_sl = write_sl_pulses(sat_b1, sys)

# spoilers
spoil_amp = 0.8 * sys.max_grad  # Hz/m
spoil_dur = 4500e-6  # s
gx_spoil, gy_spoil, gz_spoil = [make_trapezoid(channel=c, system=sys, amplitude=spoil_amp, duration=spoil_dur)
                                for c in ['x', 'y', 'z']]

# pseudo adc (not played out)
pseudo_adc = make_adc(num_samples=1, duration=1e-3)

# loop through z spectrum offsets
offsets_ppm = np.linspace(-offset_range, offset_range, num_offsets)
offsets = offsets_ppm * gamma * b0

if run_m0_scan:
    seq.add_block(make_delay(m0_t_rec))
    seq.add_block(pseudo_adc)

# loop through offsets and set pulses and delays
for o in offsets:
    # take care of phase accumulation during off-res pulse
    seq.add_block(make_delay(t_rec))  # recovery time
    # TODO this is just roughly
    if o < 0:
        pre_sl, post_sl = adia_sl['pos']
    else:
        pre_sl, post_sl = adia_sl['neg']
    pre_sl.freq_offset = o
    phase = np.mod(o * 2 * np.pi * np.where(np.abs(pre_sl.signal) > 0)[0].size * 1e-6, 2 * np.pi)
    rf_sat.phase_offset = np.mod(phase, 2*np.pi)
    rf_sat.freq_offset = o
    phase = np.mod(o * 2 * np.pi * np.where(np.abs(rf_sat.signal) > 0)[0].size * 1e-6, 2 * np.pi)
    post_sl.phase_offset = np.mod(phase, 2*np.pi)
    post_sl.freq_offset = o
    seq.add_block(pre_sl)
    seq.add_block(rf_sat)
    seq.add_block(post_sl)
    if spoiling:
        seq.add_block(gx_spoil, gy_spoil, gz_spoil)
    seq.add_block(pseudo_adc)

seq.set_definition('offsets_ppm', offsets_ppm)
seq.set_definition('run_m0_scan', str(run_m0_scan))
seq.write(seq_filename)
