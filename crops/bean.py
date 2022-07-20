from .base import BaseCropModel


class BeanModel(BaseCropModel):
    name = '콩'
    _type = 'bean'
    color = '#3aa584'
    key = 'bean'

    # 기본값
    default_start_doy = 172

    # 재배관련 - warnings
    high_extrema_temperature = 35
    high_extrema_exposure_days = 5
    low_extrema_temperature = 20
    low_extrema_exposure_days = 30

    # 재배관련 - parameter
    base_temperature = 0
    max_dev_temperature = 35
    growth_gdd = 2700  # 생육 완료

    # 재배관련 - hyperparameter
    first_priority_hyperparams = []
    gdd_hyperparams = [
        {
            'type': 'sow', 'name': '파종',
            'value': 0,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
        {
            'type': 'bloom_range', 'name': '개화',
            'value': [450, 1840],
            'max_period': 20,
            'text': '',
            'expose_to': ['events']
        },
        {
            'type': 'harvest_range', 'name': '수확',
            'value': 2700,
            'max_period': 10,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]
    doy_hyperparams = []
    warning_hyperparams = []
