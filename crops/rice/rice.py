from ..base import BaseCropModel


class RiceModel(BaseCropModel):
    name = '벼'
    _type = 'rice'
    color = '#d77c29'
    gdd_method = 'm3'
    division = 'agricultural'

    max_dev_temperature = 40

    # 재배관련 - warnings
    high_extrema_temperature = 40
    high_extrema_exposure_days = 5
    low_extrema_temperature = 12
    low_extrema_exposure_days = 5

    @property
    def schedules(self):
        ret = super().schedules
        start_doy = self.start_doy  # 이앙기
        fertilize1_range = [start_doy - 4, start_doy - 5]  # 기비
        fertilize2 = start_doy + 12  # 분얼비

        # 출수기
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

        fertilize3_range = [heading_range[0] - 25, heading_range[1] - 25]  # 수비
        fertilizing_events = [
            {
                'type': 'fertilize_range', 'name': '기비',
                'data': fertilize1_range,
                'text': """인산 비료의 경우 기비시 전량 시비합니다."""
            },
            {
                'type': 'fertilize', 'name': '분얼비',
                'data': fertilize2,
                'text': """
                    기비와 수비의 비율을 7:3으로 할 경우,
                    분얼비는 생략가능합니다.
                """
            },
            {
                'type': 'fertilize_range', 'name': '수비',
                'data': fertilize3_range
            },
        ]
        ret.extend(fertilizing_events)
        return ret

    @property
    def warnings(self):
        ret = super().warnings

        start_doy = self.start_doy

        # 안전 출수기
        # 출수기 이후 40 일 평균기온 21~24 도 사이 22.5 도가 최적 출수기
        # 범위에서 벗어나 1 도 차이마다 10%씩 수량감소
        lowest_heading_temp = 16
        low_heading_temp = 21
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
        elif harvest_decrease_by_cold_ratio >= 10 and harvest_decrease_by_cold_ratio < 50:
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
        elif harvest_decrease_by_heat_ratio >= 10 and harvest_decrease_by_heat_ratio < 50:
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
