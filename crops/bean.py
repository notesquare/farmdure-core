from .base import BaseCropModel


class BeanModel(BaseCropModel):
    name = '콩'
    _type = 'bean'
    color = '#3aa584'
    key = 'bean'

    # 기본값
    default_start_doy = 172

    # 재배관련 - parameter
    base_temperature = 0
    max_dev_temperature = 35

    # 재배관련 - hyperparameter
    growth_gdd = 2700  # 생육 완료
    harvest_gdd = 2700  # 수확

    # 재배관련 - warnings
    high_extrema_temperature = 35
    high_extrema_exposure_days = 5
    low_extrema_temperature = 20
    low_extrema_exposure_days = 30

    @property
    def events(self):
        ret = super().events

        # events 계산
        start_doy = self.start_doy  # 파종기
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]

        dedicated_events = [
            {'type': 'sow', 'name': '파종', 'data': start_doy},
            {'type': 'harvest_range', 'name': '수확', 'data': harvest_range}
        ]
        ret.extend(dedicated_events)
        return ret

    @property
    def schedules(self):
        ret = super().schedules

        # schedules 계산
        start_doy = self.start_doy  # 파종기
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]

        ret.extend([
            {
                'type': 'sow',
                'name': '파종',
                'data': start_doy,
                'text': ''
            },
            {
                'type': 'harvest_range',
                'name': '수확',
                'data': harvest_range,
                'text': ''
            }
        ])
        return ret
