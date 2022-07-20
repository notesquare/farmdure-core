from .base import BaseCropModel


class GarlicModel(BaseCropModel):
    name = '마늘'
    _type = 'garlic'
    color = '#b67982'
    key = 'garlic'

    # 기본값
    default_start_doy = 269

    # 재배관련 - parameter
    base_temperature = 7.1
    max_dev_temperature = 25
    growth_gdd = 1000  # 생육 완료

    # 재배관련 - hyperparameter
    first_priority_hyperparams = [
        {
            'method': 'GDD',
            'type': 'harvest_range',
            'value': 1000,
            'max_period': 10,
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
            'type': 'harvest_range', 'name': '수확',
            'value': 1000,
            'max_period': 10,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]
    doy_hyperparams = []
    warning_hyperparams = [
        {
            'method': 'temperature_and_exposure',
            'high_extrema_temperature': 25,
            'high_extrema_exposure_days': 5,
            'low_extrema_temperature': 10,
            'low_extrema_exposure_days': 30
        },
        {
            'method': 'milestone_and_temperature_condition',
            'milestone': {
                'ref': ['harvest_range', 'harvest_range'],
                'index': [0, 0],
                'value': [-120, 60]
                # TODO: [max(start_doy, harvest_range[0] - 120),
                #        max(start_doy, harvest_range[0] - 120) + 60]
            },
            'condition': {
                'variable': 'tmax',
                'temperature': 25,
                'operator': 'ge'
            },
            'warning_data': {
                'title': '수확량 감소',
                'type': '생육 정지 주의',
                'message': '쪽 분화 ~ 수확 전 25℃ 이상에서 생육이 정지됨'
            }
        },
    ]
