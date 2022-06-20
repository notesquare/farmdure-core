from .base import BaseCropModel


class CornModel(BaseCropModel):
    name = '옥수수'
    _type = 'corn'
    color = '#fed55c'
    key = 'corn'

    # 기본값
    default_start_doy = 96  # 파종

    # 재배관련 - parameter
    base_temperature = 10
    max_dev_temperature = 45
    allow_multiple_cropping = True

    # 재배관련 - hyperparameter
    silking_gdd = 1049  # 출사
    growth_gdd = 1747  # 생육 완료
    harvest_gdd = 1747  # 수확

    # 재배관련 - warnings
    # 1. 한계온도 & 노출일수
    high_extrema_temperature = 45
    high_extrema_exposure_days = 5
    low_extrema_temperature = 10
    low_extrema_exposure_days = 30

    # 2. 고온 장해: 출웅기(출사전 6~7 일) 최고기온 35°C 초과 임실률 감소

    @property
    def events(self):
        ret = super().events

        # events 계산
        start_doy = self.start_doy  # 파종기
        silking = self.get_event_end_doy(start_doy, self.silking_gdd)  # 출사(암술)
        silking_range = [silking - 5, silking + 9]
        tasselling_range = [
            silking_range[0] - 7, silking_range[1] - 6
        ]  # 출웅(수술)
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)  # 수확
        harvest_range = [harvest - 3, harvest + 7]

        dedicated_events = [
            {'type': 'sow', 'name': '파종', 'data': start_doy},
            {'type': 'silking_range', 'name': '출사', 'data': silking_range},
            {'type': 'harvest_range', 'name': '수확', 'data': harvest_range},
            {
                'type': 'tasselling_range', 'name': '출웅',
                'data': tasselling_range, 'hidden': True
            },
        ]
        ret.extend(dedicated_events)
        return ret

    @property
    def schedules(self):
        ret = super().schedules

        # schedules 계산
        start_doy = self.start_doy  # 파종기
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)  # 수확
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

        start_doy = self.start_doy

        df = self.gdd_weather_df.copy()
        silking = self.get_event_end_doy(start_doy, self.silking_gdd)  # 출사(암술)
        silking_range = [silking - 5, silking + 9]
        tasselling_range = [
            max(start_doy, silking_range[0] - 7),
            silking_range[1] - 6
        ]  # 출웅(수술)

        # 최고기온 35도 초과에서 임실률 감소
        danger_temperature = 35
        ripening_reduced = \
            (df.loc[tasselling_range[0]: tasselling_range[1],
                    'tmax'] > danger_temperature).sum() > 0

        if ripening_reduced:
            ret.append({
                'title': '수확량 감소',
                'type': '임실률 감소 주의',
                'ref': f"""
                    출웅기 중 {danger_temperature}℃ 초과 온도에 노출되었습니다.
                    임실률이 감소할 수 있습니다."""
            })

        return ret
