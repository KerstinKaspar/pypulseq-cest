"""
simulate.py
"""
from typing import Union
from pathlib import Path
from pySimPulseqSBB import BMCSim, SimulationParameters
from pypulseq_cest.parser import parse_params, get_zspec
from bmctool.set_params import load_params
from bmctool.utils.eval import plot_z


def simulate(config_file: Union[str, Path],
             seq_file: Union[str, Path],
             show_plot: bool = False,
             **kwargs) \
        -> SimulationParameters:
    """
    Function to run a pySimPulseqSBB based simulation for given seq and config files.
    :param config_file: Path of the config file (can be of type str or Path)
    :param seq_file: Path of the seq file (can be of type str or Path)
    :param show_plot: flag to switch plotting option on/off
    """

    # load the parameters
    sp = load_params(config_file)

    # create SWIG object of type SimulationParameters (C++ class)
    sim_params = parse_params(sp=sp, seq_file=seq_file)

    # create SWIG object of type BMCSim (C++ class)
    sim = BMCSim(sim_params, str(seq_file))

    # run simulation
    sim.RunSimulation()

    # retrieve the calculated magnetization
    m_out = sim.GetFinalMagnetizationVectors()

    if show_plot:
        if 'offsets' in kwargs:
            offsets = kwargs.pop('offsets')
            _, mz = get_zspec(m_out=m_out, sp=sp, seq_file=seq_file)
        else:
            offsets, mz = get_zspec(m_out=m_out, sp=sp, seq_file=seq_file)

        plot_z(mz=mz,
               offsets=offsets,
               plot_mtr_asym=False,
               **kwargs)

    return sim_params


def sim_example():
    """
    Function to run an example simulation.
    """
    seq_file = Path(__file__).parent / 'example_library' / 'seq_example.seq'
    config_file = Path(__file__).parent / 'example_library' / 'config_example.yaml'

    simulate(config_file=config_file,
             seq_file=seq_file,
             show_plot=True,
             normalize=True,
             title='Example spectrum')


if __name__ == '__main__':
    sim_example()