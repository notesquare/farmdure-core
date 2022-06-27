from .rice import RiceModel


class MiddleLateMatureRiceModel(RiceModel):
    name = '중만생종 벼'
    _type = 'rice'
    key = 'middleLateMatureRice'
    display_order = 0

    # 기본값
    default_start_doy = 165  # 이앙

    # 재배관련 - parameter
    base_temperature = 8

    # 재배관련 - hyperparameter
    heading_gdd = 1404  # 출수
    growth_gdd = 2600  # 생육 완료
    harvest_gdd = 2600  # 수확

    @property
    def events(self):
        ret = super().events

        # events 계산
        start_doy = self.start_doy  # 이앙기
        heading = self.get_event_end_doy(start_doy, self.heading_gdd)
        heading_range = [
            max(start_doy, heading - 5), heading + 9
        ]
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]

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
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]

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
