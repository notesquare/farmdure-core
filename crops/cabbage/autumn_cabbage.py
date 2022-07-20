from .cabbage import CabbageModel


class AutumnCabbageModel(CabbageModel):
    name = '가을배추'
    color = '#205a1d'
    key = 'autumnCabbage'

    # 기본값
    default_start_doy = 245

    # 재배관련 - parameter
    base_temperature = 5
    max_dev_temperature = 35
    growth_gdd = 725  # 생육 완료
    allow_multiple_cropping = False

    # 재배관련 - hyperparameter
    _first_priority_hyperparams = [
        {
            'method': 'GDD',
            'type': 'transplant',
            'value': 0
        },
        {
            'method': 'GDD',
            'type': 'harvest_range',
            'value': 601,
            'max_period': 10,
        },
    ]
    _gdd_hyperparams = [
        {
            'type': 'transplant', 'name': '정식',
            'value': 0,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
        {
            'type': 'ripening_range', 'name': '결구',
            'value': [505, 725],  # 결구 실제값 [505, 800]
            'text': '',
            'max_period': 30,
            'expose_to': ['events']
        },
        {
            'type': 'harvest_range', 'name': '수확',
            'value': [725, 870],
            'max_period': 30,
            'text': '',
            'expose_to': ['events', 'schedules']
        },
    ]
    _doy_hyperparams = [
        {
            'type': 'sow', 'name': '파종',
            'ref': ['transplant'],
            'value': [-30],
            'text': '',
            'expose_to': ['events', 'schedules']
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
