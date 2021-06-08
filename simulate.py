from bmctool.utils.eval import plot_z

from pypulseq_cest.parser import get_zspec
from pypulseq_cest.simulate import simulate


# You need a simulation configuration file in the YAML format and a sequence file in the seq format (see **Configuration and sequence file library** below). For example:
sim_config = 'pypulseq_cest/example_library/config_example.yaml'
seq_file = 'pypulseq_cest/example_library/seq_example.seq'

# Run the simulateions with a
sim = simulate(config_file=sim_config, seq_file=seq_file, show_plot=False)

# If you need additional processing, you can access the sunctions directly from the simulation object:
# For example, you can retrieve the magnetization vector with the following function:
m_out = sim.GetFinalMagnetizationVectors()

# To get the correct magnetization in z-direction, you can use the following function.
offsets, mz = get_zspec(m_out=m_out, sp=sim, seq_file=seq_file, normalize_if_m0=True)

# You can plot the magnetization with the following function from the bmctool:
plot_z(mz=mz, offsets=offsets)
