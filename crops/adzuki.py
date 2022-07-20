from .base import BaseCropModel


class AdzukiModel(BaseCropModel):
    name = '팥'
    _type = 'adzuki'
    color = '#bb7178'
    key = 'adzuki'

    # 기본값
    default_start_doy = 146

    # 재배관련 - parameter
    base_temperature = 5
    max_dev_temperature = 24
    growth_gdd = 2300  # 생육 완료

    # 재배관련 - warnings
    high_extrema_temperature = 30
    high_extrema_exposure_days = 15
    low_extrema_temperature = 16
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
            'type': 'bloom_range', 'name': '개화',
            'value': [850, 1240],
            'max_period': 20,
            'text': '',
            'expose_to': ['events']
        },
        {
            'type': 'harvest_range', 'name': '수확',
            'value': 2300,
            'max_period': 10,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]
    doy_hyperparams = []
    warning_hyperparams = []
