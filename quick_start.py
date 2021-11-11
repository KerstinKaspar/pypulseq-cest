from pySimPulseqSBB import BMCSim
from pypulseq_cest.parser import parse_params, get_zspec
from bmctool.set_params import load_params
from bmctool.utils.eval import plot_z


# define a config and a sequence file
config_file = 'pypulseq_cest/example_library/config_example.yaml'
seq_file = 'pypulseq_cest/example_library/seq_example.seq'

# load the simulation parameters
sp = load_params(config_file)

# create SWIG object of type SimulationParameters (C++ class)
sim_params = parse_params(sp=sp)

# create SWIG object of type BMCSim (C++ class)
sim = BMCSim(sim_params)

# set external sequence (*.seq) file
sim.LoadExternalSequence(str(seq_file))

# run simulation
sim.RunSimulation()

# retrieve magnetization vectors (x, y and z component of all pools):
m_out = sim.GetCopyOfMagnetizationVectors()

# retrieve offset values and z-magnetization of the water pool
offsets, mz = get_zspec(m_out=m_out, sp=sp, seq_file=seq_file)

# plot z-spectrum
plot_z(mz=mz,
       offsets=offsets,
       normalize=True,
       plot_mtr_asym=True)

