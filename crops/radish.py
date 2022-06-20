from .base import BaseCropModel


class RadishModel(BaseCropModel):
    name = '무'
    _type = 'radish'
    color = '#5f5442'
    key = 'radish'

    # 기본값
    default_start_doy = 30  # 파종

    # 재배관련 - parameter
    base_temperature = 5
    max_dev_temperature = 35

    # 재배관련 - hyperparameter
    growth_gdd = 850  # 생육 완료
    harvest_gdd = 850  # 수확

    # 재배관련 - warnings
    high_extrema_temperature = 35
    high_extrema_exposure_days = 5
    low_extrema_temperature = 4
    low_extrema_exposure_days = 5

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
