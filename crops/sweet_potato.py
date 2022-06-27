from .base import BaseCropModel


class SweetPotatoModel(BaseCropModel):
    name = '고구마'
    _type = 'sweetPotato'
    color = '#904e50'
    key = 'sweetPotato'
    gdd_method = 'm3'
    division = 'agricultural'
    display_order = 5

    # 기본값
    default_start_doy = 131  # 삽식

    # 재배관련 - parameter
    base_temperature = 15.5
    max_dev_temperature = 38
    allow_multiple_cropping = True

    # 재배관련 - hyperparameter
    growth_gdd = 1462  # 생육 완료
    harvest_gdd = 1462  # 수확

    # 재배관련 - warnings
    high_extrema_temperature = 32.2
    high_extrema_exposure_days = 15
    low_extrema_temperature = 15
    low_extrema_exposure_days = 30

    @property
    def events(self):
        ret = super().events

        # events 계산
        start_doy = self.start_doy  # 삽식
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]

        dedicated_events = [
            {'type': 'sow', 'name': '파종', 'data': start_doy - 60},  # 삽식 60일 전
            {'type': 'transplant', 'name': '삽식', 'data': start_doy},
            {'type': 'harvest_range', 'name': '수확', 'data': harvest_range}
        ]
        ret.extend(dedicated_events)
        return ret

    @property
    def schedules(self):
        ret = super().schedules

        # schedules 계산
        start_doy = self.start_doy  # 삽식
        harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
        harvest_range = [harvest - 3, harvest + 7]

        ret.extend([
            {
                'type': 'sow',
                'name': '파종',
                'data': start_doy - 60,
                'text': ''
            },
            {
                'type': 'transplant',
                'name': '삽식',
                'data': start_doy,
                'text': ''
            },
            {
                'type': 'harvest_range',
                'name': '수확',
                'data': harvest_range,
                'text': ''
            },
        ])
        return ret
