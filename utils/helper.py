import os
from pathlib import Path

import yaml


def is_hyperparam_equal(hyperparam1, hyperparam2):
    type1 = hyperparam1['type'].split('_')[0]
    type2 = hyperparam2['type'].split('_')[0]
    name1 = hyperparam1.get('name', '')
    name2 = hyperparam2.get('name', '')
    return type1 == type2 and name1 == name2


def write_hidden_file(dir, fname, data):
    if os.name != 'nt':
        fname = '.' + fname

    with open(Path(dir) / fname, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

    # TODO: hide file in windows
