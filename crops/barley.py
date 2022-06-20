from .base import BaseCropModel


class BarleyModel(BaseCropModel):
    name = '보리'
    _type = 'barley'
    color = '#d0ab4a'
    key = 'barley'

    # 기본값
    default_start_doy = 284  # 파종

    # 재배관련 - parameter
    base_temperature = 0
    max_dev_temperature = 30

    # 재배관련 - hyperparameter
    tillering_gdd_range = [525, 885]  # 분얼 신장
    heading_gdd_range = [896, 1200]  # 출수
    ripening_gdd_range = [1200, 1600]  # 등숙 실제값 [1200, 1800]
    growth_gdd = 1600  # 생육 완료 실제값 1800
    harvest_gdd_range = [1600, 2295]  # 수확

    # 재배관련 - warnings
    high_extrema_temperature = 30
    high_extrema_exposure_days = 5
    low_extrema_temperature = 3
    low_extrema_exposure_days = 15

    # 한계값
    tillering_max_doy_range = 50
    heading_max_doy_range = 30
    ripening_max_doy_range = 40
    harvest_max_doy_range = 40

    @property
    def events(self):
        ret = super().events

        # events 계산
        start_doy = self.start_doy  # 파종기
        tillering_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.tillering_gdd_range
        ]
        heading_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.heading_gdd_range
        ]
        ripening_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.ripening_gdd_range
        ]
        harvest_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.harvest_gdd_range
        ]

        # 한계값으로 clipping
        if tillering_range[1] - tillering_range[0] \
                > self.tillering_max_doy_range:
            tillering_range[1] = tillering_range[0] \
                + self.tillering_max_doy_range
        if heading_range[1] - heading_range[0] > self.heading_max_doy_range:
            heading_range[1] = heading_range[0] + self.heading_max_doy_range
        if ripening_range[1] - ripening_range[0] > self.ripening_max_doy_range:
            ripening_range[1] = ripening_range[0] + self.ripening_max_doy_range
        if harvest_range[1] - harvest_range[0] > self.harvest_max_doy_range:
            harvest_range[1] = harvest_range[0] + self.harvest_max_doy_range

        dedicated_events = [
            {'type': 'sow', 'name': '파종', 'data': start_doy},
            {
                'type': 'tillering_range', 'name': '분얼 및 신장',
                'data': tillering_range
            },
            {'type': 'heading_range', 'name': '출수', 'data': heading_range},
            {'type': 'ripening_range', 'name': '등숙', 'data': ripening_range},
            {'type': 'harvest_range', 'name': '수확', 'data': harvest_range}
        ]
        ret.extend(dedicated_events)
        return ret

    @property
    def schedules(self):
        ret = super().schedules

        # schedules 계산
        start_doy = self.start_doy  # 파종기
        harvest_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.harvest_gdd_range
        ]

        # 한계값으로 clipping
        if harvest_range[1] - harvest_range[0] > self.harvest_max_doy_range:
            harvest_range[1] = harvest_range[0] + self.harvest_max_doy_range

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
