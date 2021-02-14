"""
simulate.py
    Script to run the C++ SimPulseqSBB simulation based on the defined parameters.
    You need to define the files containing sample and experimental parameters, as well as the sequence file.
"""
from pySimPulseqSBB import SimPulseqSBB
from sim.parse_params import parse_params
from sim.set_params import load_params
from sim.utils.eval import get_zspec, plot_z

# set the necessary filepaths
sim_config = 'library/config_example.yaml'
seq_file = 'library/seq_example.seq'

# if pulse library is installed try this
# sim_config = '../pulseq-cest-library/sim-library/GM_3T_001_bmsim.yaml'
# seq_file = '../pulseq-cest-library/seq-library/APTw_3T_003_2uT_8block_DC95_834ms_braintumor/APTw_3T_003_2uT_8block_DC95_834ms_braintumor.seq'


# load the parameters
sp = load_params(sim_config)
# parse for C++ handling
sim_params = parse_params(sp=sp, seq_file=seq_file)
# run the simulation
SimPulseqSBB(sim_params, seq_file)

# retrieve the calculated magnetization
m_out = sim_params.GetFinalMagnetizationVectors()
mz = get_zspec(m_out=m_out, sp=sp, noise=(0, 0))

# plot raw spectrum
plot_z(mz=mz, offsets=sp.offsets)

# plot normalized spectrum and asymmetry
plot_z(mz=mz[1:]/mz[0], offsets=sp.offsets[1:], plot_mtr_asym=True)
