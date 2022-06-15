from .base import BaseCropModel


class GarlicModel(BaseCropModel):
    name = '마늘'
    _type = 'garlic'
    color = '#b67982'
    key = 'garlic'

    # 기본값
    default_start_doy = 269

    # 재배관련 - parameter
    base_temperature = 7.1
    max_dev_temperature = 25

    # 재배관련 - hyperparameter
    growth_gdd = 1000  # 생육 완료
    harvest_gdd = 1000  # 수확

    # 재배관련 - environments
    # TODO:
    # 고온 피해: 쪽 분화 ~ 수확전 최고기온 25°C 이상에서 생육정지
    # 쪽분화 1월 21일 ~ 3월 21일

    @property
    def events(self):
        ret = super().events

        # events 계산
        start_doy = self.start_doy  # 파종기
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]
        garlic_develop_range = [
            max(start_doy, harvest_range[0] - 120),
            max(start_doy, harvest_range[0] - 120) + 60
        ]

        dedicated_events = [
            {'type': 'sow', 'name': '파종', 'data': start_doy},
            {'type': 'harvest_range', 'name': '수확', 'data': harvest_range},
            {
                'type': 'garlic_develop_range', 'name': '쪽분화기',
                'data': garlic_develop_range, 'hidden': True
            }
        ]
        ret.extend(dedicated_events)
        return ret

    @property
    def environments(self):
        ret = super().environments

        df = self.gdd_weather_df.copy()

        period = 10  # 10일 마다 고온장해 확률값을 나타내는 대표값을 계산

        df['develop_stopped'] = 0

        # 최고기온 25도 이상에서 마늘 생육정지
        df.loc[df['tmax'] >= 25, 'develop_stopped'] = 1
        prob_df = df.groupby((df.index - 1) // period + 1)\
                    .agg({'develop_stopped': 'mean'})  # 10일 동안 비대정지 확률값 계산

        data = []
        for k, v in prob_df['develop_stopped'].to_dict().items():
            data.append({
                'doy_range': (k*period - period + 1, min(k*period, 366)),
                'prob': v
            })

        ret.append({
            'type': 'negative',
            'name': '생육정지',
            'data': data,
            'ref': 'garlic_develop_range'
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
