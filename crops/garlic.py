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

    # 재배관련 - warnings
    high_extrema_temperature = 25
    high_extrema_exposure_days = 5
    low_extrema_temperature = 10
    low_extrema_exposure_days = 30

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

        start_doy = self.start_doy  # 파종기
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]
        garlic_develop_range = [
            max(start_doy, harvest_range[0] - 120),
            max(start_doy, harvest_range[0] - 120) + 60
        ]

        danger_temperature = 25
        develop_stopped = \
            (df.loc[garlic_develop_range[0]: garlic_develop_range[1],
                    'tmax'] >= danger_temperature).sum() > 0

        if develop_stopped:
            ret.append({
                'title': '수확량 감소',
                'type': '생육 정지 주의',
                'message': f'족 분화 ~ 수확 전 {danger_temperature}℃ 이상에서 생육이 정지됨'
            })

        return ret
