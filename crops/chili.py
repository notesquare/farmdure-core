from .base import BaseCropModel


class ChiliModel(BaseCropModel):
    name = '고추'
    _type = 'chili'
    color = '#da2128'
    key = 'chili'

    # 기본값
    default_start_doy = 106  # 정식

    # 재배관련 - parameter
    base_temperature = 5
    max_dev_temperature = 35

    # 재배관련 - hyperparameter
    bloom_gdd_range = [150, 1950]  # 개화
    green_chili_harvest_gdd_range = [550, 1070]  # 풋고추 수확
    growth_gdd = 1000  # 생육 완료
    red_chili_harvest_gdd_range = [1085, 2730]  # 붉은 고추 수확

    # 재배관련 - environments
    # 고온 장해: 개화전 13~17 일 평균기온 30°C 이상에서 이상화분 발생
    doy_range_before_bloom = [13, 17]

    # 한계값
    green_chili_harvest_max_doy_range = 30
    red_chili_harvest_max_doy_range = 80

    @property
    def events(self):
        ret = super().events

        # events 계산
        start_doy = self.start_doy  # 정식기
        bloom_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.bloom_gdd_range
        ]
        before_bloom_range = [
            bloom_range[0] - self.doy_range_before_bloom[1],
            bloom_range[1] - self.doy_range_before_bloom[0]
        ]
        green_chili_harvest_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.green_chili_harvest_gdd_range
        ]
        red_chili_harvest_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.red_chili_harvest_gdd_range
        ]

        # 한계값으로 clipping
        if green_chili_harvest_range[1] - green_chili_harvest_range[0] \
                > self.green_chili_harvest_max_doy_range:
            green_chili_harvest_range[1] = green_chili_harvest_range[0] \
                + self.green_chili_harvest_max_doy_range
        if red_chili_harvest_range[1] - red_chili_harvest_range[0] \
                > self.red_chili_harvest_max_doy_range:
            red_chili_harvest_range[1] = red_chili_harvest_range[0] \
                + self.red_chili_harvest_max_doy_range

        dedicated_events = [
            {'type': 'sow', 'name': '파종', 'data': start_doy - 65},
            {'type': 'transplant', 'name': '아주심기', 'data': start_doy},
            {
                'type': 'harvest_range', 'name': '풋고추 수확',
                'data': green_chili_harvest_range
            },
            {
                'type': 'harvest_range', 'name': '붉은고추 수확',
                'data': red_chili_harvest_range
            },
            {
                'type': 'before_bloom_range', 'name': '',
                'data': before_bloom_range, 'hidden': True
            },
        ]
        ret.extend(dedicated_events)
        return ret

    @property
    def environments(self):
        ret = super().environments

        # 고온 장해: 개화전 13~17 일 평균기온 30°C 이상에서 이상화분 발생
        df = self.gdd_weather_df.copy()
        period = 10  # 10일 마다 고온장해 확률값을 나타내는 대표값을 계산
        df['pollen_damaged'] = 0
        df.loc[df['tavg'] >= 30, 'pollen_damaged'] = 1  # 평균기온 30도 이상에서 이상화분
        prob_df = df.groupby((df.index - 1) // period + 1)\
                    .agg({'pollen_damaged': 'mean'})  # 10일 동안 이상화분 확률값 계산

        data = []
        for k, v in prob_df['pollen_damaged'].to_dict().items():
            data.append({
                'doy_range': (k*period - period + 1, min(k*period, 366)),
                'prob': v
            })

        ret.append({
            'type': 'negative',
            'name': '이상화분',
            'data': data,
            'ref': 'before_bloom'
        })
        return ret

    @property
    def schedules(self):
        ret = super().schedules

        # schedules 계산
        start_doy = self.start_doy  # 정식기
        green_chili_harvest_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.green_chili_harvest_gdd_range
        ]
        red_chili_harvest_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.red_chili_harvest_gdd_range
        ]
        fertilize_range1 = [
            start_doy + 25, start_doy + 30
        ]  # 정식 25~30 일 후
        fertilize_range2 = [
            fertilize_range1[0] + 25, fertilize_range1[1] + 30
        ]  # 1차 추비 25~30 일 후
        fertilize_range3 = [
            fertilize_range2[0] + 25, fertilize_range2[1] + 30
        ]  # 2차 추비 25~30 일 후

        # 한계값으로 clipping
        if green_chili_harvest_range[1] - green_chili_harvest_range[0] \
                > self.green_chili_harvest_max_doy_range:
            green_chili_harvest_range[1] = green_chili_harvest_range[0] \
                + self.green_chili_harvest_max_doy_range
        if red_chili_harvest_range[1] - red_chili_harvest_range[0] \
                > self.red_chili_harvest_max_doy_range:
            red_chili_harvest_range[1] = red_chili_harvest_range[0] \
                + self.red_chili_harvest_max_doy_range

        ret.extend([
            {
                'type': 'sow',
                'name': '파종',
                'data': start_doy - 65,
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
                'name': '풋고추 수확',
                'data': green_chili_harvest_range,
                'text': ''
            },
            {
                'type': 'harvest_range',
                'name': '붉은고추 수확',
                'data': red_chili_harvest_range,
                'text': ''
            },
            {
                'type': 'fertilize_range',
                'name': '추비 1회',
                'data': fertilize_range1,
                'text': ''
            },
            {
                'type': 'fertilize_range',
                'name': '추비 2회',
                'data': fertilize_range2,
                'text': ''
            },
            {
                'type': 'fertilize_range',
                'name': '추비 3회',
                'data': fertilize_range3,
                'text': ''
            },
        ])
        return ret
