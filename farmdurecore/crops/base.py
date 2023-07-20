import pprint
from collections import OrderedDict

import polars as pl

from ..utils.helper import is_hyperparam_equal, is_hyperparam_valid
from ..utils.profiler import (
    profile_gdd_hyperparams, profile_doy_hyperparams,
    profile_warning_hyperparams
)


DOY_MINIMA = 1
DOY_MAXIMA = 366 * 2


class BaseCropModel:
    base_temperature = 0
    develop_range = [33, 43]  # latitude range in which crop is growable
    allow_multiple_cropping = False
    max_dev_temperature = 99

    def __init__(self, id: str = None):
        self.id = id
        self.weather_df = None
        self.gdd_weather_df = None
        self.min_start_doy = 0
        self.max_start_doy = 366

    def __repr__(self):
        attr_repr = f"""
                작물키: {self.key}
                작물명: {self.name}
                GDD 계산법: {self.gdd_method}
                기준온도: {self.base_temperature}
                최고생육온도: {self.max_dev_temperature}"""
        gdd_repr = [
            f"""
                구분: {prof['name']}
                GDD 값: {prof['value']}
                기간제한: {prof.get('period', '')}
                상세내용: {prof.get('text', '')}
                카테고리: {prof.get('expose_to', '')}
            """
            for prof in profile_gdd_hyperparams(self)
        ]

        doy_repr = [
            f"""
                구분: {prof['name']}
                기준일: {prof['value']}
                기간제한: {prof.get('period', '')}
                상세내용: {prof.get('text', '')}
                카테고리: {prof.get('expose_to', '')}
            """
            for prof in profile_doy_hyperparams(self)
        ]

        warning_repr = [
            f"""
                방식: {prof['method']}
                구분: {prof['name']}
                상세내용: {prof.get('text', '')}
            """
            for prof in profile_warning_hyperparams(self)
        ]

        attr_repr = f"기본정보 {attr_repr}"
        gdd_repr = f"GDD 기반 조건 {''.join(gdd_repr)}" \
            if len(gdd_repr) != 0 else ''
        doy_repr = f"날짜 기반 조건 {''.join(doy_repr)}" \
            if len(doy_repr) != 0 else ''
        warning_repr = f"경고 표시 조건 {''.join(warning_repr)}" \
            if len(warning_repr) != 0 else ''

        ret = f'{attr_repr}\n{gdd_repr}\n{doy_repr}\n{warning_repr}\n'
        return ret

    def set_parameters(self, parameters):
        # TODO: remove previous parameters
        self.base_temperature = 0
        self.max_dev_temperature = 99

        # remove previous hyper_parameters
        self.gdd_hyperparams = []
        self.doy_hyperparams = []
        self.first_priority_hyperparams = []
        self.warning_hyperparams = []

        # crop_params = parameters.get(self.key, {})
        for k, v in parameters.items():
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
                if (new_param.get('ranged') is False and
                        'period' in merged_param):
                    del merged_param['period']

                if not is_hyperparam_valid(merged_param):
                    print('not valid')
                    break

                self.gdd_hyperparams[idx] = merged_param

            # search & udpate doy_hyperparams
            # TODO: Not Implemented yet

            # search & udpate refernce_hyperparams(first priority hyperparams)
            for idx, old_param in enumerate(self.first_priority_hyperparams):
                if not is_hyperparam_equal(old_param, new_param):
                    continue
                merged_param = {**old_param, **new_param}
                self.first_priority_hyperparams[idx] = merged_param

            # search & update warning_hyperparams
            # TODO: Not Implemented yet

    def get_gdd_weather_df(self):
        if self.weather_df is None:
            raise ValueError('weather data not prepared.')

        weather_df = self.weather_df
        # avg. temperature
        df = weather_df.groupby('doy').agg([
                pl.mean('tmin'),
                pl.mean('tmax')])

        gdd_method = self.gdd_method
        if gdd_method == 'm1':
            t_b = self.base_temperature

            q = df.with_columns([
                ((pl.col('tmax') + pl.col('tmin')) / 2).alias('tavg'),

                (((pl.col('tmax') + pl.col('tmin')) / 2) - t_b).clip_min(0)
                .alias('tavg_dev'),
            ]).sort('doy')

        elif gdd_method == 'm2':
            t_b = self.base_temperature
            t_u = self.max_dev_temperature

            q = df.with_columns([
                ((pl.col('tmax') + pl.col('tmin')) / 2).alias('tavg'),
                (
                    ((pl.col('tmax') + pl.col('tmin')) / 2).clip(t_b, t_u)
                    - t_b
                ).alias('tavg_dev'),
            ]).sort('doy')

        elif gdd_method == 'm3':
            t_b = self.base_temperature
            t_u = self.max_dev_temperature

            q = (
                df.with_columns([
                    ((pl.col('tmax') + pl.col('tmin')) / 2).alias('tavg'),
                    pl.col('tmax').clip_max(t_u).alias('t_m'),
                    pl.col('tmax').clip_max(t_u).clip_min(t_b).alias('t_n')
                ])
                .with_columns([
                    pl.when(pl.col('tavg') < t_b).then(t_b)
                    .when(pl.col('tavg') > t_u).then(t_u)
                    .otherwise((pl.col('t_m') + pl.col('t_n')) / 2)
                    .alias('tavg_dev')
                ])
                .select([
                    pl.col('doy'),
                    pl.col('tmin'),
                    pl.col('tmax'),
                    pl.col('tavg_dev') - t_b,
                ])
                .sort('doy')
            )

        else:
            raise NotImplementedError('Unknown GDD method', gdd_method)

        q_next_year = q.clone().with_columns(pl.col('doy') + 366)
        q_year_after_next_year = q.clone().with_columns(pl.col('doy') + 366*2)

        ret_q = pl.concat([q, q_next_year, q_year_after_next_year])\
            .with_columns(pl.col('tavg_dev').cumsum().alias('tavg_dev_cumsum'))
        return ret_q

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

        min_idx = 0
        max_idx = 366 * 3 - 1
        cursor_idx = min(event_base_doy - 1, max_idx)
        cursor_idx = max(cursor_idx, min_idx)

        df = self.gdd_weather_df
        end_doy = df.slice(cursor_idx, 366*3).filter(
            pl.col('tavg_dev').cumsum() > gdd
        ).select(
            pl.col('doy').first()
        ).collect()

        if len(end_doy) == 0:
            return DOY_MAXIMA
        return end_doy['doy'].to_numpy()[0] + 1

    def get_event_start_doy(self, event_base_doy, gdd):
        if self.weather_df is None:
            raise ValueError('weather data not prepared.')
        if gdd == 0:
            return event_base_doy

        df = self.gdd_weather_df

        min_idx = 0
        max_idx = 366 * 3 - 1
        cursor_idx = min(event_base_doy - 1, max_idx)
        cursor_idx = max(cursor_idx, min_idx)

        start_doy = df.slice(0, event_base_doy-1).filter(
            pl.col('tavg_dev').reverse().cumsum() > gdd
        ).select(
            pl.col('doy').first()
        ).collect()

        if len(start_doy) == 0:
            return DOY_MINIMA
        return event_base_doy - start_doy['doy'].to_numpy()[0]

    def calculate_first_priority_params(self):
        ret = {}
        # 우선 계산 필요한 event들 계산 => ret에 저장
        for param in self.first_priority_hyperparams:
            if param['method'] == 'GDD':
                _matching_param = filter(
                    lambda x: is_hyperparam_equal(x, param),
                    self.gdd_hyperparams
                )
                matching_param = next(_matching_param)
                event = self.calculate_gdd_hyperparam(matching_param)
                ret.update({event['type']: event['doy']})

            elif param['method'] == 'DOY':
                _matching_param = filter(
                    lambda x: is_hyperparam_equal(x, param),
                    self.doy_hyperparams
                )
                matching_param = next(_matching_param)
                # NOTE: "ret" will be mutated in loop,
                # "calculate_doy_hyperparam" method dosn't mutates "ret"
                event = self.calculate_doy_hyperparam(matching_param, ret)
                ret.update({event['type']: event['doy']})
            else:
                raise NotImplementedError('not implemented')
        return ret

    def calculate_gdd_hyperparam(self, param):
        start_doy = self.start_doy

        # get_event
        if param.get('ranged') is True:
            period = param.get('period')
            if isinstance(param['value'], list):
                event_doys = [
                    self.get_event_end_doy(start_doy, val)
                    for val in param['value']
                ]
                if period is not None:
                    # upper bound to doys
                    event_doys[1] = event_doys[0] + period \
                        if event_doys[1] - event_doys[0] > period \
                        else event_doys[1]

            else:
                event_doy = self.get_event_end_doy(start_doy, param['value'])
                event_doys = [event_doy, event_doy + param['period']]

            # apply limits to doy
            event_doys = [
                max(event_doys[0], 0),
                min(event_doys[1], 366 * 2)
            ]
            ranged = True

        else:
            event_doys = self.get_event_end_doy(start_doy, param['value'])
            ranged = False

        event = {
            'type': param.get('type'),
            'name': param.get('name', ''),
            'doy': event_doys,
            'ranged': ranged,
            'text': param.get('text', '')
        }
        return event

    def calculate_doy_hyperparam(self, param, ref_data):
        event_doys = []

        n_refs = len(param['ref'])
        for ref, index, val in zip(
            param['ref'],
            param.get('index', [None] * n_refs),
            param['value']
        ):
            _ref_data = ref_data.get(ref)
            if _ref_data is None:
                raise ValueError('Failed to get preceding calculation results')

            if isinstance(_ref_data, list):
                if index is None:
                    index = 0 if val < 0 else 1
                ret_doy = _ref_data[index] + val

            else:
                ret_doy = _ref_data + val

            event_doys.append(ret_doy)

        if len(event_doys) == 1:
            event_doys = event_doys[0]
            ranged = False
        else:
            ranged = True

        event = {
            'type': param.get('type'),
            'name': param.get('name', ''),
            'doy': event_doys,
            'ranged': ranged,
            'text': param.get('text', '')
        }
        return event

    def get_extreme_temperature_warnings(self, param):
        start_doy = self.start_doy
        end_doy = self.end_doy
        df = self.weather_df
        n_years = len(df.select(pl.col('year').unique()).collect())

        high_extrema_temperature = param['high_extrema_temperature']
        high_extrema_exposure_days = param['high_extrema_exposure_days']
        low_extrema_temperature = param['low_extrema_temperature']
        low_extrema_exposure_days = param['low_extrema_exposure_days']

        ret = []

        # 생육한계 최고온도 & 노출일수
        burn_exposed_years = df.sort(['year', 'doy'])\
            .filter(
                (pl.col('tmax') > high_extrema_temperature) &
                (pl.col('doy') >= start_doy) &
                (pl.col('doy') <= end_doy)
            )\
            .groupby(
                (pl.col('doy').diff(1).fill_null(1) != 1).cumsum()
                .alias('consecutive_doys')
            )\
            .agg([
                pl.first('year'),
                pl.count('doy').alias('exposed_days')
            ])\
            .filter(pl.col('exposed_days') >= high_extrema_exposure_days)\
            .select(pl.col('year').unique())\
            .collect()

        if len(burn_exposed_years) / n_years >= 0.3:
            ret.append({
                'title': '재배가능성 낮음',
                'type': '고온해 위험',
                'message': f"""생육한계 최고온도 {
                    high_extrema_temperature
                }℃ 초과의 온도에 연속 {
                    high_extrema_exposure_days
                }일 이상 노출된 년도의 수가 전체 기상자료의 30% 이상입니다."""
            })

        # 생육한계 최저온도 & 노출일수
        cold_exposed_years = df.sort(['year', 'doy'])\
            .filter(
                (pl.col('tmin') < low_extrema_temperature) &
                (pl.col('doy') >= start_doy) &
                (pl.col('doy') <= end_doy)
            )\
            .groupby(
                (pl.col('doy').diff(1).fill_null(1) != 1).cumsum()
                .alias('consecutive_doys')
            )\
            .agg([
                pl.first('year'),
                pl.count('doy').alias('exposed_days')
            ])\
            .filter(pl.col('exposed_days') >= low_extrema_exposure_days)\
            .select(pl.col('year').unique())\
            .collect()
        if len(cold_exposed_years) / n_years >= 0.3:
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
        df = self.gdd_weather_df
        ref_data = self.calculate_first_priority_params()

        doys = self.calculate_doy_hyperparam(
            param['milestone'],
            ref_data
        )['doy']
        cond = param['condition']

        variable = cond['variable']
        danger_temperature = cond['temperature']
        operator = cond['operator']

        if operator == 'ge':
            liability = \
                df.filter(
                    (pl.col('doy') >= doys[0]) & (pl.col('doy') <= doys[1]) &
                    (pl.col(variable) >= danger_temperature)
                ).collect().shape[0] > 0

        elif operator == 'gt':
            liability = \
                df.filter(
                    (pl.col('doy') >= doys[0]) & (pl.col('doy') <= doys[1]) &
                    (pl.col(variable) > danger_temperature)
                ).collect().shape[0] > 0

        elif operator == 'eq':
            liability = \
                df.filter(
                    (pl.col('doy') >= doys[0]) & (pl.col('doy') <= doys[1]) &
                    (pl.col(variable) == danger_temperature)
                ).collect().shape[0] > 0

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
        )['doy']
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
            'ranged': True,
            'doy': [self.start_doy, self.end_doy]
        }

    @property
    def progress(self):
        df = self.gdd_weather_df
        _doy = max(self.start_doy - 1, 1)
        ret = df.filter(
            (pl.col('doy') >= _doy) & (pl.col('doy') <= self.end_doy)
        )\
            .select([
                pl.col('doy'),

                (pl.col('tavg_dev').cumsum() / self.growth_gdd)
                .clip_max(1).round(2).alias('progress')
            ])\
            .unique(subset=['progress'])\
            .sort('doy')\
            .collect()

        return {
            'type': 'progress',
            'name': '생육진행도',
            'doy': ret['doy'].to_list()
        }

    def parse_params(self, params):
        for param in params:
            if isinstance(param, list):
                yield from param
            else:
                yield param

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
        for param in self.parse_params(self.doy_hyperparams):
            if 'events' not in param['expose_to']:
                continue
            event = self.calculate_doy_hyperparam(param, ref)
            events.append(event)
        return events

    @property
    def water_level(self):
        return []

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
        for param in self.parse_params(self.doy_hyperparams):
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

        for param in self.parse_params(self.warning_hyperparams):
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

        for param in self.parse_params(self.doy_hyperparams):
            hyper_params.append({
                **param,
                'editable': False
            })

        return _parameters + hyper_params
