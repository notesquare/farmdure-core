from .base import BaseCropModel


class SesameModel(BaseCropModel):
    name = '참깨'
    _type = 'sesame'
    color = '#a27d5a'
    key = 'sesame'
    division = 'functional'

    # 기본값
    default_start_doy = 126  # 파종

    # 재배관련 - parameter
    base_temperature = 0
    max_dev_temperature = 30

    # 재배관련 - hyperparameter
    bloom_gdd_range = [410, 1110]  # 개화
    growth_gdd = 1572
    harvest_gdd = 1572  # 수확

    # 재배관련 - warnings
    high_extrema_temperature = 30
    high_extrema_exposure_days = 5
    low_extrema_temperature = 18
    low_extrema_exposure_days = 30

    # 고온피해: 개화기 40°C 이상 고온 조기낙화 등숙률 저하

    # 한계값
    bloom_max_doy_range = 40

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

    @property
    def warnings(self):
        ret = super().warnings

        df = self.gdd_weather_df.copy()

        # 최고기온 40도 이상에서 참깨 조기낙화
        danger_temperature = 40
        start_doy = self.start_doy  # 파종기
        bloom_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.bloom_gdd_range
        ]

        # 한계값으로 clipping
        if bloom_range[1] - bloom_range[0] > self.bloom_max_doy_range:
            bloom_range[1] = bloom_range[0] + self.bloom_max_doy_range

        premature_abscission = (df.loc[
            bloom_range[0]: bloom_range[1],
            'tmax'] >= danger_temperature).sum() > 0

        if premature_abscission:
            ret.append({
                'title': '수확량 감소',
                'type': '조기낙화 주의',
                'message': f"""
                    개화기 중 {danger_temperature}℃ 이상에 노출되었습니다.
                    등숙률이 저하될 수 있습니다."""
            })

        return ret
