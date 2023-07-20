from collections import OrderedDict

from .rice import (
    MiddleLateMatureRiceModel,
    MiddleMatureRiceModel,
    EarlyMatureRiceModel
)
from .cabbage import (
    SpringCabbageModel,
    AutumnCabbageModel,
)
from .chili import ChiliModel
from .wheat import WheatModel
from .corn import CornModel
from .barley import BarleyModel
from .sweet_potato import SweetPotatoModel
from .potato import PotatoModel
from .onion import OnionModel
from .garlic import GarlicModel
from .radish import RadishModel
from .adzuki import AdzukiModel
from .sesame import SesameModel
from .bean import BeanModel


CropModels = [
    MiddleLateMatureRiceModel,
    MiddleMatureRiceModel,
    EarlyMatureRiceModel,
    SpringCabbageModel,
    AutumnCabbageModel,
    ChiliModel,
    WheatModel,
    CornModel,
    BarleyModel,
    SweetPotatoModel,
    PotatoModel,
    OnionModel,
    GarlicModel,
    RadishModel,
    AdzukiModel,
    SesameModel,
    BeanModel,
]

CropModelsByCategory = OrderedDict([
    ('식량작물', OrderedDict([
        ('벼', [
            EarlyMatureRiceModel,
            MiddleMatureRiceModel,
            MiddleLateMatureRiceModel
        ]),
        ('보리', [BarleyModel]),
        ('콩', [BeanModel]),
        ('고구마', [SweetPotatoModel]),
        ('감자', [PotatoModel]),
        ('옥수수', [CornModel]),
        ('밀', [WheatModel]),
        ('팥', [AdzukiModel]),
    ])),
    ('원예작물', OrderedDict([
        ('고추', [ChiliModel]),
        ('마늘', [GarlicModel]),
        ('양파', [OnionModel]),
        ('배추', [
            SpringCabbageModel,
            AutumnCabbageModel
        ]),
        ('무', [RadishModel]),
    ])),
    ('특용작물', OrderedDict([
        ('참깨', [SesameModel])
    ]))
])

cropNameByType = {
    'rice': '벼',
    'adzuki': '팥',
    'barley': '보리',
    'bean': '콩',
    'cabbage': '배추',
    'chili': '고추',
    'corn': '옥수수',
    'garlic': '마늘',
    'onion': '양파',
    'potato': '감자',
    'radish': '무',
    'sesame': '참깨',
    'sweetPotato': '고구마',
    'wheat': '밀'
}
