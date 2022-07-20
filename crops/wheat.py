from .base import BaseCropModel


class WheatModel(BaseCropModel):
    name = '밀'
    _type = 'wheat'
    color = '#cb7a16'
    key = 'wheat'

    # 기본값
    default_start_doy = 284  # 파종

    # 재배관련 - parameter
    base_temperature = 0
    max_dev_temperature = 32
    growth_gdd = 1671  # 생육 완료

    # 재배관련 - warnings
    high_extrema_temperature = 32
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
            'value': [601, 970],
            'max_period': 50,
            'text': '',
            'expose_to': ['events']
        },
        {
            'type': 'heading_range', 'name': '출수',
            'value': [975, 1280],
            'max_period': 30,
            'text': '',
            'expose_to': ['events']
        },
        {
            'type': 'ripening_range', 'name': '등숙',
            'value': [1280, 1665],
            'max_period': 30,
            'text': '',
            'expose_to': ['events']
        },
        {
            'type': 'harvest_range', 'name': '수확',
            'value': [1671, 2595],
            'max_period': 40,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]
    doy_hyperparams = []
    warning_hyperparams = []
