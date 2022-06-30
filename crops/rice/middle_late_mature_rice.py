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

    @property
    def water_level(self):
        start_doy = self.start_doy
        heading = self.get_event_end_doy(start_doy, self.heading_gdd)
        heading_range = [
            max(start_doy, heading - 5), heading + 9
        ]
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]

        irrigation_repeat_start = heading_range[1] + 10
        irrigation_repeat_end = harvest_range[0] - 7

        ripening_water_doys1 = range(
            irrigation_repeat_start,
            irrigation_repeat_end+1, 3
        )
        ripening_water_doys2 = range(
            irrigation_repeat_start+3,
            irrigation_repeat_end+3+1, 3
        )
        ripening_water_doys = []
        for d1, d2 in zip(
            ripening_water_doys1,
            ripening_water_doys2
        ):
            if (d1 >= irrigation_repeat_end or
                    d2 >= irrigation_repeat_end):
                break
            ripening_water_doys.extend([d1, d2])
        ripening_water_levels = [2, 0] * len(ripening_water_doys)
        data = [
            {
                'doyRange': [start_doy - 5, start_doy],
                'name': '이앙전 물대기', 'waterLevels': [5, 5]
            },
            {
                'doyRange': [start_doy, start_doy + 3],
                'name': '이앙기', 'waterLevels': [2, 2]
            },
            {
                'doyRange': [start_doy + 3, start_doy + 8],
                'name': '활착기', 'waterLevels': [7, 7]
            },
            {
                'doyRange': [start_doy + 8, start_doy + 16],
                'name': '분얼성기', 'waterLevels': [2, 2]
            },
            {
                'doyRange': [start_doy + 16, heading_range[0] - 30],
                'name': '중간물떼기', 'waterLevels': [0, 0]
            },
            {
                'doyRange': [heading_range[0] - 30, heading_range[0]],
                'name': '배동받이때(유수형성기)', 'waterLevels': [2, 2]
            },
            {
                'doyRange': [heading_range[0], heading_range[1] + 10],
                'name': '출수기', 'waterLevels': [7, 7]
            },
            {
                'doyRange': ripening_water_doys,
                'name': '등숙기', 'waterLevels': ripening_water_levels
            },
            {
                'doyRange': [harvest_range[0] - 7, harvest_range[0]],
                'name': '완전물떼기', 'waterLevels': [2, 0]
            },
        ]

        ret = []
        for datum in data:
            doys = datum.get('doyRange')
            levs = datum.get('waterLevels')
            ret.extend([
                {'doy': doy, 'waterLevel': level}
                for doy, level in zip(doys, levs)
            ])
        return ret
