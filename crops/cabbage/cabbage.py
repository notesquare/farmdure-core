from ..base import BaseCropModel


class CabbageModel(BaseCropModel):
    name = '배추'
    _type = 'cabbage'

    first_priority_hyperparams = []
    gdd_hyperparams = []
    # 2. 수확은 정식에서부터 45~75일 사이에 위치
    doy_hyperparams = [
        {
            'type': 'fertilize', 'name': '기비',
            'ref': ['transplant'],
            'value': [-7],
            'text': '',
            'expose_to': ['schedules'],
        },
        {
            'type': 'fertilize', 'name': '추비 1차',
            'ref': ['transplant'],
            'value': [15],
            'text': '',
            'expose_to': ['schedules'],
        },
        {
            'type': 'fertilize', 'name': '추비 2차',
            'ref': ['transplant'],
            'value': [30],
            'text': '',
            'expose_to': ['schedules'],
        },
        {
            'type': 'fertilize', 'name': '추비 3차',
            'ref': ['transplant'],
            'value': [45],
            'text': '',
            'expose_to': ['schedules'],
        },
    ]

    warning_hyperparams = [
        {
            'method': 'temperature_and_exposure',
            'high_extrema_temperature': 30,
            'high_extrema_exposure_days': 5,
            'low_extrema_temperature': 5,
            'low_extrema_exposure_days': 5,
        },
        # 수확은 정식에서부터 45~75일 사이에 위치
        {
            'method': 'milestone_length_condition',
            'milestone': {
                'ref': ['transplant', 'harvest_range'],
                'index': [None, 0],
                'value': [0, 0]
            },
            'condition': {
                'length': 75,
                'operator': 'ge'
            },
            'warning_data': {
                'title': '재배가능성 낮음',
                'type': '재배불가능',
                'message': '최대 생육기간 75일 이상입니다.'
            }
        },
        {
            'method': 'milestone_length_condition',
            'milestone': {
                'ref': ['transplant', 'harvest_range'],
                'index': [None, 1],
                'value': [0, 0]
            },
            'condition': {
                'length': 45,
                'operator': 'le'
            },
            'warning_data': {
                'title': '재배가능성 낮음',
                'type': '재배불가능',
                'message': '최소 생육기간 45일 이하입니다.'
            }
        },
    ]
