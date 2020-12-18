"""
function fedinitions to pars the parameters into the C++ class
"""

from pySimPulseqSBB import SimulationParameters, WaterPool, MTPool, CESTPool
from sim.params import Params
from pySimPulseqSBB import Lorentzian, SuperLorentzian, NoLineshape


def parse_params(sp: Params,
                 seq_file: str) -> SimulationParameters:
    """
    parsing python parameters into the according C++ functions
    :param sp: simulation parameter object
    :param seq_file: location of the seq-file to simulate
    :return: SWIG object for C++ object handling
    """
    sp_sim = SimulationParameters()
    # pass offsets and m0 to sp
    sp.set_definitions(seq_file=seq_file)
    # init magnetization vector
    num_adc_events = sp.get_num_adc_events() + 1
    sp_sim.InitMagnetizationVectors(sp.m_vec, num_adc_events)
    # constructwater pool
    water_pool = WaterPool(sp.water_pool['r1'], sp.water_pool['r2'], sp.water_pool['f'])
    sp_sim.SetWaterPool(water_pool)
    if sp.mt_pool:
        lineshape = set_lineshape(sp.mt_pool['lineshape'])
        mt_pool = MTPool(sp.mt_pool['r1'], sp.mt_pool['r2'], sp.mt_pool['f'], sp.mt_pool['dw'], sp.mt_pool['k'], lineshape)
        sp_sim.SetMTPool(mt_pool)
    sp_sim.InitCESTPoolMemory(len(sp.cest_pools))
    for i in range(len(sp.cest_pools)):
        cest_pool = CESTPool(sp.cest_pools[i]['r1'], sp.cest_pools[i]['r2'], sp.cest_pools[i]['f'], sp.cest_pools[i]['dw'], sp.cest_pools[i]['k'])
        sp_sim.SetCESTPool(cest_pool, i)
    sp_sim.InitScanner(sp.scanner['b0'], sp.scanner['rel_b1'], sp.scanner['b0_inhomogeneity'], sp.scanner['gamma'])
    if 'verbose' in sp.options.keys():
        sp_sim.SetVerbose(sp.options['verbose'])
    if 'reset_init_mag' in sp.options.keys():
        sp_sim.SetUseInitMagnetization(sp.options['reset_init_mag'])
    if 'max_pulse_samples' in sp.options.keys():
        sp_sim.SetMaxNumberOfPulseSamples(sp.options['max_pulse_samples'])
    return sp_sim


def set_lineshape(ls: str = None) -> (Lorentzian, SuperLorentzian, NoLineshape):
    """
    return the according lineshape object
    """
    try:
        if ls == 'Lorentzian':
            return Lorentzian
        elif ls == 'SuperLorentzian':
            return SuperLorentzian
        elif not ls:
            return NoLineshape
    except ValueError:
        print(ls + ' is not a valid lineshape for MT Pool.')




