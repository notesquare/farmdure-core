from .base import BaseCropModel


class PotatoModel(BaseCropModel):
    name = '감자'
    _type = 'potato'
    color = '#ca934f'
    key = 'potato'

    # 기본값
    default_start_doy = 65  # 파종

    # 재배관련 - parameter
    base_temperature = 4.5
    max_dev_temperature = 35
    growth_gdd = 875  # 생육 완료

    # 재배관련 - hyperparameter
    first_priority_hyperparams = [
        {
            'method': 'GDD',
            'type': 'transplant_range',
            'value': [55, 110],
            'max_period': 20,
        },
        {
            'method': 'GDD',
            'type': 'harvest_range',
            'value': 875,
            'max_period': 10,
        },
        {
            'method': 'DOY',
            'type': 'potato_growth_range',
            'ref': ['transplant_range', 'harvest_range'],
            'index': [1, 0],
            'value': [30, -10],
        }
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
            'value': [55, 110],
            'max_period': 20,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
        {
            'type': 'harvest_range', 'name': '수확',
            'value': 875,
            'max_period': 10,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]
    doy_hyperparams = [
        {
            'type': 'potato_growth_range', 'name': '덩이줄기 비대기',
            'ref': ['transplant_range', 'harvest_range'],
            'index': [1, 0],
            'value': [30, -10],
            'expose_to': [],
        },
    ]
    warning_hyperparams = [
        {
            'method': 'temperature_and_exposure',
            'high_extrema_temperature': 35,
            'high_extrema_exposure_days': 5,
            'low_extrema_temperature': 0,
            'low_extrema_exposure_days': 30
        },
        {
            'method': 'milestone_and_temperature_condition',
            'milestone': {
                'ref': ['potato_growth_range', 'potato_growth_range'],
                'index': [0, 1],
                'value': [0, 0]
                # TODO: [min(potato_growth_start_doy, potato_growth_end_doy),
                #       potato_growth_end_doy]  # 비대기 ~ 수확까지 최소 10일은 여유가 있도록 함
            },
            'condition': {
                'variable': 'tmax',
                'temperature': 30,
                'operator': 'ge'
            },
            'warning_data': {
                'title': '수확량 감소',
                'type': '덩이줄기 비대 정지 주의',
                'message': """
                    덩이 줄기 비대기 중 30℃ 이상 온도에 노출되었습니다.
                    덩이줄기 비대가 정지될 수 있습니다."""
            }
        },
    ]
