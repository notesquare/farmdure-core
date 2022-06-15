from .cabbage import CabbageModel


class AutumnCabbageModel(CabbageModel):
    name = '가을배추'
    _type = 'cabbage'
    color = '#205a1d'
    key = 'autumnCabbage'

    # 기본값
    default_start_doy = 245

    # 재배관련 - parameter
    base_temperature = 5
    max_dev_temperature = 35
    allow_multiple_cropping = False

    # 재배관련 - hyperparameter
    ripening_gdd_range = [505, 725]  # 결구 실제값 [505, 800]
    growth_gdd = 725  # 생육 완료
    harvest_gdd_range = [725, 870]  # 수확

    # 재배관련 - environments
    freezing_temperature = -3

    # 재배관련 - warnings

    # 한계값
    ripening_max_doy_range = 30
    harvest_max_doy_range = 30

    @property
    def events(self):
        ret = super().events

        # events 계산
        start_doy = self.start_doy  # 정식기
        ripening_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.ripening_gdd_range
        ]
        harvest_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.harvest_gdd_range
        ]

        # 한계값으로 clipping
        if ripening_range[1] - ripening_range[0] > self.ripening_max_doy_range:
            ripening_range[1] = ripening_range[0] + self.ripening_max_doy_range
        if harvest_range[1] - harvest_range[0] > self.harvest_max_doy_range:
            harvest_range[1] = harvest_range[0] + self.harvest_max_doy_range

        dedicated_events = [
            {'type': 'sow', 'name': '파종', 'data': start_doy - 30},  # 정식 30일 전
            {'type': 'transplant', 'name': '정식', 'data': start_doy},
            {'type': 'ripening_range', 'name': '결구', 'data': ripening_range},
            {'type': 'harvest_range', 'name': '수확', 'data': harvest_range}
        ]
        ret.extend(dedicated_events)
        return ret

    @property
    def schedules(self):
        ret = super().schedules

        # events 계산
        start_doy = self.start_doy  # 정식기
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
                'data': start_doy - 30,
                'text': ''
            },
            {
                'type': 'transplant',
                'name': '정식',
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
