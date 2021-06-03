"""
simulate.py
"""
from pySimPulseqSBB import SimPulseqSBB
from pypulseq_cest.parser import parse_params, get_zspec, Params
from bmctool.set_params import load_params
from bmctool.utils.eval import plot_z


def simulate(sim_config: str, seq_file:str) -> Params:
    # load the parameters
    sp = load_params(sim_config)

    # parse for C++ handling
    sim_params = parse_params(sp=sp, seq_file=seq_file)

    # run the simulation
    SimPulseqSBB(sim_params, seq_file)

    # retrieve the calculated magnetization
    m_out = sim_params.GetFinalMagnetizationVectors()
    offsets, mz = get_zspec(m_out=m_out, sp=sp, seq_file=seq_file)

    # plot raw spectrum
    plot_z(mz=mz, offsets=offsets)

    return sim_params


if __name__ == '__main__':
    # set the necessary file paths
    sim_config = '../library/config_example.yaml'
    seq_file = '../library/seq_example.seq'
