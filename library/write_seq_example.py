# write_seq_example.py
# Creates an example sequence file (10 offsets, 10 block pulses with tp = 100 ms, td = 10 ms, B1 = 2 µT)
#
# P. Schuenke and K. Heinecke 2020
# patrick.schuenke@ptb.de

import os
import numpy as np
from pypulseq.Sequence.sequence import Sequence
from pypulseq.make_adc import make_adc
from pypulseq.make_delay import make_delay
from pypulseq.make_trap_pulse import make_trapezoid
from pypulseq.make_block_pulse import make_block_pulse
from pypulseq.opts import Opts
from bmctool.utils.seq.write import write_seq

# get id of generation file
seqid = 'seq_example'

# general settings
author = 'P. Schuenke and K. Heinecke'
plot_sequence = False  # plot preparation block?
convert_to_1_3 = True  # convert seq-file to a pseudo version 1.3 file?

# sequence definitions (everything in seq_defs will be written to definitions in .seq-file)
seq_defs:dict = {}
seq_defs['b0'] = 7  # B0 [T]
seq_defs['b1cwpe'] = 2.0  # cw power equivalent [µT]
seq_defs['n_pulses'] = 10  # number of pulses
seq_defs['tp'] = 100e-3  # pulse duration [s]
seq_defs['td'] = 10e-3  # interpulse delay [s]
seq_defs['trec'] = 3  # recovery time [s]
seq_defs['trec_m0'] = 12  # recovery time before M0 [s]

seq_defs['m0_offset'] = -300  # m0 offset [ppm]
seq_defs['offsets_ppm'] = np.append(seq_defs['m0_offset'], np.linspace(-10, 10, 101))  # offset vector [ppm]

seq_defs['dcsat'] = (seq_defs['tp']) / (seq_defs['tp'] + seq_defs['td'])  # duty cycle
seq_defs['num_meas'] = seq_defs['offsets_ppm'].size  # number of repetition
seq_defs['tsat'] = seq_defs['n_pulses'] * (seq_defs['tp'] + seq_defs['td']) - seq_defs['td']  # saturation time [s]
seq_defs['seq_id_string'] = seqid  # unique seq id

seq_filename = seq_defs['seq_id_string'] + '.seq'

# scanner limits
sys = Opts(max_grad=40, grad_unit='mT/m', max_slew=130, slew_unit='T/m/s',
           rf_ringdown_time=30e-6, rf_dead_time=100e-6, rf_raster_time=1e-6)

gamma_hz = 42.5764

# ===========
# PREPARATION
# ===========

# spoiler
spoil_amp = 0.8 * sys.max_grad  # Hz/m
rise_time = 1.0e-3  # spoiler rise time in seconds
spoil_dur = 4.5e-3  # complete spoiler duration in seconds

gx_spoil, gy_spoil, gz_spoil = [make_trapezoid(channel=c, system=sys, amplitude=spoil_amp, duration=spoil_dur,
                                               rise_time=rise_time) for c in ['x', 'y', 'z']]

# RF pulses
flip_angle_sat = seq_defs['b1cwpe'] * gamma_hz * 2 * np.pi * seq_defs['tp']
sat_pulse, _ = make_block_pulse(flip_angle=flip_angle_sat, duration=seq_defs['tp'], system=sys)

# ADC events
pseudo_adc = make_adc(num_samples=1, duration=1e-3)  # (not played out; just used to split measurements)

# DELAYS
post_spoil_delay = make_delay(50e-6)
td_delay = make_delay(seq_defs['td'])
trec_delay = make_delay(seq_defs['trec'])
m0_delay = make_delay(seq_defs['trec_m0'])

# Sequence object
seq = Sequence()

# ===
# RUN
# ===

offsets_hz = seq_defs['offsets_ppm'] * gamma_hz * seq_defs['b0']  # convert from ppm to Hz

for offset in offsets_hz:
    # add delay
    if offset == seq_defs['m0_offset'] * gamma_hz * seq_defs['b0']:
        if seq_defs['trec_m0'] > 0:
            seq.add_block(m0_delay)
    else:
        if seq_defs['trec'] > 0:
            seq.add_block(trec_delay)
    # set sat_pulse
    sat_pulse.freq_offset = offset
    accum_phase = 0
    for n in range(seq_defs['n_pulses']):
        sat_pulse.phase_offset = accum_phase % (2 * np.pi)
        seq.add_block(sat_pulse)
        accum_phase = (accum_phase + offset * 2 * np.pi * np.sum(sat_pulse.signal > 0) * 1e-6) % (2 * np.pi)
        if n < seq_defs['n_pulses']-1:
            seq.add_block(td_delay)
    print(np.where(offsets_hz == offset)[0][0], '/', len(offsets_hz), ': offset ', offset)
    seq.add_block(gx_spoil, gy_spoil, gz_spoil)
    seq.add_block(pseudo_adc)

write_seq(seq=seq,
          seq_defs=seq_defs,
          filename=seqid+'.seq',
          author=author,
          use_matlab_names=True,
          convert_to_1_3=convert_to_1_3)

# plot the sequence
if plot_sequence:
    seq.plot(time_range=[0, seq_defs['trec_m0']+seq_defs['tsat']])  # to plot all offsets, remove time_range argument
