from .base import BaseCropModel


class ChiliModel(BaseCropModel):
    name = '고추'
    _type = 'chili'
    color = '#da2128'
    key = 'chili'

    # 기본값
    default_start_doy = 106  # 정식

    # 재배관련 - parameter
    base_temperature = 5
    max_dev_temperature = 35
    growth_gdd = 1000

    # 재배관련 - hyperparameter
    first_priority_hyperparams = [
        {
            'method': 'GDD',
            'type': 'transplant',
            'value': 0
        },
        {
            'method': 'GDD',
            'type': 'bloom_range',
            'value': [150, 1950]
        },
    ]
    gdd_hyperparams = [
        {
            'type': 'transplant', 'name': '정식',
            'value': 0,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
        {
            'type': 'bloom_range', 'name': '개화',
            'value': [150, 1950],
            'text': '',
            'expose_to': []
        },
        {
            'type': 'harvest_range', 'name': '풋고추 수확',
            'value': [550, 1070],
            'max_period': 30,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
        {
            'type': 'harvest_range', 'name': '붉은고추 수확',
            'value': [1085, 2730],
            'max_period': 80,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]

    doy_hyperparams = [
        {
            'type': 'sow', 'name': '파종',
            'ref': ['transplant'],
            'value': [-65],
            'text': '',
            'expose_to': ['events', 'schedules']
        },
        {
            'type': 'fertilize_range', 'name': '기비',
            'ref': ['transplant', 'transplant'],
            'value': [-21, -14],
            'text': '흙갈이 하기 2~3주 전 석회, 붕소 비료를 투여',
            'expose_to': ['schedules']
        },
        {
            'type': 'fertilize', 'name': '기비',
            'ref': ['transplant'],
            'value': [-7],
            'text': '이랑 만들기 7일 전 화학비료 투여',
            'expose_to': ['schedules']
        },
        {
            'type': 'fertilize_range', 'name': '추비 1차',
            'ref': ['transplant', 'transplant'],
            'value': [25, 30],
            'text': '',
            'expose_to': ['schedules']
        },
        {
            'type': 'fertilize_range', 'name': '추비 2차',
            'ref': ['transplant', 'transplant'],
            'value': [50, 60],
            'text': '',
            'expose_to': ['schedules']
        },
        {
            'type': 'fertilize_range', 'name': '추비 3차',
            'ref': ['transplant', 'transplant'],
            'value': [75, 90],
            'text': '',
            'expose_to': ['schedules']
        },
    ]

    warning_hyperparams = [
        {
            'method': 'temperature_and_exposure',
            'high_extrema_temperature': 40,
            'high_extrema_exposure_days': 5,
            'low_extrema_temperature': 10,
            'low_extrema_exposure_days': 30
        },
        {
            'method': 'milestone_and_temperature_condition',
            'milestone': {
                'ref': ['bloom_range', 'bloom_range'],
                'index': [0, 1],
                'value': [-13, -17]
            },
            'condition': {
                'variable': 'tavg',
                'temperature': 30,
                'operator': 'ge'
            },
            'warning_data': {
                'title': '수확량 감소',
                'type': '이상화분 발생 주의',
                'message': """
                    개화 전 13 ~ 17일 기간에서 30℃ 이상의 온도에 노출될 경우 화분의 수정능력이 저하됩니다.
                """
            }
        },
    ]
