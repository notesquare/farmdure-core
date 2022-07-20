from .base import BaseCropModel


class RadishModel(BaseCropModel):
    name = '무'
    _type = 'radish'
    color = '#5f5442'
    key = 'radish'

    # 기본값
    default_start_doy = 30  # 파종

    # 재배관련 - parameter
    base_temperature = 5
    max_dev_temperature = 35
    growth_gdd = 850  # 생육 완료

    # 재배관련 - warnings
    high_extrema_temperature = 35
    high_extrema_exposure_days = 5
    low_extrema_temperature = 4
    low_extrema_exposure_days = 30

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
            'type': 'harvest_range', 'name': '수확',
            'value': 850,
            'max_period': 10,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]
    doy_hyperparams = []
    warning_hyperparams = []
