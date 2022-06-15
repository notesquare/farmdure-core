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

    # 재배관련 - environments
    # 고온 장해: 출웅기(출사전 6~7 일) 최고기온 35°C 초과 임실률 감소

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
    def environments(self):
        ret = super().environments

        df = self.gdd_weather_df.copy()

        period = 10  # 10일 마다 고온장해 확률값을 나타내는 대표값을 계산

        df['ripening_reduced'] = 0
        df.loc[df['tmax'] > 35, 'ripening_reduced'] = 1  # 최고기온 35도 초과에서 임실률 감소
        prob_df = df.groupby((df.index - 1) // period + 1)\
                    .agg({'ripening_reduced': 'mean'})  # 10일 동안 임실률감소 확률값 계산

        data = []
        for k, v in prob_df['ripening_reduced'].to_dict().items():
            data.append({
                'doy_range': (k*period - period + 1, min(k*period, 366)),
                'prob': v
            })
        ret.append({
            'type': 'negative',
            'name': '임실감소',
            'data': data,
            'ref': 'tasselling_range'
        })

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
