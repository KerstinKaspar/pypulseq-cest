"""
function M_z = Standard_pulseq_cest_Simulation(seq_fn, B0)
  Run pulseq SBB simulation
 example for a Z - spectrum for GM at 3T with
 - 2 CEST pools
 - a Lorentzian shaped MT pool

 All parameters are saved in a struct which is the input for the mex file
 Kai Herz, 2020
 kai.herz @ tuebingen.mpg.de
"""
import numpy as np

from SimPulseqSBB import SimPulseqSBB
from parse_params import parse_sp, get_offsets
from simulation_params import *
import matplotlib.pyplot as plt
import pypulseq
from pypulseq.Sequence.sequence import Sequence

# set parameter values
sp = Params()
sp.set_water_pool(r1_w, r2_w, f_w)
# for each cest pool set a pool in the params
r1 = [x for x in dir() if 'r1_' in x and x != 'r1_w' and x != 'r1_mt']
r2 = [x for x in dir() if 'r2_' in x and x != 'r2_w' and x != 'r2_mt']
k = [x for x in dir() if 'k_' in x and x != 'k_w' and x != 'k_mt']
f = [x for x in dir() if 'f_' in x and x != 'f_w' and x != 'f_mt']
dw = [x for x in dir() if 'dw_' in x and x != 'dw_w' and x != 'dw_mt']
for pool in range(len(r1)):
    sp.set_cest_pool(eval(r1[pool]), eval(r2[pool]), eval(k[pool]), eval(f[pool]), eval(dw[pool]))
if 'r1_mt' in dir():
    sp.set_mt_pool(r1_mt, r2_mt, k_mt, f_mt, dw_mt, lineshape_mt)
sp.set_m_vec(scale)
sp.set_scanner(b0, gamma, b0_inhom, rel_b1)
if 'verbose' in dir():
    sp.set_options(verbose)
if 'reset_init_mag' in dir():
    sp.set_options(reset_init_mag)
if 'max_pulse_samples' in dir():
    sp.set_options(max_pulse_samples)

sp_sim = parse_sp(sp, seq_file)

SimPulseqSBB(sp_sim, seq_file)
m_out = sp_sim.GetFinalMagnetizationVectors()
print(m_out)
mz = m_out[2, :]

plt.figure()
offsets = get_offsets(seq_file)
plt.title('Z-spec')
plt.ylabel('M')
plt.xlabel('Offsets')
plt.plot(offsets, mz, '.--')
plt.show()

seq = Sequence()
seq.read(seq_file)






