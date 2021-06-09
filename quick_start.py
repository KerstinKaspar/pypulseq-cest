from pypulseq_cest.parser import get_zspec
from pypulseq_cest.simulate import simulate


# Define a config and a sequence file
sim_config = 'pypulseq_cest/example_library/config_example.yaml'
seq_file = 'pypulseq_cest/example_library/seq_example.seq'

# Start the simulations:
sim = simulate(config_file=sim_config, seq_file=seq_file, show_plot=True, normalize=True)  # check readme for more information about simulate function

# Retrieve magnetization vector (x,y,and z component) of the water pool:
m_out = sim.GetFinalMagnetizationVectors()

# Retrieve offset values and z-magnetization of the water pool
offsets, mz = get_zspec(m_out=m_out, sp=sim, seq_file=seq_file)
print(f'The offsets used for simulation are: \n{offsets}')

