import pandas as pd

from ..utils.helper import is_hyperparam_equal


DOY_MINIMA = 1
DOY_MAXIMA = 366 * 2


class BaseCropModel:
    base_temperature = 0
    develop_range = [33, 43]  # latitude range in which crop is growable
    allow_multiple_cropping = False
    max_dev_temperature = 99

    def __init__(self, id=None):
        self.id = id
        self.weather_df = None
        self.gdd_weather_df = None
        self.min_start_doy = 0
        self.max_start_doy = 366

    def set_parameters(self, parameters):
        # TODO: remove previous parameters
        self.base_temperature = 0
        self.max_dev_temperature = 99

        # remove previous hyper_parameters
        self.gdd_hyperparams = []
        self.doy_hyperparams = []
        self.first_priority_hyperparams = []
        self.warning_hyperparams = []

        if hasattr(self, 'parent_key'):
            parent_crop_params = parameters.get(self.parent_key, {})
            [setattr(self, k, v) for k, v in parent_crop_params.items()]

        crop_params = parameters.get(self.key, {})
        for k, v in crop_params.items():
            if hasattr(self, k) and isinstance(getattr(self, k), list):
                # if parameter is already set by parent & is list,
                # concatenate
                inherited_v = getattr(self, k)
                setattr(self, k, inherited_v + v)
            else:
                setattr(self, k, v)

    def set_id_with_index(self, index):
        self.id = f'{self.key}_{index}'

    def set_weather_data(self, weather_df):
        self.weather_df = weather_df
        self.gdd_weather_df = self.get_gdd_weather_df()

    def update_parameters(self, parameters: list) -> None:
        for new_param in parameters:
            # search & update parameters (not hyperparameters)
            # parameters: 기준온도, 최대생육온도, GDD계산식

            param_type = new_param['type']
            param_value = new_param['value']

            if hasattr(self, param_type):
                setattr(self, param_type, param_value)
                continue

            # search & udpate gdd_hyperparams
            for idx, old_param in enumerate(self.gdd_hyperparams):
                if not is_hyperparam_equal(old_param, new_param):
                    continue
                merged_param = {**old_param, **new_param}
                # if param has max_period its type should be _range
                if merged_param.get('max_period', 0) != 0:
                    merged_param['type'] = \
                        merged_param['type'].replace('_range', '') + '_range'
                self.gdd_hyperparams[idx] = merged_param

            # TODO: search & udpate doy_hyperparams

            # search & udpate refernce_hyperparams(first priority hyperparams)
            for idx, old_param in enumerate(self.first_priority_hyperparams):
                if not is_hyperparam_equal(old_param, new_param):
                    continue
                merged_param = {**old_param, **new_param}
                # if param has max_period its type should be _range
                if merged_param.get('max_period', 0) != 0:
                    merged_param['type'] = \
                        merged_param['type'].replace('_range', '') + '_range'
                self.first_priority_hyperparams[idx] = merged_param

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
        df_year_after_next_year = df.copy()
        df_next_year['doy'] += 366
        df_year_after_next_year['doy'] += 366*2

        ret_df = pd.concat(
            [df, df_next_year, df_year_after_next_year],
            ignore_index=True
        )
        ret_df['tavg_dev_cumsum'] = ret_df['tavg_dev'].cumsum()
        return ret_df.set_index('doy')

    def set_start_doy(self, start_doy=None):
        if start_doy is None:
            start_doy = self.start_doy

        end_doy = self.get_event_end_doy(start_doy, self.growth_gdd)
        if end_doy < 366*2:
            self.start_doy = start_doy
            self.end_doy = end_doy
        else:
            end_doy = 366*2
            self.end_doy = end_doy
            start_doy = self.get_event_start_doy(end_doy, self.growth_gdd)
            self.start_doy = max(start_doy, 1)

    def get_event_end_doy(self, event_base_doy, gdd):
        if self.weather_df is None:
            raise ValueError('weather data not prepared.')
        if gdd == 0:
            return event_base_doy

        df = self.gdd_weather_df

        min_idx = 1
        max_idx = len(df)
        cursor_idx = min(event_base_doy - 1, max_idx)
        cursor_idx = max(cursor_idx, min_idx)

        event_end_df = (
            df['tavg_dev_cumsum'] >= gdd +
            df.loc[cursor_idx, 'tavg_dev_cumsum']
        )

        if event_end_df.sum() == 0:
            return DOY_MAXIMA
        event_end_doy = int(event_end_df.idxmax())
        return event_end_doy

    def get_event_start_doy(self, event_base_doy, gdd):
        if self.weather_df is None:
            raise ValueError('weather data not prepared.')
        if gdd == 0:
            return event_base_doy

        df = self.gdd_weather_df

        min_idx = 1
        max_idx = len(df)
        cursor_idx = min(event_base_doy - 1, max_idx)
        cursor_idx = max(cursor_idx, min_idx)

        event_start_df = (
            # TODO
            df.loc[event_base_doy: 0: -1, 'tavg_dev'].cumsum() >=
            gdd
        )

        # can't satisfiy condition
        if event_start_df.sum() == 0:
            return DOY_MINIMA
        event_start_doy = int(event_start_df.idxmax())
        return event_start_doy

    def calculate_first_priority_params(self):
        ret = {}
        # 우선 계산 필요한 event들 계산 => ret에 저장
        for param in self.first_priority_hyperparams:
            if param['method'] == 'GDD':
                event = self.calculate_gdd_hyperparam(param)

                base_type = event['type'].split('_')[0]
                ret.update({
                    base_type: event['data'],
                    base_type + '_range': event['data']
                })
            elif param['method'] == 'DOY':
                # NOTE: "ret" will be mutated in loop,
                # "calculate_doy_hyperparam" method dosn't mutates "ret"
                event = self.calculate_doy_hyperparam(param, ret)
                base_type = event['type'].split('_')[0]
                ret.update({
                    base_type: event['data'],
                    base_type + '_range': event['data']
                })
                pass
            else:
                raise NotImplementedError('not implemented')
        return ret

    def calculate_gdd_hyperparam(self, param):
        start_doy = self.start_doy

        # get_event
        max_period = param.get('max_period')
        if isinstance(param['value'], list):
            event_data = [
                self.get_event_end_doy(start_doy, val)
                for val in param['value']
            ]
            if max_period is not None:
                event_data[1] = event_data[0] + max_period \
                    if event_data[1] - event_data[0] > max_period \
                    else event_data[1]

        else:
            event_data = self.get_event_end_doy(start_doy, param['value'])
            if max_period is not None:
                event_data = [
                    event_data - (max_period // 2 - 2),
                    event_data + (max_period // 2 + 2)
                ]

        event = {
            'type': param.get('type'),
            'name': param.get('name', ''),
            'data': event_data,
            'text': param.get('text', '')
        }
        return event

    def calculate_doy_hyperparam(self, param, ref_data):
        event_data = []

        n_refs = len(param['ref'])
        for ref, index, val in zip(
            param['ref'],
            param.get('index', [None] * n_refs),
            param['value']
        ):
            _ref_data = ref_data.get(ref)
            if _ref_data is None:
                raise ValueError('Failed to get preceding calculation results')

            if index is not None:
                ret_doy = _ref_data[index] + val
            else:
                ret_doy = _ref_data + val

            event_data.append(ret_doy)

        event_data = event_data[0] if len(event_data) == 1 else event_data
        event = {
            'type': param.get('type'),
            'name': param.get('name', ''),
            'data': event_data,
            'text': param.get('text', '')
        }
        return event

    def get_extreme_temperature_warnings(self, param):
        start_doy = self.start_doy
        end_doy = self.end_doy
        df = self.weather_df.copy()
        n_years = df['year'].nunique()

        high_extrema_temperature = param['high_extrema_temperature']
        high_extrema_exposure_days = param['high_extrema_exposure_days']
        low_extrema_temperature = param['low_extrema_temperature']
        low_extrema_exposure_days = param['low_extrema_exposure_days']

        ret = []

        # 생육한계 최고온도 & 노출일수
        tmax_df = df.copy()[['year', 'doy', 'tmax']]\
            .sort_values(['year', 'doy'])\
            .query((f'tmax > {high_extrema_temperature} & '
                    f'doy >= {start_doy} & doy <= {end_doy}'))

        tmax_df['doy_group'] = (tmax_df['doy'].diff(1).fillna(1) != 1).cumsum()
        tmax_df['too_much_exposure'] = False

        for _, group in tmax_df.groupby('doy_group'):
            if len(group) >= high_extrema_exposure_days:
                tmax_df.loc[group.index, 'too_much_exposure'] = True

        _tmax_exposure_df = tmax_df.pivot(
            index='doy', columns='year', values='too_much_exposure'
            ).fillna(False).sort_index()
        tmax_exposure_df = _tmax_exposure_df.sum(axis=1) / n_years
        if (tmax_exposure_df.loc[start_doy: end_doy] >= 0.3).sum() > 0:
            ret.append({
                'title': '재배가능성 낮음',
                'type': '고온해 위험',
                'message': f"""생육한계 최고온도 {
                    high_extrema_temperature
                }℃ 초과의 온도에 연속 {
                    high_extrema_exposure_days
                }일 이상 노출된 년도의 수가 전체 기상자료의 10% 이상입니다."""
            })

        # 생육한계 최저온도 & 노출일수
        tmin_df = df.copy()[['year', 'doy', 'tmin']]\
            .sort_values(['year', 'doy'])\
            .query((f'tmin < {low_extrema_temperature} & '
                    f'doy >= {start_doy} & doy <= {end_doy}'))
        tmin_df['doy_group'] = (tmin_df['doy'].diff(1).fillna(1) != 1).cumsum()
        tmin_df['too_much_exposure'] = False

        for _, group in tmin_df.groupby('doy_group'):
            if len(group) >= low_extrema_exposure_days:
                tmin_df.loc[group.index, 'too_much_exposure'] = True

        _tmin_exposure_df = tmin_df.pivot(
            index='doy', columns='year', values='too_much_exposure'
            ).fillna(False).sort_index()
        tmin_exposure_df = _tmin_exposure_df.sum(axis=1) / n_years
        if (tmin_exposure_df.loc[start_doy: end_doy] >= 0.3).sum() > 0:
            ret.append({
                    'title': '재배가능성 낮음',
                    'type': '동해 위험',
                    'message': f"""생육한계 최저온도 {
                        low_extrema_temperature
                    }℃ 미만의 온도에 연속 {
                        low_extrema_exposure_days
                    }일 이상 노출된 년도의 수가 전체 기상자료의 30% 이상입니다."""
                    })

        return ret

    def get_milestone_temperature_warnings(self, param):
        df = self.gdd_weather_df.copy()
        ref_data = self.calculate_first_priority_params()

        doys = self.calculate_doy_hyperparam(
            param['milestone'],
            ref_data
        )['data']
        cond = param['condition']

        variable = cond['variable']
        danger_temperature = cond['temperature']
        operator = cond['operator']

        if operator == 'ge':
            liability = \
                (df.loc[doys[0]: doys[1], variable] >=
                    danger_temperature).sum() > 0
        elif operator == 'gt':
            liability = \
                (df.loc[doys[0]: doys[1], variable] >
                    danger_temperature).sum() > 0
        elif operator == 'eq':
            liability = \
                (df.loc[doys[0]: doys[1], variable] ==
                    danger_temperature).sum() > 0
        else:
            raise NotImplementedError('operation not implemented')

        if liability:
            warning_data = param.get('warning_data', None)
            return [warning_data]
        return []

    def get_milestone_length_warnings(self, param):
        ref_data = self.calculate_first_priority_params()
        doys = self.calculate_doy_hyperparam(
            param['milestone'],
            ref_data
        )['data']
        milestone_length = doys[1] - doys[0]
        cond = param['condition']
        length = cond['length']
        operator = cond['operator']

        if operator == 'gt':
            liability = milestone_length > length
        elif operator == 'ge':
            liability = milestone_length >= length
        elif operator == 'eq':
            liability = milestone_length == length
        elif operator == 'le':
            liability = milestone_length <= length
        elif operator == 'lt':
            liability = milestone_length < length
        else:
            raise NotImplementedError('operation not implemented')

        if liability:
            warning_data = param.get('warning_data', None)
            return [warning_data]
        return []

    @property
    def growth_gdd(self):
        rule = self.growth_gdd_rule
        ref = rule.get('ref')
        idx = rule.get('index')

        ref_param = None
        for param in self.gdd_hyperparams:
            is_type_match = param['type'].split('_')[0] == ref.split('_')[0]
            if is_type_match is True:
                ref_param = param
                break
        ref_val = ref_param['value']
        if isinstance(ref_val, list):
            return ref_val[idx]
        else:
            return ref_val

    @property
    def growth(self):
        # 작물의 변화 일정
        return {
            'type': 'growth_range',
            'name': '재배기간',
            'data': [self.start_doy, self.end_doy]
        }

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
        events = [self.growth]
        ref = self.calculate_first_priority_params()

        # gdd 기반 계산이 필요한 event들 계산
        for param in self.gdd_hyperparams:
            if 'events' not in param['expose_to']:
                continue

            event = self.calculate_gdd_hyperparam(param)
            events.append(event)

        # doy 기반 계산이 필요한 event들 계산
        for param in self.doy_hyperparams:
            if 'events' not in param['expose_to']:
                continue
            event = self.calculate_doy_hyperparam(param, ref)
            events.append(event)
        return events

    @property
    def schedules(self):
        # 작업 일정
        schedules = []
        ref = self.calculate_first_priority_params()

        # gdd 기반 계산이 필요한 event들 계산
        for param in self.gdd_hyperparams:
            if 'schedules' not in param['expose_to']:
                continue

            schedule = self.calculate_gdd_hyperparam(param)
            schedules.append(schedule)

        # doy 기반 계산이 필요한 event들 계산
        for param in self.doy_hyperparams:
            if 'schedules' not in param['expose_to']:
                continue
            schedule = self.calculate_doy_hyperparam(param, ref)
            schedules.append(schedule)

        return schedules

    @property
    def attribute(self):
        attribute = {
            'key': self.key,
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
        ret_warnings = []

        for param in self.warning_hyperparams:
            method = param['method']

            if method == 'temperature_and_exposure':
                _warnings = self.get_extreme_temperature_warnings(param)
                ret_warnings.extend(_warnings)

            elif method == 'milestone_and_temperature_condition':
                _warnings = self.get_milestone_temperature_warnings(param)
                ret_warnings.extend(_warnings)

            elif method == 'milestone_length_condition':
                _warnings = self.get_milestone_length_warnings(param)
                ret_warnings.extend(_warnings)

        return ret_warnings

    @property
    def parameters(self):
        _parameters = [
            {
                'type': 'base_temperature',
                'value': self.base_temperature,
                'editable': True,
            },
            {
                'type': 'max_dev_temperature',
                'value': self.max_dev_temperature,
                'editable': True,
            },
            {
                'type': 'gdd_method',
                'value': self.gdd_method,
                'editable': True,
            },
        ]

        hyper_params = []
        for param in self.gdd_hyperparams:
            hyper_params.append({
                **param,
                'editable': True
            })

        for param in self.doy_hyperparams:
            hyper_params.append({
                **param,
                'editable': False
            })

        return _parameters + hyper_params
