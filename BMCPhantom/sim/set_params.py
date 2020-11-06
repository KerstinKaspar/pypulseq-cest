"""
param_configs.py
    Script to set the parameters used for the simulation.

Only the parameter values need to be adapted: If the simulation is started from simulate.py, this file does not need
to be run separately, the setting of the parameters into the class instance will be handled automatically.

PARAMETERS:
    b0: field strength [T]
    gamma: gyromagnetic ratio [rad / uT]
    b0_inhom: field inhomogeneity [ppm]
    rel_b1: relative b1
    f: proton fraction (relative)
    dw: chemical shift from water [ppm]
    k: exchange rate [Hz]
    lineshape_mt: lineshape of the MT Pool ('Lorentzian', 'SuperLorentzian' or 'None')
"""

from sim_pulseq_sbb.params import Params
from os import path
import yaml


def load_config(*args: str) -> dict:
    """
    Load config yaml files from path.
    :params args: path(s) of the file(s) containing comfiguration parameters
    """
    config = {}
    for filepath in args:
        with open(filepath) as file:
            config.update(yaml.load(file, Loader=yaml.Loader))
    return config


def check_values(val_dict, config, invalid, dict_key=None):
    valids = load_config('param_configs/maintenance/valid_params.yaml')
    valid_num = valids['valid_num']
    valid_str = valids['valid_str']
    valid_bool = valids['valid_bool']
    valid_lineshapes = valids['valid_lineshapes']
    for k, v in val_dict.items():
        if k not in valid_num + valid_str + valid_bool:
            if dict_key:
                invalid.append(k + ' in ' + dict_key)
            else:
                invalid.append(k)
        elif k in valid_str:
            if type(v) is not str:
                if dict_key:
                    invalid.append(str(v) + ' value from ' + k + ' in ' + dict_key + ' should be of type string.')
                else:
                    invalid.append(str(v) + ' value from ' + k + ' should be of type string.')
        elif k in valid_num:
            if type(v) not in [float, int]:
                if type(v) is str:
                    if type(eval(v)) in [float, int]:
                        if dict_key:
                            config[dict_key][k] = eval(v)
                        else:
                            config[k] = eval(v)
                    else:
                        if dict_key:
                            invalid.append(str(v) + ' value from ' + k + ' in ' + dict_key + ' should be a numerical type.')
                        else:
                            invalid.append(str(v) + ' value from ' + k + ' should be a numerical type.')
        elif k in valid_bool:
            if type(v) is not bool:
                if v in ['true', 'True', 'TRUE', 'yes', 'Yes', 'yes', 1]:
                    if dict_key:
                        config[dict_key][k] = True
                    else:
                        config[k] = True
                elif v in ['false', 'False', 'FALSE', 'no', 'No', 'NO', 0]:
                    if dict_key:
                        config[dict_key][k] = False
                    else:
                        config[k] = False
                else:
                    if dict_key:
                        invalid.append(str(v) + ' value from ' + k + ' in ' + dict_key + ' should be of type bool.')
                    else:
                        invalid.append(str(v) + ' value from ' + k + ' should be of type bool.')
        if k == 'seq_file':
            if not path.exists(v):
                invalid.append('Seq_file leads to an invalid path.')
        if k == 'lineshape':
            if v not in valid_lineshapes:
                if v in ['None', 'none', 'NONE', False, 'False', 'false', 'FALSE', 'no', 'No', 'NO']:
                    config[dict_key][k] = None
                else:
                    invalid.append(str(v) + ' value from ' + k + ' in ' + dict_key + ' should be out of: ' +
                                   ''.join(l + ', ' for l in valid_lineshapes[:-1]) + valid_lineshapes[-1])
    return config, invalid


def check_cest_values(dv, config, invalid, k, dk):
    if 'cest_pools' in config.keys():
        config['cest_pool'] = config.pop('cest_pools')
    conf_temp = config['cest_pool']
    conf_temp, invalid_new = check_values(dv, conf_temp, invalid, dk)
    if invalid_new != invalid:
        invalid_new.append('some definition in cest_pool')
    config['cest_pool'] = conf_temp
    return config, invalid


def check_necessary(config: dict, necessary, necessary_w):
    missing = []
    for n in necessary:
        if n not in config.keys():
            missing.append(n)
    if missing:
        raise AssertionError('The following parameters have to be defined: ' + ''.join(m + ', ' for m in missing[:-1])
                             + missing[-1])
    for n in necessary_w:
        if n not in config['water_pool'].keys():
            missing.append(n)
    if missing:
        raise AssertionError('The following water_pool parameters have to be defined: ' +
                             ''.join(m + ', ' for m in missing[:-1]) + missing[-1])


def check_params(config):
    invalid = []
    valids = load_config('param_configs/maintenance/valid_params.yaml')
    valid = valids['valid_first']
    valid_dict = valids['valid_dict']
    necessary = valids['necessary']
    necessary_w = valids['necessary_w']
    check_necessary(config=config, necessary=necessary, necessary_w=necessary_w)
    config_dicts = {ck: cv for ck, cv in config.items() if type(cv) is dict}
    config_vals = {ck: cv for ck, cv in config.items() if type(cv) is not dict}
    for k, v in config.items():
        if k not in valid:
            invalid.append(k)
    for k, v in config_dicts.items():
        if type(v[list(v.keys())[0]]) is dict:
            if k in valid_dict:
                for dk, dv in v.items():
                    config, invalid = check_cest_values(dv, config, invalid, k, dk)
            else:
                invalid.append(k)
        else:
            config, invalid = check_values(v, config, invalid, dict_key=k)
    config, invalid = check_values(config_vals, config, invalid)
    if invalid:
        raise AssertionError('Check parameter configuration files! \n '
                             'Invalid: ' + ''.join(str(i) + ', ' for i in invalid[:-1]) + str(invalid[-1]))
    return config


def pprint_dict(dictionary: dict):
    for k, v in dictionary.items():
        print(k, ':', v)


def verbose_output(config: dict):
    print('You defined the following parameters:')
    pprint_dict({k: v for k, v in config.items() if type(v) is not dict})
    print('You set a water pool with the parameters:')
    pprint_dict(config['water_pool'])
    if 'mt_pool' in config.keys() and type(config['mt_pool']) is dict:
        print('You set an mt_pool with the parameters:')
        pprint_dict(config['mt_pool'])
    if 'cest_pool' in config.keys() and type(config['cest_pool']) is dict:
        print('You set {} CEST pools():'.format(len(config['cest_pool'])))
        for k, v in config['cest_pool']:
            print('You set an {} pool with the parameters:'.format(k))
            pprint_dict(v)


def load_params(sample_filepath: str, experimental_filepath: str) -> object:
    """
    Load parameters into simulation parameter object
    :param sample_filepath: path for the file containing sample parameters
    :param experimental_filepath: path for the file containing experimental parameters
    """
    # load the configurations from the files
    config = load_config(sample_filepath, experimental_filepath)
    # check parameters for missing, typos, wrong assignments
    config = check_params(config)
    config['sample_params'] = sample_filepath[:-5]
    config['experimental_params'] = experimental_filepath[:-5]
    # print configuration settings
    if 'verbose' in config.keys() and config['verbose']:
        verbose_output(config)
    # instantiate class to store the parameters
    sp = Params(config=config)
    # scanner and inhomogeneity settings
    sp.set_scanner(**{k: v for k, v in config.items() if k in ['b0', 'gamma', 'b0_inhom', 'rel_b1']})
    # water pool settings
    sp.set_water_pool(**config['water_pool'])
    # mt_pool settings
    if 'mt_pool' in config.keys() and config['mt_pool']:
        sp.set_mt_pool(**config['mt_pool'])
    # cest pool settings
    if 'cest_pool' in config.keys() and config['cest_pool']:
        for pool_name, pool_params in config['cest_pool'].items():
            sp.set_cest_pool(**pool_params)
    # scale
    if 'scale' in config.keys():
        sp.set_m_vec(config['scale'])
    else:
        sp.set_m_vec()
    # optional params
    sp.set_options(**{k: v for k, v in config.items() if k in ['reset_init_mag', 'max_pulse_samples', 'par_calc',
                                                               'verbose']})
    return sp


