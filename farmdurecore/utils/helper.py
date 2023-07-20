import yaml
from pathlib import Path


def is_hyperparam_equal(hyperparam1, hyperparam2):
    type1 = hyperparam1['type']
    type2 = hyperparam2['type']
    name1 = hyperparam1.get('name', '')
    name2 = hyperparam2.get('name', '')

    return type1 == type2 and name1 == name2


def is_hyperparam_valid(hyperparam):
    ranged = hyperparam.get('ranged', False)
    if ranged is True:
        if (hyperparam.get('period') is None and
                not isinstance(hyperparam['value'], list)):
            return False
    else:
        if (hyperparam.get('period') is not None or
                isinstance(hyperparam['value'], list)):
            return False
    return True


def get_default_crop_params(crop_key):
    fp = Path(__file__).parent.parent / 'parameters.yaml'
    with open(fp, 'r', encoding='utf-8') as f_param:
        crop_params = yaml.load(
            f_param,
            Loader=yaml.FullLoader
        )

    return crop_params[crop_key]
