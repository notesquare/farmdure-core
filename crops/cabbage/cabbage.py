from xml.sax.handler import property_encoding
from ..base import BaseCropModel


class CabbageModel(BaseCropModel):
    name = '배추'
    _type = 'cabbage'
    division = 'horticultural'

    # 재배관련 - warnings
    # 1. 한계온도 & 노출일수
    high_extrema_temperature = 30
    high_extrema_exposure_days = 5
    low_extrema_temperature = 5
    low_extrema_exposure_days = 5

    # 2. 수확은 정식에서부터 45~75일 사이에 위치

    @property
    def schedules(self):
        ret = super().schedules

        start_doy = self.start_doy

        # 투비 시기
        fertilize1 = start_doy + 15
        fertilize2 = start_doy + 30
        fertilize3 = start_doy + 45

        ret.extend([
            {
                'type': 'fertilize',
                'name': '추비 1차',
                'data': fertilize1,
                'text': ''
            },
            {
                'type': 'fertilize',
                'name': '추비 2차',
                'data': fertilize2,
                'text': ''
            },
            {
                'type': 'fertilize',
                'name': '추비 3차',
                'data': fertilize3,
                'text': ''
            }
        ])
        return ret

    @property
    def warnings(self):
        ret = super().warnings

        # 1. 수확은 정식에서부터 45~75일 사이에 위치
        start_doy = self.start_doy  # 정식기

        if hasattr(self, 'harvest_gdd'):
            harvest = self.get_event_end_doy(start_doy, self.harvest_gdd)
            harvest_range = [harvest - 3, harvest + 7]
        elif hasattr(self, 'harvest_gdd_range'):
            harvest_range = [
                self.get_event_end_doy(start_doy, gdd)
                for gdd in self.harvest_gdd_range
            ]
            if harvest_range[1] - harvest_range[0] \
                    > self.harvest_max_doy_range:
                harvest_range[1] = harvest_range[0] + \
                    self.harvest_max_doy_range

        harvestable_range = [start_doy + 45, start_doy + 75]  # 45~75일
        if harvest_range[1] < harvestable_range[0]:
            ret.append({
                'title': '재배가능성 낮음',
                'type': '재배불가능',
                'message': '최소 생육기간 45일 이하입니다.'
            })
        elif harvest_range[0] > harvestable_range[1]:
            ret.append({
                'title': '재배가능성 낮음',
                'type': '재배불가능',
                'message': '최대 생육기간 75일 이상입니다.'
            })

        return ret
