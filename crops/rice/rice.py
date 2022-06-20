from ..base import BaseCropModel


class RiceModel(BaseCropModel):
    name = '벼'
    _type = 'rice'
    color = '#d77c29'
    gdd_method = 'm3'

    max_dev_temperature = 40

    # 재배관련 - warnings
    high_extrema_temperature = 40
    high_extrema_exposure_days = 5
    low_extrema_temperature = 12
    low_extrema_exposure_days = 5

    @property
    def warnings(self):
        ret = super().warnings

        start_doy = self.start_doy

        # 안전 출수기
        # 출수기 이후 40 일 평균기온 21~24 도 사이 22.5 도가 최적 출수기
        # 범위에서 벗어나 1 도 차이마다 10%씩 수량감소
        lowest_heading_temp = 16
        lower_temp = 21
        high_heading_temp = 24
        highest_heading_temp = 29

        if hasattr(self, 'heading_gdd_range'):
            heading_range = [
                max(start_doy, self.get_event_end_doy(start_doy, gdd))
                for gdd in self.heading_gdd_range
            ]
        elif hasattr(self, 'heading_gdd'):
            heading = self.get_event_end_doy(start_doy, self.heading_gdd)
            heading_range = [
                max(start_doy, heading - 5), heading + 9
            ]
        else:
            raise AttributeError(f'CropModel {self.key} is incomplete')

        window_size = 40
        df = self.gdd_weather_df.copy()
        df['40days_tavg'] = df.rolling(window_size + 1)\
                              .agg({'tavg': 'mean'})\
                              .shift(-window_size)['tavg']

        tavg_40days_while_heading = df.loc[
            heading_range[0]: heading_range[1], '40days_tavg'
        ]
        if (tavg_40days_while_heading <= lowest_heading_temp).sum() > 0:
            ret.append({
                'type': '출수 위험',
                'name': '안전 출수기',
                'message': f"""출수기 온도 {lowest_heading_temp}℃ 이하입니다.
                    수확량이 50% 감소할 수 있습니다"""
            })
        elif (tavg_40days_while_heading < lower_temp).sum() > 0:
            ret.append({
                'type': '출수 주의',
                'name': '안전 출수기',
                'message': f"""안전 출수기 적정온도 {lower_temp}℃ 미만입니다.
                    수확량이 감소할 수 있습니다"""
            })
        if (tavg_40days_while_heading >= highest_heading_temp).sum() > 0:
            ret.append({
                'type': '출수 위험',
                'name': '안전 출수기',
                'message': f"""출수기 온도 {highest_heading_temp}℃ 이상입니다.
                    수확량이 50% 감소할 수 있습니다"""
            })
        elif (tavg_40days_while_heading > high_heading_temp).sum() > 0:
            ret.append({
                'type': '출수 주의',
                'name': '안전 출수기',
                'message': f"""안전 출수기 적정온도 {high_heading_temp}℃ 초과입니다.
                    수확량이 감소할 수 있습니다"""
            })

        return ret
