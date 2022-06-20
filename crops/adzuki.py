from .base import BaseCropModel


class AdzukiModel(BaseCropModel):
    name = '팥'
    _type = 'adzuki'
    color = '#bb7178'
    key = 'adzuki'

    # 기본값
    default_start_doy = 146

    # 재배관련 - parameter
    base_temperature = 5
    max_dev_temperature = 24

    # 재배관련 - hyperparameter
    bloom_gdd_range = [850, 1240]  # 개화
    growth_gdd = 2300  # 생육 완료
    harvest_gdd = 2300  # 수확

    # 재배관련 - warnings
    high_extrema_temperature = 30
    high_extrema_exposure_days = 5
    low_extrema_temperature = 16
    low_extrema_exposure_days = 5

    # 한계값
    bloom_max_doy_range = 20

    @property
    def events(self):
        ret = super().events

        # events 계산
        start_doy = self.start_doy  # 파종기
        bloom_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.bloom_gdd_range
        ]
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]

        # 한계값으로 clipping
        if bloom_range[1] - bloom_range[0] > self.bloom_max_doy_range:
            bloom_range[1] = bloom_range[0] + self.bloom_max_doy_range

        dedicated_events = [
            {'type': 'sow', 'name': '파종', 'data': start_doy},
            {'type': 'bloom_range', 'name': '개화', 'data': bloom_range},
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
