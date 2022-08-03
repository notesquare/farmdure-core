from .rice import RiceModel


class EarlyMatureRiceModel(RiceModel):
    name = '조생종 벼'
    _type = 'rice'
    parent_key = 'rice'
    key = 'earlyMatureRice'
