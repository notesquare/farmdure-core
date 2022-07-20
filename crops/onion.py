from .base import BaseCropModel


class OnionModel(BaseCropModel):
    name = '양파'
    _type = 'onion'
    color = '#aed477'
    key = 'onion'

    # 기본값
    default_start_doy = 238

    # 재배관련 - parameter
    base_temperature = 4.5
    max_dev_temperature = 25
    growth_gdd = 2092  # 생육 완료

    # 재배관련 - hyperparameter
    first_priority_hyperparams = [
        {
            'method': 'GDD',
            'type': 'harvest_range',
            'value': [2092, 2352],
            'max_period': 30,
        },
        {
            'method': 'DOY',
            'type': 'onion_develop_range',
            'ref': ['harvest_range', 'harvest_range'],
            'index': [0, 1],
            'value': [-40, -40],
        },
    ]
    gdd_hyperparams = [
        {
            'type': 'sow', 'name': '파종',
            'value': 0,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
        {
            'type': 'transplant_range', 'name': '정식',
            'value': [790, 1050],
            'max_period': 40,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
        {
            'type': 'harvest_range', 'name': '수확',
            'value': [2092, 2352],
            'max_period': 30,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]
    doy_hyperparams = [
        {
            'type': 'onion_develop_range', 'name': '구비대기',
            'ref': ['harvest_range', 'harvest_range'],
            'index': [0, 1],
            'value': [-40, -40],
            'expose_to': [],
        },
    ]
    warning_hyperparams = [
        {
            'method': 'temperature_and_exposure',
            'high_extrema_temperature': 25,
            'high_extrema_exposure_days': 10,
            'low_extrema_temperature': 4,
            'low_extrema_exposure_days': 30
        },
        {
            'method': 'milestone_and_temperature_condition',
            'milestone': {
                'ref': ['onion_develop_range', 'onion_develop_range'],
                'index': [0, 1],
                'value': [0, 0]
            },
            'condition': {
                'variable': 'tmax',
                'temperature': 25,
                'operator': 'ge'
            },
            'warning_data': {
                'title': '수확량 감소',
                'type': ' 생육저하 주의',
                'message': '구비대기 시기, 25℃ 이상에서 생육둔화'
            }
        },
    ]

