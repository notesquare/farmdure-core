from .base import BaseCropModel


class SesameModel(BaseCropModel):
    name = '참깨'
    _type = 'sesame'
    color = '#a27d5a'
    key = 'sesame'

    # 기본값
    default_start_doy = 126  # 파종

    # 재배관련 - parameter
    base_temperature = 0
    max_dev_temperature = 30
    growth_gdd = 1572

    # 재배관련 - hyperparameter
    first_priority_hyperparams = [
        {
            'method': 'GDD',
            'type': 'bloom_range',
            'value': [410, 1110],
            'max_period': 40
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
            'type': 'bloom_range', 'name': '개화',
            'value': [410, 1110],
            'max_period': 40,
            'text': '',
            'expose_to': ['events']
        },
        {
            'type': 'harvest_range', 'name': '수확',
            'value': 1572,
            'max_period': 10,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]
    doy_hyperparams = []
    warning_hyperparams = [
        {
            'method': 'temperature_and_exposure',
            'high_extrema_temperature': 30,
            'high_extrema_exposure_days': 5,
            'low_extrema_temperature': 18,
            'low_extrema_exposure_days': 30,
        },
        {
            'method': 'milestone_and_temperature_condition',
            'milestone': {
                'ref': ['bloom_range', 'bloom_range'],
                'index': [0, 1],
                'value': [0, 0]
            },
            'condition': {
                'variable': 'tmax',
                'temperature': 40,
                'operator': 'ge'
            },
            'warning_data': {
                'title': '수확량 감소',
                'type': '조기낙화 주의',
                'message': """
                    개화기 중 40℃ 이상에 노출되었습니다.
                    등숙률이 저하될 수 있습니다."""
            }
        },
    ]
