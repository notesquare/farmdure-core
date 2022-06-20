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

    # 재배관련 - warnings
    doy_range_before_bloom = [13, 17]
    high_extrema_temperature = 40
    high_extrema_exposure_days = 5
    low_extrema_temperature = 10
    low_extrema_exposure_days = 5

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

    @property
    def warnings(self):
        ret = []

        start_doy = self.start_doy
        end_doy = self.end_doy

        # 1. 한계온도 & 노출일수
        # 생육한계 최고온도 & 노출일수
        df = self.gdd_weather_df.copy()
        if hasattr(self, 'high_extrema_temperature'):
            df['high_extrema_exposure'] = \
                df['tmax'] >= self.high_extrema_temperature  # 고추만 초과가 아닌 "이상"
            df['high_extrema_exposure_group'] = \
                df['high_extrema_exposure'].diff(1).cumsum()

            high_extrema_exposure_doy_ranges = []
            for idx, group in df.groupby('high_extrema_exposure_group'):
                high_extrema_col = group['high_extrema_exposure']

                if (high_extrema_col.all() and high_extrema_col.count()
                        >= self.high_extrema_exposure_days):
                    high_extrema_exposure_doy_ranges.append(
                        [group.index[0], group.index[-1]]
                    )
            for high_extrema_doy_range in high_extrema_exposure_doy_ranges:
                is_intersected = min(end_doy, high_extrema_doy_range[1]) \
                    > max(start_doy, high_extrema_doy_range[0])
                if is_intersected:
                    ret.append({
                        'title': '재배가능성 낮음',
                        'type': '고온해 위험',
                        'message': f"""생육한계 최고온도 {
                            self.high_extrema_temperature
                        }℃ 초과의 온도에 연속 {
                            self.high_extrema_exposure_days
                        }일 이상 노출되었습니다."""
                    })
                    break

        # 생육한계 최저온도 & 노출일수
        if hasattr(self, 'low_extrema_temperature'):
            df['low_extrema_exposure'] = \
                df['tmin'] < self.low_extrema_temperature
            df['low_extrema_exposure_group'] = \
                df['low_extrema_exposure'].diff(1).cumsum()

            low_extrema_exposure_doy_ranges = []
            for idx, group in df.groupby('low_extrema_exposure_group'):
                low_extrema_col = group['low_extrema_exposure']

                if (low_extrema_col.all() and low_extrema_col.count()
                        >= self.low_extrema_exposure_days):

                    low_extrema_exposure_doy_ranges.append(
                        [group.index[0], group.index[-1]]
                    )
            for low_extrema_doy_range in low_extrema_exposure_doy_ranges:
                is_intersected = min(end_doy, low_extrema_doy_range[1]) \
                    > max(start_doy, low_extrema_doy_range[0])
                if is_intersected:
                    ret.append({
                        'title': '재배가능성 낮음',
                        'type': '동해 위험',
                        'message': f"""생육한계 최저온도 {
                            self.low_extrema_temperature
                        }℃ 미만의 온도에 연속 {
                            self.low_extrema_exposure_days
                        }일 이상 노출되었습니다."""
                    })
                    break

        # 수확률 감소: 개화전 13~17 일 평균기온 30°C 이상에서 이상화분 발생
        df = self.gdd_weather_df.copy()
        bloom_range = self.bloom_gdd_range

        # 개화전 13~17 일
        start_doy = self.start_doy  # 정식기
        bloom_range = [
            self.get_event_end_doy(start_doy, gdd)
            for gdd in self.bloom_gdd_range
        ]
        before_bloom_range = [
            max(self.start_doy,
                bloom_range[0] - self.doy_range_before_bloom[1]
                ),
            bloom_range[1] - self.doy_range_before_bloom[0]
        ]

        # 평균기온 30°C 이상
        danger_temperature = 30
        pollen_liability = \
            (df.loc[before_bloom_range[0]: before_bloom_range[1],
                    'tavg'] >= danger_temperature).sum() > 0

        if pollen_liability:
            ret.append({
                'title': '수확량 감소',
                'type': '이상화분 발생 주의',
                'message': f"""
                    개화 전 {self.doy_range_before_bloom[0]}~
                    {self.doy_range_before_bloom[1]}일 기간에서
                    {danger_temperature}℃ 이상의 온도에 노출될 경우 화분의 수정능력이 저하됩니다."""
            })

        return ret
