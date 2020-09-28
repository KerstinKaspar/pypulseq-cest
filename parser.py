from SimPulseqSBB import SimulationParameters, WaterPool
from params import Params


def parse_sp(sp: Params, num_adc_events: int = 1):
    # sp = Params()
    sp_sim = SimulationParameters()
    # init magnetization vector
    sp_sim.InitMagnetizationVectors(sp.m_vec, num_adc_events)
    # constructwater pool
    water_pool = WaterPool(sp.water_pool.r1, sp.water_pool.r2, sp.water_pool.f)
    sp_sim.SetWaterPool(water_pool)

    return sp_sim