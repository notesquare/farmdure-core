from .rice import RiceModel


class MiddleMatureRiceModel(RiceModel):
    name = '중생종 벼'
    _type = 'rice'
    key = 'middleMatureRice'
    display_order = 1

    # 기본값
    default_start_doy = 148

    # 재배관련 - parameter
    base_temperature = 7

    # 재배관련 - hyperparameter
    heading_gdd_range = [1330, 1510]  # 출수
    growth_gdd = 2550  # 생육 완료
    harvest_gdd_range = [2500, 2600]  # 수확

    # 한계값
    heading_max_doy_range = 20
    harvest_max_doy_range = 20

    @property
    def events(self):
        ret = super().events

        # events 계산
        start_doy = self.start_doy  # 이앙기
        heading_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.heading_gdd_range
        ]
        harvest_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.harvest_gdd_range
        ]

        # 한계값으로 clipping
        if heading_range[1] - heading_range[0] > self.heading_max_doy_range:
            heading_range[1] = heading_range[0] + self.heading_max_doy_range
        if harvest_range[1] - harvest_range[0] > self.harvest_max_doy_range:
            harvest_range[1] = harvest_range[0] + self.harvest_max_doy_range

        dedicated_events = [
            {'type': 'sow', 'name': '파종', 'data': start_doy - 25},  # 이앙 25일 전
            {'type': 'transplant', 'name': '이앙', 'data': start_doy},
            {'type': 'heading_gdd_range', 'name': '출수', 'data': heading_range},
            {'type': 'harvest_range', 'name': '수확', 'data': harvest_range}
        ]
        ret.extend(dedicated_events)
        return ret

    @property
    def schedules(self):
        ret = super().schedules

        # schedules 계산
        start_doy = self.start_doy  # 이앙기
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
                'data': start_doy - 25,
                'text': ''
            },
            {
                'type': 'transplant',
                'name': '이앙',
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
