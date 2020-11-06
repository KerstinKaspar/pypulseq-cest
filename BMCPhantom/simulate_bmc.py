"""
simulate_bmc.py
    Script to run the BMCTool simulation based on the defined parameters.
    You can adapt parameters in param_configs.py or use a standard CEST setting as defined in standard_cest_params.py.
"""
from sim_bmc.bmc_tool_v2 import BMCTool
from sim_pulseq_sbb.eval import plot_z
from sim_pulseq_sbb.set_params import load_params

# set the necessary filepaths:
sample_file = 'param_configs/sample_params.yaml'
experimental_file = 'param_configs/experimental_params.yaml'
seq_file = 'example/example_APTw_test.seq'


sim_params = load_params(sample_file, experimental_file)

Sim = BMCTool(sim_params, seq_file)

Sim.run(par_calc=True)

m_out = Sim.Mout

mz = m_out[sim_params.mz_loc, :]

fig = plot_z(mz, seq_file=seq_file, plot_mtr_asym=True)
