from .base import BaseCropModel


class SweetPotatoModel(BaseCropModel):
    name = '고구마'
    _type = 'sweetPotato'
    color = '#904e50'
    key = 'sweetPotato'
    gdd_method = 'm3'

    # 기본값
    default_start_doy = 131  # 삽식

    # 재배관련 - parameter
    base_temperature = 15.5
    max_dev_temperature = 38
    growth_gdd = 1462  # 생육 완료
    allow_multiple_cropping = True

    # 재배관련 - warnings
    high_extrema_temperature = 32.2
    high_extrema_exposure_days = 15
    low_extrema_temperature = 15
    low_extrema_exposure_days = 30

    # 재배관련 - hyperparameter
    first_priority_hyperparams = [
        {
            'method': 'GDD',
            'type': 'transplant', 'value': 0
        },
    ]
    gdd_hyperparams = [
        {
            'type': 'transplant', 'name': '삽식',
            'value': 0,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
        {
            'type': 'harvest_range', 'name': '수확',
            'value': 1462,
            'max_period': 10,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]
    doy_hyperparams = [
        {
            'type': 'sow', 'name': '파종',
            'ref': ['transplant'],
            'value': [-60],
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]
    warning_hyperparams = []
