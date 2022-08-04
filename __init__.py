from pathlib import PurePath

import yaml


DEFAULT_PARAMETERS_FP = PurePath(__file__).parent / 'default_parameters.yaml'
with open(DEFAULT_PARAMETERS_FP, 'r') as f_param:
    cropParameters = yaml.load(f_param, Loader=yaml.FullLoader)


__all__ = ['cropParameters']
