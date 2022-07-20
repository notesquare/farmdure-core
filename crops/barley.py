from .base import BaseCropModel


class BarleyModel(BaseCropModel):
    name = '보리'
    _type = 'barley'
    color = '#d0ab4a'
    key = 'barley'

    # 기본값
    default_start_doy = 290  # 파종

    # 재배관련 - parameter
    base_temperature = 0
    max_dev_temperature = 30
    growth_gdd = 1600  # 생육 완료 실제값 1800

    # 재배관련 - warnings
    high_extrema_temperature = 30
    high_extrema_exposure_days = 5
    low_extrema_temperature = 3
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
            'type': 'tillering_range', 'name': '분얼 및 신장',
            'value': [525, 885],
            'max_period': 50,
            'text': '',
            'expose_to': ['events']
        },
        {
            'type': 'heading_range', 'name': '출수',
            'value': [896, 1200],
            'max_period': 30,
            'text': '',
            'expose_to': ['events']
        },
        {
            'type': 'ripening_range', 'name': '등숙',
            'value': [1200, 1600],  # 등숙 실제값 [1200, 1800]
            'max_period': 40,
            'text': '',
            'expose_to': ['events']
        },
        {
            'type': 'harvest_range', 'name': '수확',
            'value': [1600, 2295],
            'max_period': 40,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]
    doy_hyperparams = []
    warning_hyperparams = []
