from .base import BaseCropModel


class PotatoModel(BaseCropModel):
    name = '감자'
    _type = 'potato'
    color = '#ca934f'
    key = 'potato'

    # 기본값
    default_start_doy = 65  # 파종

    # 재배관련 - parameter
    base_temperature = 4.5
    max_dev_temperature = 35

    # 재배관련 - hyperparameter
    transplant_gdd_range = [55, 110]  # 정식
    growth_gdd = 875  # 생육 완료
    harvest_gdd = 875  # 수확

    # 재배관련 - warnings
    high_extrema_temperature = 35
    high_extrema_exposure_days = 5
    low_extrema_temperature = 0
    low_extrema_exposure_days = 30

    # 고온피해: 덩이줄기 비대기(정식 30 일 후~수확 10 일전) 최고기온 27~30°C 덩이줄기 비대 정지

    # 한계값
    transplant_max_doy_range = 20

    @property
    def events(self):
        ret = super().events

        start_doy = self.start_doy  # 파종기
        transplant_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.transplant_gdd_range
        ]
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]

        # 한계값으로 clipping
        if transplant_range[1] - transplant_range[0] \
                > self.transplant_max_doy_range:
            transplant_range[1] = transplant_range[0] \
                + self.transplant_max_doy_range

        dedicated_events = [
            {'type': 'sow', 'name': '파종', 'data': start_doy},
            {
                'type': 'transplant_range', 'name': '정식',
                'data': transplant_range
            },
            {'type': 'harvest_range', 'name': '수확', 'data': harvest_range}
        ]
        ret.extend(dedicated_events)
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
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]

        # 한계값으로 clipping
        if transplant_range[1] - transplant_range[0] \
                > self.transplant_max_doy_range:
            transplant_range[1] = transplant_range[0] \
                + self.transplant_max_doy_range

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

    @property
    def warnings(self):
        ret = super().warnings

        df = self.gdd_weather_df.copy()

        start_doy = self.start_doy  # 파종기
        transplant_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.transplant_gdd_range
        ]
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]

        # 줄기덩이 비대기
        potato_growth_start_doy = transplant_range[1] + 30  # 정식 30 일 후
        potato_growth_end_doy = harvest_range[0] - 10  # 수확 10 일전
        potato_growth_range = [
            min(potato_growth_start_doy, potato_growth_end_doy),
            potato_growth_end_doy  # 비대기 ~ 수확까지 최소 10일은 여유가 있도록 함
        ]

        # 한계값으로 clipping
        if transplant_range[1] - transplant_range[0] \
                > self.transplant_max_doy_range:
            transplant_range[1] = transplant_range[0] \
                + self.transplant_max_doy_range

        # 최고기온 27~30도에서 감자 비대정지
        danger_temperature = 30
        growth_stop = \
            (df.loc[potato_growth_range[0]: potato_growth_range[1],
                    'tmax'] >= danger_temperature).sum() > 0
        if growth_stop:
            ret.append({
                    'title': '수확량 감소',
                    'type': '덩이줄기 비대 정지 주의',
                    'message': f"""
                        덩이 줄기 비대기 중
                        {danger_temperature}℃ 이상 온도에 노출되었습니다.
                        덩이줄기 비대가 정지될 수 있습니다."""
                })
        return ret
