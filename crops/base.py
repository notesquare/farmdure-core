import pandas as pd


class BaseCropModel:
    base_temperature = 0
    develop_range = [33, 43]  # latitude range in which crop is growable
    allow_multiple_cropping = False
    max_dev_temperature = 99
    gdd_method = 'm2'

    def __init__(self, id=None):
        self.id = id
        self.weather_df = None
        self.gdd_weather_df = None
        self.min_start_doy = 0
        self.max_start_doy = 366

        self.start_doy = self.default_start_doy

    def set_id_with_index(self, index):
        self.id = f'{self.key}_{index}'

    def set_weather_data(self, weather_df):
        self.weather_df = weather_df
        self.gdd_weather_df = self.get_gdd_weather_df()

    def update_gdd_method(self, method):
        should_update = self.gdd_method != method
        self.gdd_method = method
        self.gdd_weather_df = self.get_gdd_weather_df()

        if should_update is True:
            self.set_start_doy(self.start_doy)

    def get_gdd_weather_df(self):
        if self.weather_df is None:
            raise ValueError('weather data not prepared.')

        # avg. temperature
        _df = self.weather_df.reset_index(drop=True)
        df = _df.groupby('doy').mean().reset_index()

        gdd_method = self.gdd_method
        if gdd_method == 'm1':
            df['tavg'] = (df['tmax'] + df['tmin']) / 2
            df['tavg_dev'] = df['tavg'] - self.base_temperature
            df['tavg_dev'] = df['tavg_dev'].clip(lower=0)

        elif gdd_method == 'm2':
            t_b = self.base_temperature
            t_u = self.max_dev_temperature

            df['tavg'] = (df['tmax'] + df['tmin']) / 2
            df['tavg_dev'] = df['tavg'].clip(lower=t_b, upper=t_u) - t_b

        elif gdd_method == 'm3':
            t_b = self.base_temperature
            t_u = self.max_dev_temperature

            df['tavg'] = (df['tmax'] + df['tmin']) / 2
            df['t_m'] = df['tmax'].clip(upper=t_u)
            df['t_n'] = df['t_m'].clip(lower=t_b)
            df['tavg_dev'] = (df['t_m'] + df['t_n']) / 2

            df.loc[df['tavg'] < t_b, 'tavg_dev'] = t_b
            df.loc[df['tavg'] > t_u, 'tavg_dev'] = t_u
            df['tavg_dev'] = df['tavg_dev'] - t_b
            df = df.drop(['t_m', 't_n'], axis=1)

        else:
            raise NotImplementedError('Unknown GDD method', gdd_method)

        df_next_year = df.copy()
        df_next_year['doy'] += 366

        ret_df = pd.concat([df, df_next_year], ignore_index=True)
        ret_df['tavg_dev_cumsum'] = ret_df['tavg_dev'].cumsum()
        return ret_df.set_index('doy')

    def set_start_doy(self, start_doy=None):
        # Note: sets start_doy then updates end_doy
        if start_doy is None:
            start_doy = self.default_start_doy

        self.start_doy = start_doy
        end_doy = self.get_event_end_doy(self.start_doy, self.growth_gdd)
        self.end_doy = end_doy

    def set_end_doy(self, end_doy):
        # Note: sets end_doy then updates start_doy
        self.end_doy = end_doy
        start_doy = self.get_event_start_doy(self.start_doy, self.growth_gdd)
        self.start_doy = start_doy

    def get_event_end_doy(self, event_base_doy, gdd):
        if self.weather_df is None:
            raise ValueError('weather data not prepared.')

        event_base_doy = max(event_base_doy, 2)
        df = self.gdd_weather_df
        event_doy = (
            df['tavg_dev_cumsum'] >= gdd +
            df.loc[event_base_doy - 1, 'tavg_dev_cumsum']
        ).idxmax()

        event_doy = int(event_doy)
        return event_doy

    def get_event_start_doy(self, event_base_doy, gdd):
        if self.weather_df is None:
            raise ValueError('weather data not prepared.')

        df = self.gdd_weather_df
        event_doy = (
            df.loc[event_base_doy: 0: -1, 'tavg_dev'].cumsum() >=
            gdd
        ).idxmax()

        event_doy = int(event_doy)
        return event_doy

    def is_start_doy_possible(self, start_doy):
        ret = self.min_start_doy <= start_doy and \
              start_doy <= self.max_start_doy
        return ret

    @property
    def start_doy_range(self):
        return [self.min_start_doy, self.max_start_doy]

    @property
    def growths(self):
        # 작물의 변화 일정
        return [
            {
                'type': 'growth_range',
                'name': '재배기간',
                'data': [self.start_doy, self.end_doy]
            }
        ]

    @property
    def progress(self):
        df = self.gdd_weather_df
        _doy = max(self.start_doy - 1, 1)
        starting_cummulative_temperature = \
            df.loc[_doy, 'tavg_dev_cumsum']
        progress = (
            df['tavg_dev_cumsum'] - starting_cummulative_temperature
        ) / self.growth_gdd

        data = progress\
            .loc[_doy: self.end_doy]\
            .astype('f8')\
            .round(2)\
            .clip(upper=1.)\
            .drop_duplicates(keep='first')\
            .rename('progress')\
            .reset_index()\
            .to_dict('records')
        return {
            'type': 'progress',
            'name': '생육진행도',
            'data': data
        }

    @property
    def events(self):
        events = self.growths
        return events

    @property
    def schedules(self):
        # 농민의 작업 일정
        return []

    @property
    def attribute(self):
        attribute = {
            'key': self.key,
            'start_doy_range': self.start_doy_range,
            'allow_multiple_cropping': self.allow_multiple_cropping
        }
        if hasattr(self, 'id'):
            attribute.update({'id': self.id})
        if hasattr(self, 'name'):
            attribute.update({'name': self.name})
        if hasattr(self, '_type'):
            attribute.update({'type': self._type})
        if hasattr(self, 'color'):
            attribute.update({'color': self.color})
        return attribute

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
                df['tmax'] > self.high_extrema_temperature
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

        return ret
