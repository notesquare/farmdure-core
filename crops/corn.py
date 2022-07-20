from .base import BaseCropModel


class CornModel(BaseCropModel):
    name = '옥수수'
    _type = 'corn'
    color = '#fed55c'
    key = 'corn'

    # 기본값
    default_start_doy = 96  # 파종

    # 재배관련 - parameter
    base_temperature = 5
    max_dev_temperature = 45
    growth_gdd = 1400  # 생육 완료
    allow_multiple_cropping = True

    # 재배관련 - hyperparameter
    harvest_gdd = 1400  # 수확

    first_priority_hyperparams = [
        {
            'method': 'GDD',
            'type': 'sow',
            'value': 0
        },
        {
            'method': 'GDD',
            'type': 'silking_range',
            'value': 1049,
            'max_period': 14,
        },
        {
            'method': 'DOY',
            'type': 'tasselling_range',
            'ref': ['silking_range', 'silking_range'],
            'index': [0, 1],
            'value': [-7, -6],
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
            'type': 'silking_range', 'name': '출사',
            'value': 1049,
            'max_period': 14,
            'text': '',
            'expose_to': ['events']
        },
        {
            'type': 'harvest_range', 'name': '수확',
            'value': 1400,
            'max_period': 10,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]
    doy_hyperparams = [
        {
            'type': 'tasselling_range', 'name': '출웅',
            'ref': ['silking_range', 'silking_range'],
            'index': [0, 1],
            'value': [-7, -6],
            'expose_to': [],
        },
        {
            'type': 'fertilize_range', 'name': '기비',
            'ref': ['sow', 'sow'],
            'value': [-30, -15],
            'text': '',
            'expose_to': ['schedules']
        },
        {
            'type': 'fertilize_range', 'name': '추비 1차',
            'ref': ['sow', 'sow'],
            'value': [30, 40],
            'text': '잎이 7~8장, 키가 성인 무릎정도 자랐을 때',
            'expose_to': ['schedules']
        },
        {
            'type': 'fertilize', 'name': '추비 2차',
            'ref': ['sow'],
            'value': [70],
            'text': '옥수수 수꽃이 나왔을 때',
            'expose_to': ['schedules']
        },
    ]
    warning_hyperparams = [
        {
            'method': 'temperature_and_exposure',
            'high_extrema_temperature': 45,
            'high_extrema_exposure_days': 5,
            'low_extrema_temperature': 10,
            'low_extrema_exposure_days': 30
        },
        {
            'method': 'milestone_and_temperature_condition',
            'milestone': {
                'ref': ['tasselling_range', 'tasselling_range'],
                'index': [0, 1],
                'value': [0, 0]
            },
            'condition': {
                'variable': 'tmax',
                'temperature': 35,
                'operator': 'gt'
            },
            'warning_data': {
                'title': '수확량 감소',
                'type': '임실률 감소 주의',
                'message': """
                    출웅기 중 35℃ 초과 온도에 노출되었습니다.
                    임실률이 감소할 수 있습니다."""
            }
        },
    ]
