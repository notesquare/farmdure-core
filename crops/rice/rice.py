from ..base import BaseCropModel


class RiceModel(BaseCropModel):
    name = '벼'
    _type = 'rice'
    color = '#d77c29'
    gdd_method = 'm3'

    max_dev_temperature = 40

    @property
    def environments(self):
        ret = super().environments

        # 안전 출수기
        # 출수기 이후 40 일 평균기온 21~24 도 사이 22.5 도가 최적 출수기
        # 범위에서 벗어나 1 도 차이마다 10%씩 수량감소
        window_size = 40
        df = self.gdd_weather_df.copy()
        df['40days_tavg'] = df.rolling(window_size + 1)\
                              .agg({'tavg': 'mean'})\
                              .shift(-window_size)['tavg']
        df['heading_t_diff1'] = (df['40days_tavg'] - 21).abs()
        df['heading_t_diff2'] = (df['40days_tavg'] - 24).abs()
        df['safe_heading_prob'] = \
            1 - (
                    df[['heading_t_diff1', 'heading_t_diff2']]
                    .min(axis=1) * 0.1
                ).clip(upper=1)
        df['safe_heading_prob'] = df['safe_heading_prob'].round(2)

        _df = df[['safe_heading_prob']].iloc[:366]
        # days, for every period safe heading probability is averaged
        period = 10
        prob_df = _df.groupby((_df.index - 1) // period + 1).mean()
        prob_df = prob_df.round(2)

        data = []
        for k, v in prob_df['safe_heading_prob'].to_dict().items():
            data.append({
                'doy_range': (k*period - period + 1, min(k*period, 366)),
                'prob': v
            })

        ret.append({
                'type': 'positive',
                'name': '안전출수',
                'data': data,
                'ref': 'heading_gdd_range'
            })

        return ret

    @property
    def warnings(self):
        ret = super().warnings

        # 1. 한계온도 & 노출일수
        # 생육한계 최고온도 & 노출일수
        # df = self.gdd_weather_df
        # df['high_extrema_exposure'] = df['tmax'] \
        #     > self.high_extrema_temperature
        # df['high_extrema_exposure_group'] = df['high_extrema_exposure']\
        #     .diff(1).cumsum()

        # high_extrema_exposure_doy_ranges = []
        # for idx, group in df.groupby('high_extrema_exposure_group'):
        #     high_extrema_col = group['high_extrema_exposure']

        #     if high_extrema_col.all() \
        #        and high_extrema_col.count() > self.high_extrema_exposure_days:

        #         high_extrema_exposure_doy_ranges.append(
        #             [group.index[0], group.index[-1]]
        #         )

        # # 생육한계 최저온도 & 노출일수
        # df['low_extrema_exposure'] = df['tmin'] < self.low_extrema_temperature
        # df['low_extrema_exposure_group'] = df['low_extrema_exposure'].diff(1)\
        #     .cumsum()

        # low_extrema_exposure_doy_ranges = []
        # for idx, group in df.groupby('low_extrema_exposure_group'):
        #     low_extrema_col = group['low_extrema_exposure']

        #     if (
        #         low_extrema_col.all() and
        #         low_extrema_col.count() > self.low_extrema_exposure_days
        #     ):

        #         low_extrema_exposure_doy_ranges.append(
        #             [group.index[0], group.index[-1]]
        #         )

        # start_doy = self.start_doy
        # end_doy = self.end_doy
        # for low_extrema_doy_range in low_extrema_exposure_doy_ranges:
        #     is_intersected = min(end_doy, low_extrema_doy_range[1]) > \
        #         max(start_doy, low_extrema_doy_range[0])
        #     if is_intersected:
        #         ret.append({
        #             'title': '⚠️ 재배가능성 낮음',
        #             'message': (
        #                 f'생육한계 최저온도 {self.low_extrema_temperature}℃ 미만의 온도에 '
        #                 f'연속 {self.low_extrema_exposure_days}일 초과하여 노출되었습니다.'
        #             )
        #         })
        #         break
        # for high_extrema_doy_range in high_extrema_exposure_doy_ranges:
        #     is_intersected = min(end_doy, high_extrema_doy_range[1]) > \
        #         max(start_doy, high_extrema_doy_range[0])
        #     if is_intersected:
        #         ret.append({
        #             'title': '⚠️ 재배가능성 낮음',
        #             'message': (
        #                 f'생육한계 최고온도 {self.high_extrema_temperature}℃ 초과의 온도에 '
        #                 f'연속 {self.high_extrema_exposure_days}일 초과하여 노출되었습니다.'
        #             )
        #         })
        #         break

        # 2. 수확은 정식에서부터 45~75일 사이에 위치
        start_doy = self.start_doy  # 정식기

        if hasattr(self, 'harvest_gdd'):
            harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
            harvest_range = [harvest - 3, harvest + 7]
        elif hasattr(self, 'harvest_gdd_range'):
            harvest_range = [
                self.get_event_end_doy(start_doy, gdd)
                for gdd in self.harvest_gdd_range
            ]
            if (
                harvest_range[1] - harvest_range[0]
                    > self.harvest_max_doy_range):
                harvest_range[1] = harvest_range[0] \
                    + self.harvest_max_doy_range

        harvestable_range = [start_doy + 45, start_doy + 75]
        is_valid = min(harvest_range[1], harvestable_range[1]) > \
            max(harvest_range[0], harvestable_range[0])

        if is_valid is False:
            ret.append({
                'title': '⚠️ 재배가능성 낮음',
                'message': '수확은 정식에서부터 45~75일 사이에 위치해야 합니다.'
            })
        return ret
