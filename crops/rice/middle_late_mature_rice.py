from .rice import RiceModel


class MiddleLateMatureRiceModel(RiceModel):
    name = '중만생종 벼'
    _type = 'rice'
    key = 'middleLateMatureRice'

    # 기본값
    default_start_doy = 165  # 이앙

    # 재배관련 - parameter
    base_temperature = 8

    # 재배관련 - hyperparameter
    fertilize_gdd_range = [625, 1215]  # 수비
    heading_gdd = 1404  # 출수
    growth_gdd = 1935  # 생육 완료
    harvest_gdd = 2111  # 수확

    @property
    def events(self):
        ret = super().events

        # events 계산
        start_doy = self.start_doy  # 이앙기
        heading = self.get_event_end_doy(start_doy, self.heading_gdd)
        heading_range = [heading - 5, heading + 9]
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]
        fertilize_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.fertilize_gdd_range
        ]

        dedicated_events = [
            {'type': 'sow', 'name': '파종', 'data': start_doy - 25},  # 이앙 25일 전
            {'type': 'transplant', 'name': '이앙', 'data': start_doy},
            {'type': 'heading_gdd_range', 'name': '출수', 'data': heading_range},
            {'type': 'harvest_range', 'name': '수확', 'data': harvest_range},
            {'type': 'fertilize_range', 'name': '수비', 'data': fertilize_range}
        ]
        ret.extend(dedicated_events)
        return ret

    @property
    def schedules(self):
        ret = super().schedules

        # schedules 계산
        start_doy = self.start_doy  # 이앙기
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]
        fertilize_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.fertilize_gdd_range
        ]

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
                'type': 'fertilize_range',
                'name': '수비',
                'data': fertilize_range,
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
