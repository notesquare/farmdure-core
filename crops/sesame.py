from .base import BaseCropModel


class SesameModel(BaseCropModel):
    name = '참깨'
    _type = 'sesame'
    color = '#a27d5a'
    key = 'sesame'

    # 기본값
    default_start_doy = 126  # 파종

    # 재배관련 - parameter
    base_temperature = 0
    max_dev_temperature = 30

    # 재배관련 - hyperparameter
    bloom_gdd_range = [410, 1110]  # 개화
    growth_gdd = 1572
    harvest_gdd = 1572  # 수확

    # 재배관련 - environments
    # TODO
    # TODO: 고온피해: 개화기 40°C 이상 고온 조기낙화 등숙률 저하
    burning_temperature = 40

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
    def environments(self):
        ret = super().environments

        df = self.gdd_weather_df.copy()

        period = 10  # 10일 마다 고온장해 확률값을 나타내는 대표값을 계산

        df['premature_abscission'] = 0

        # 최고기온 40도 이상에서 참깨 조기낙화
        df.loc[df['tmax'] >= 40, 'premature_abscission'] = 1

        # 10일 동안 비대정지 확률값 계산
        prob_df = df.groupby((df.index - 1) // period + 1)\
                    .agg({'premature_abscission': 'mean'})

        data = []
        for k, v in prob_df['premature_abscission'].to_dict().items():
            data.append({
                'doy_range': (k*period - period + 1, min(k*period, 366)),
                'prob': v
            })

        ret.append({
            'type': 'negative',
            'name': '조기낙화',
            'data': data,
            'ref': 'bloom_range'
        })

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
