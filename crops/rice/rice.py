from ..base import BaseCropModel


class RiceModel(BaseCropModel):
    name = '벼'
    _type = 'rice'
    color = '#d77c29'
    gdd_method = 'm3'

    @property
    def warnings(self):
        ret = super().warnings

        # 안전 출수기
        # 출수기 이후 40 일 평균기온 21~24 도 사이 22.5 도가 최적 출수기
        # 범위에서 벗어나 1 도 차이마다 10%씩 수량감소
        lowest_heading_temp = 16
        low_heading_temp = 21
        high_heading_temp = 24
        highest_heading_temp = 29

        ref = self.calculate_first_priority_params()
        heading_range = ref.get('heading_range')

        window_size = 40
        df = self.gdd_weather_df.copy()
        df['40days_tavg'] = df.rolling(window_size + 1)\
                              .agg({'tavg': 'mean'})\
                              .shift(-window_size)['tavg']

        harvest_decrease_by_cold = (
            df.loc[heading_range[0]: heading_range[1], '40days_tavg']
            - low_heading_temp).clip(upper=0).round(0)
        harvest_decrease_by_heat = (
            high_heading_temp
            - df.loc[heading_range[0]: heading_range[1], '40days_tavg']
            ).clip(upper=0).round(0)

        harvest_decrease_by_cold_ratio = (
            -10 * harvest_decrease_by_cold.sum() /
            (heading_range[1] - heading_range[0] + 1)
        )
        harvest_decrease_by_heat_ratio = (
            -10 * harvest_decrease_by_heat.sum() /
            (heading_range[1] - heading_range[0] + 1)
        )

        if harvest_decrease_by_cold_ratio >= 50:
            ret.append({
                'type': '출수 위험',
                'title': '안전 출수기',
                'message': f"""출수기 온도 {lowest_heading_temp}℃ 이하입니다.
                    수확량이 50% 감소할 수 있습니다"""
            })
        elif (harvest_decrease_by_cold_ratio >= 10 and
              harvest_decrease_by_cold_ratio < 50):
            ret.append({
                'type': '출수 주의',
                'title': '안전 출수기',
                'message': f"""안전 출수기 적정온도 {low_heading_temp}℃ 미만입니다.
                    수확량이 감소할 수 있습니다"""
            })
        elif harvest_decrease_by_heat_ratio >= 50:
            ret.append({
                'type': '출수 위험',
                'title': '안전 출수기',
                'message': f"""출수기 온도 {highest_heading_temp}℃ 이상입니다.
                    수확량이 50% 감소할 수 있습니다"""
            })
        elif (harvest_decrease_by_heat_ratio >= 10 and
              harvest_decrease_by_heat_ratio < 50):
            ret.append({
                'type': '출수 주의',
                'title': '안전 출수기',
                'message': f"""안전 출수기 적정온도 {high_heading_temp}℃ 초과입니다.
                    수확량이 감소할 수 있습니다"""
            })
        else:
            ret.append({
                'type': '안전 출수',
                'title': '안전 출수기',
                'message': f"""
                    출수기 중 40일 평균 기온이
                    {low_heading_temp}~{high_heading_temp}℃ 를 만족합니다."""
            })
        return ret

    @property
    def water_level(self):
        ret = []
        for param in self.doy_hyperparams:
            if 'water_level' not in param['expose_to']:
                continue
            ref = self.calculate_first_priority_params()

            period = param.get('period')
            if period is None:
                # 일반적인 수위 관리
                doys = self.calculate_doy_hyperparam(param, ref)['data']
                levs = param['water_level']
            else:
                # 물대기와 물떼기 반복
                _doys = self.calculate_doy_hyperparam(param, ref)['data']
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
        return ret
