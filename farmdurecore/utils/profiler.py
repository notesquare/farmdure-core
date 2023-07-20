"""
functions are for making simulation results
to be more human friendly
"""

from datetime import datetime


OP_STR = {
  'ge': '이상',
  'gt': '초과',
  'e': '동일',
  'le': '이하',
  'lt': '미안',
}

VAR_STR = {
  'tmax': '최고기온',
  'tmin': '최저기온',
  'tavg': '평균기온',
}

EXPOSURE_STR = {
  'events': '생육단계',
  'schedules': '농작업일정',
  'water_level': '관개',
}


def get_human_time(doy):
    year = 4  # always leap year
    ts = datetime(year, 1, 1).timestamp() + (doy - 1) * 24 * 3600
    dt = datetime.fromtimestamp(ts)
    return f'{dt.month}월 {dt.day}일'


def get_event_start_doy(crop_model, param, method):
    if method == 'GDD':
        event = crop_model.calculate_gdd_hyperparam(param)
    elif method == 'DOY':
        ref = crop_model.calculate_first_priority_params()
        event = crop_model.calculate_doy_hyperparam(param, ref)

    doys = event['doy']
    start_doy = doys[0] if isinstance(doys, list) else doys
    return start_doy


def iter_params(params):
    for param in params:
        if not isinstance(param, list):
            yield param
        else:
            iter_params(param)


def profile_doy_hyperparams(crop_model):
    ret = []
    for param in iter_params(crop_model.doy_hyperparams):
        text = param.get('text', '')

        value = param['value']
        ref = param['ref']
        period = param.get('period')
        expose_to = param.get('expose_to', [])

        _repr_value = []
        for _ref, _idx, _val in zip(
            ref,
            param.get('index', [None]*len(ref)),
            value
        ):
            filtered_ret = filter(
                lambda x: x['type'] == _ref,
                crop_model.first_priority_hyperparams
            )

            _prefix = next(filtered_ret)
            prefix = _prefix['name']
            suffix = ''
            if _idx == 0:
                suffix = ' 시작'
            if _idx == 1:
                suffix = ' 종료'

            if _val == 0:
                _repr_value.append(f'{prefix}')
            else:
                postfix = '전' if _val < 0 else '후'
                _repr_value.append(f'{prefix}{suffix} {abs(_val)}일 {postfix}')
            repr_value = ' ~ '.join(_repr_value)

        if isinstance(value, list):
            period_type = '최대'  # upper bound
        else:
            period_type = '최소'  # under bound

        _ret = {
            'name': param['name'],
            'value': repr_value
        }

        if len(text) != 0:
            _ret['text'] = text

        if period is not None:
            _ret['period'] = f'{period_type} {period}일'

        if len(expose_to) != 0:
            _ret['expose_to'] = [EXPOSURE_STR[k] for k in expose_to]
        ret.append(_ret)
    return ret


def profile_gdd_hyperparams(crop_model):
    ret = []
    for param in iter_params(crop_model.gdd_hyperparams):
        text = param.get('text', '')
        value = param['value']
        period = param.get('period')
        expose_to = param.get('expose_to', [])

        if isinstance(value, list):
            value_repr = ' ~ '.join([str(val) for val in value])
            period_type = '최대'  # upper bound
        else:
            value_repr = str(value)
            period_type = '최소'  # under bound

        _ret = {
            'name': param['name'],
            'value': value_repr
        }

        if len(text) != 0:
            _ret['text'] = text

        if period is not None:
            _ret['period'] = f'{period_type} {period}일'

        if len(expose_to) != 0:
            _ret['expose_to'] = [EXPOSURE_STR[k] for k in expose_to]
        ret.append(_ret)
    return ret


def profile_warning_hyperparams(crop_model):
    ret = []
    for param in iter_params(crop_model.warning_hyperparams):
        method = param['method']

        if method == 'temperature_and_exposure':
            ret.extend([
                {
                    'method': '한계온도 노출일수',
                    'name': '고온해',
                    'text': f'''{
                        param['high_extrema_temperature']
                    }℃ 이상(초과) {
                        param['high_extrema_exposure_days']
                    }일 이상 노출'''
                },
                {
                    'method': '한계온도 노출일수',
                    'name': '동해',
                    'text': f'''{
                        param['low_extrema_temperature']
                    }℃ 이하(미만) {
                        param['low_extrema_exposure_days']
                    }일 이상 노출'''
                },
            ])

        elif method == 'milestone_and_temperature_condition':
            ref = param['milestone']['ref']
            value = param['milestone']['value']

            milestone_rule = []
            for _ref, _idx, _val in zip(
                ref,
                param.get('index', [None]*len(ref)),
                value
            ):
                filtered_ret = filter(
                    lambda x: x['type'] == _ref,
                    crop_model.first_priority_hyperparams
                )

                _prefix = next(filtered_ret)
                prefix = _prefix['name']
                suffix = ''
                if _idx == 0:
                    suffix = ' 시작'
                if _idx == 1:
                    suffix = ' 종료'

                if _val == 0:
                    milestone_rule.append(f'{prefix}')
                else:
                    postfix = '전' if _val < 0 else '후'
                    milestone_rule.append(
                        f'{prefix}{suffix} {abs(_val)}일 {postfix}'
                    )
            milestone_str = ' ~ '.join(milestone_rule)

            cond = param['condition']
            variable = cond['variable']
            temperature = cond['temperature']
            operator = cond['operator']

            warning_title = param['warning_data']['title']
            ret.append({
                'method': '특정생육기 온도조건',
                'name': warning_title,
                'text': (
                    f'{milestone_str} 때 {VAR_STR[variable]} '
                    f'{temperature}℃ {OP_STR[operator]}'
                )
            })

        elif method == 'milestone_length_condition':
            ref = param['milestone']['ref']
            value = param['milestone']['value']

            milestone_rule = []
            for _ref, _idx, _val in zip(
                ref,
                param.get('index', [None]*len(ref)),
                value
            ):
                filtered_ret = filter(
                    lambda x: x['type'] == _ref,
                    crop_model.first_priority_hyperparams
                )

                _prefix = next(filtered_ret)
                prefix = _prefix['name']
                suffix = ''
                if _idx == 0:
                    suffix = ' 시작'
                if _idx == 1:
                    suffix = ' 종료'

                if _val == 0:
                    milestone_rule.append(f'{prefix}')
                else:
                    postfix = '전' if _val < 0 else '후'
                    milestone_rule.append(
                        f'{prefix}{suffix} {abs(_val)}일 {postfix}'
                    )
            milestone_str = ' ~ '.join(milestone_rule)

            cond = param['condition']
            length = cond['length']
            operator = cond['operator']

            warning_title = param['warning_data']['title']
            ret.append({
                'method': '특정생육기 기간조건',
                'name': warning_title,
                'text': f'{milestone_str}이 {length}일 {OP_STR[operator]}'
            })
    return ret
