from .base import BaseCropModel


class OnionModel(BaseCropModel):
    name = '양파'
    _type = 'onion'
    color = '#aed477'
    key = 'onion'

    # 기본값
    default_start_doy = 238

    # 재배관련 - parameter
    base_temperature = 4.5
    max_dev_temperature = 25

    # 재배관련 - hyperparameter
    transplant_gdd_range = [790, 1050]  # 정식
    growth_gdd = 2092  # 생육 완료
    harvest_gdd_range = [2092, 2352]  # 수확

    # 재배관련 - warnings
    high_extrema_temperature = 25
    high_extrema_exposure_days = 10
    low_extrema_temperature = 4
    low_extrema_exposure_days = 30

    # 고온 피해: 구비대기 (수확 40일 전) 25°C 이상에서 생육둔화

    # 한계값
    transplant_max_doy_range = 40
    harvest_max_doy_range = 30

    @property
    def events(self):
        ret = super().events

        # events 계산
        start_doy = self.start_doy  # 파종기
        transplant_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.transplant_gdd_range
        ]
        harvest_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.harvest_gdd_range
        ]

        # 한계값으로 clipping
        if transplant_range[1] - transplant_range[0] \
                > self.transplant_max_doy_range:
            transplant_range[1] = transplant_range[0] \
                + self.transplant_max_doy_range
        if harvest_range[1] - harvest_range[0] > self.harvest_max_doy_range:
            harvest_range[1] = harvest_range[0] + self.harvest_max_doy_range

        # clipping된 수확기 기준으로 구비대기 설정
        onion_develop_range = [harvest_range[0] - 40, harvest_range[1] - 40]

        dedicated_events = [
            {'type': 'sow', 'name': '파종', 'data': start_doy},
            {
                'type': 'transplant_range', 'name': '정식',
                'data': transplant_range
            },
            {'type': 'harvest_range', 'name': '수확', 'data': harvest_range},
            {
                'type': 'onion_develop_range', 'name': '구비대기',
                'data': onion_develop_range, 'hidden': True
            }
        ]
        ret.extend(dedicated_events)
        return ret

    @property
    def warnings(self):
        ret = super().warnings

        df = self.gdd_weather_df.copy()

        start_doy = self.start_doy
        harvest_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.harvest_gdd_range
        ]

        # 한계값으로 clipping
        if harvest_range[1] - harvest_range[0] > self.harvest_max_doy_range:
            harvest_range[1] = harvest_range[0] + self.harvest_max_doy_range

        # clipping된 수확기 기준으로 구비대기 설정
        onion_develop_range = [harvest_range[0] - 40, harvest_range[1] - 40]

        danger_temperature = 25
        # 최고기온 25도 초과에서 양파 생육정지
        develop_slowed = \
            (df.loc[onion_develop_range[0]: onion_develop_range[1],
                    'tmax']).sum() > danger_temperature

        if develop_slowed:
            ret.append({
                'title': '수확량 감소',
                'type': ' 생육저하 주의',
                'message': f'구비대기 시기, {danger_temperature}℃ 이상에서 생윤둔화'
            })
        return ret

    @property
    def schedules(self):
        ret = super().schedules

        # schedules 계산
        start_doy = self.start_doy  # 파종기
        transplant_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.transplant_gdd_range
        ]
        harvest_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.harvest_gdd_range
        ]

        # 한계값으로 clipping
        if transplant_range[1] - transplant_range[0] \
                > self.transplant_max_doy_range:
            transplant_range[1] = transplant_range[0] \
                + self.transplant_max_doy_range
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
                'type': 'transplant_range',
                'name': '정식',
                'data': transplant_range,
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
