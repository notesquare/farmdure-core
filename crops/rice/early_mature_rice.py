from .rice import RiceModel


class EarlyMatureRiceModel(RiceModel):
    name = '조생종 벼'
    _type = 'rice'
    key = 'earlyMatureRice'

    # 기본값
    default_start_doy = 161

    # 재배관련 - parameter
    base_temperature = 6
    growth_gdd = 2400  # 생육 완료

    # 재배관련 - hyperparameter
    _first_priority_hyperparams = [
        {
            'method': 'GDD',
            'type': 'transplant',
            'value': 0
        },
        {
            'method': 'GDD',
            'type': 'heading_range',
            'value': [1000, 1200],
            'max_period': 20
        },
        {
            'method': 'GDD',
            'type': 'harvest_range',
            'value': [2400, 2550],
            'max_period': 20
        },
    ]
    _gdd_hyperparams = [
        {
            'type': 'transplant', 'name': '이앙',
            'value': 0,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
        {
            'type': 'heading_range', 'name': '출수',
            'value': [1000, 1200],
            'max_period': 20,
            'text': '',
            'expose_to': ['events']
        },
        {
            'type': 'harvest_range', 'name': '수확',
            'value': [2400, 2550],
            'max_period': 20,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]
    _doy_hyperparams = [
        {
            'type': 'sow', 'name': '파종',
            'ref': ['transplant'],
            'value': [-25],
            'text': '',
            'expose_to': ['events', 'schedules']
        },
        {
            'type': 'fertilize_range', 'name': '기비',
            'ref': ['transplant', 'transplant'],
            'value': [-5, -4],
            'text': '인산 비료의 경우 기비시 전량 시비합니다',
            'expose_to': ['schedules']
        },
        {
            'type': 'fertilize', 'name': '분얼비',
            'ref': ['transplant'],
            'value': [12],
            'text': """
                    기비와 수비의 비율을 7:3으로 할 경우,
                    분얼비는 생략가능합니다.
                """,
            'expose_to': ['schedules']
        },
        {
            'type': 'fertilize_range', 'name': '수비',
            'ref': ['heading_range', 'heading_range'],
            'value': [-25, -25],
            'index': [0, 1],
            'text': '',
            'expose_to': ['schedules']
        },
        # water level data below
        {
            'type': 'irragation_range', 'name': '이앙전 물대기',
            'ref': ['transplant', 'transplant'],
            'value': [-5, 0],
            'water_level': [5, 5],
            'expose_to': ['water_level']
        },
        {
            'type': 'irragation_range', 'name': '이앙기',
            'ref': ['transplant', 'transplant'],
            'value': [0, 3],
            'water_level': [2, 2],
            'expose_to': ['water_level']
        },
        {
            'type': 'irragation_range', 'name': '활착기',
            'ref': ['transplant', 'transplant'],
            'value': [3, 7],
            'water_level': [7, 7],
            'expose_to': ['water_level']
        },
        {
            'type': 'irragation_range', 'name': '분얼성기',
            'ref': ['transplant', 'transplant'],
            'value': [7, 12],
            'water_level': [2, 2],
            'expose_to': ['water_level']
        },
        {
            'type': 'irragation_range', 'name': '중간물떼기',
            'ref': ['transplant', 'heading_range'],
            'value': [12, -20],
            'index': [None, 0],
            'water_level': [0, 0],
            'expose_to': ['water_level']
        },
        {
            'type': 'irragation_range', 'name': '배동받이때(유수형성기)',
            'ref': ['heading_range', 'heading_range'],
            'value': [-20, 0],
            'index': [0, 0],
            'water_level': [2, 2],
            'expose_to': ['water_level']
        },
        {
            'type': 'irragation_range', 'name': '출수기',
            'ref': ['heading_range', 'heading_range'],
            'value': [0, 10],
            'index': [0, 1],
            'water_level': [7, 7],
            'expose_to': ['water_level']
        },
        {
            'type': 'irragation_range', 'name': '등숙기',
            'ref': ['heading_range', 'harvest_range'],
            'value': [10, -7],
            'index': [1, 0],
            'water_level': [2, 0],
            'period': 3,
            'expose_to': ['water_level']
        },
        {
            'type': 'irragation_range', 'name': '완전물떼기',
            'ref': ['harvest_range', 'harvest_range'],
            'value': [-7, 0],
            'index': [0, 0],
            'water_level': [2, 0],
            'expose_to': ['water_level']
        },
    ]

    _warning_hyperparams = []

    @property
    def first_priority_hyperparams(self):
        return super().first_priority_hyperparams \
            + self._first_priority_hyperparams

    @property
    def gdd_hyperparams(self):
        return super().gdd_hyperparams + self._gdd_hyperparams

    @property
    def doy_hyperparams(self):
        return super().doy_hyperparams + self._doy_hyperparams

    @property
    def warning_hyperparams(self):
        return super().warning_hyperparams + self._warning_hyperparams
