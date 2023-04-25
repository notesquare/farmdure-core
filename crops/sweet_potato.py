from .base import BaseCropModel


class SweetPotatoModel(BaseCropModel):
    name = '고구마'
    _type = 'sweetPotato'
    color = '#904e50'
    key = 'sweetPotato'
    allow_multiple_cropping = True
