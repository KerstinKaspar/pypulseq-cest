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
from SimPulseqSBB import SimPulseqSBB
from params import Params
from parser import parse_sp
from simulation_params import *

# set parameter values
sp = Params()
sp.set_water_pool(r1_w, r2_w, f_w)
sp.set_cest_pool(r1_a, r2_a, k_a, f_a, dw_a)
sp.set_cest_pool(r1_c, r2_c, k_c, f_c, dw_c)
sp.set_mt_pool(r1_mt, r2_mt, k_mt, f_mt, dw_mt, lineshape_mt)
sp.set_m_vec(scale)
sp.set_scanner(b0, gamma, b0_inhom, rel_b1)
sp.set_options(verbose, reset_init_mag, max_pulse_samples)

sp_sim = parse_sp(sp)

m_out = SimPulseqSBB(sp_sim, seq)

# if 0:
#     seq = mr.Sequence
#     seq.read(seq_fn)
#     [ppm_sort, idx] = sort(seq.definitions('offsets_ppm'))
#
#     tic
#     # t2star
#     decay, see
#     DOI
#     10.1002 / mrm
#     .22406
#     eq.
#     6
#     num_spins = 63
#     spin_dist = linspace(-.5, .5, num_spins)
#     spin_dist = spin_dist. * 0.95  # to
#     avoid
#     extremely
#     large
#     values
#     for tan(.5 * ppi)
#         R2star = 30
#     dw_spins = R2star * tan(pi * spin_dist)
#     dw_spins = dw_spins. / (sp.Scanner.b0 * sp.Scanner.Gamma)
#
#     Z_sim = zeros(num_spins, size(M_out, 1), size(M_out, 2))
# parfor
# ii = 1:num_spins
#  sp_local =  sp  # local
# variable
# for parfor loop
#      sp_local.Scanner.B0Inhomogeneity = dw_spins(ii)
# M_out = Sim_pulseqSBB( sp_local, seq_fn)  # run
# sim
# Z_sim(ii,:,:)=M_out
# end
#
# # figure, plot(squeeze(Z_sim(:, nTotalPools * 2 + 1,:))' )
#                                                        # hold
# on,
#
# toc
# M_out = squeeze(mean(Z_sim, 1))
# # plot(M_out(nTotalPools * 2 + 1,:), 'ok')
# end
#
# M_z = M_out(nTotalPools * 2 + 1,:)
#
#
