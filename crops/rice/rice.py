from operator import itemgetter

import polars as pl

from ..base import BaseCropModel


class RiceModel(BaseCropModel):
    name = '벼'
    _type = 'rice'
    color = '#d77c29'

    @property
    def warnings(self):
        ret = super().warnings

        # 안전 출수기
        low_heading_temp = 21
        high_heading_temp = 24

        ref = self.calculate_first_priority_params()
        heading_range = ref.get('heading_range')

        if not isinstance(heading_range, list):
            heading_range = [heading_range] * 2

        win_size = 40
        df = self.weather_df

        heading_df = df.with_columns([
            ((pl.col('tmax') + pl.col('tmin')) * 0.5)
            .rolling_mean(window_size=win_size)
            .shift(-win_size+1)
            .alias('tavg_40days'),

            pl.col('year')
            .rolling_mean(window_size=win_size)
            .shift(-win_size+1)
            .alias('mean_year')
        ])\
            .filter(
                (pl.col('year') == pl.col('mean_year')) &
                (pl.col('doy') >= heading_range[0] % 366 + 1) &
                (pl.col('doy') <= heading_range[1] % 366 + 1)
            )\
            .collect()

        safe_heading_df = heading_df.filter(
            (pl.col('tavg_40days') >= 21) &
            (pl.col('tavg_40days') <= 24)
        )

        if len(heading_df) != 0:
            safe_heading_prob = len(safe_heading_df) / len(heading_df) * 100
            safe_heading_prob = round(safe_heading_prob, 1)
        else:
            safe_heading_prob = None

        if safe_heading_prob is None:
            pass
        elif safe_heading_prob >= 80:
            ret.append({
                'type': '안전 출수',
                'title': '안전 출수기',
                'message': f"""
                    출수기 중 {safe_heading_prob}% 의 날에서 40일 평균기온
                    {low_heading_temp}~{high_heading_temp}℃ 를 만족합니다."""
            })
        elif safe_heading_prob < 50:
            ret.append({
                'type': '출수 위험',
                'title': '안전 출수기',
                'message': f"""
                    출수기 중 {safe_heading_prob}% 의 날에서 40일 평균기온
                    {low_heading_temp}~{high_heading_temp}℃ 를 만족합니다."""
            })
        else:
            ret.append({
                'type': '출수 주의',
                'title': '안전 출수기',
                'message': f"""
                    출수기 중 {safe_heading_prob}% 의 날에서 40일 평균기온
                    {low_heading_temp}~{high_heading_temp}℃ 를 만족합니다."""
            })

        return ret

    @property
    def water_level(self):
        ret = super().water_level

        for param in self.doy_hyperparams:
            if 'water_level' not in param['expose_to']:
                continue
            ref = self.calculate_first_priority_params()

            period = param.get('period')
            if period is None:
                # 일반적인 수위 관리
                doys = self.calculate_doy_hyperparam(param, ref)['doy']
                levs = param['water_level']
            else:
                # 물대기와 물떼기 반복
                _doys = self.calculate_doy_hyperparam(param, ref)['doy']
                _levs = param['water_level']

                _doys1 = range(
                    _doys[0],
                    _doys[1] + 1, period
                )
                _doys2 = range(
                    _doys[0] + period,
                    _doys[1] + period + 1, period
                )
                doys = []
                for d1, d2 in zip(
                    _doys1,
                    _doys2
                ):
                    if (d1 >= _doys[1] or
                            d2 >= _doys[1]):
                        break
                    doys.extend([d1, d2])
                levs = _levs * len(doys)

            ret.extend([
                {'doy': doy, 'waterLevel': level}
                for doy, level in zip(doys, levs)
            ])
            sorted_ret = sorted(ret, key=itemgetter('doy'))
        return sorted_ret
