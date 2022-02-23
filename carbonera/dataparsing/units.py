from dataclasses import dataclass, field, fields
from typing import List

'''
Type: str
variables: [
  {
    symbol: kg
    values: [kg]
  },
  {
    symbol: t
    values: [tonne, t]
  },
]
'''

@dataclass
class UnitVariable:
  symbol: str
  values: List[str]

  def toDict(self):
      return {'symbol': self.symbol, 'values': self.values}

@dataclass
class Unit:
  name: str
  variables: List[UnitVariable]

  def toDict(self):
    return {'name': self.name, 'variables': [v.toDict() for v in self.variables]}

@dataclass
class Units:
  UnitVariable('kg', ['kg'])
  mass: Unit = field(default=Unit(
    'MASS',
    [
      UnitVariable('kg', ['kg']),
      UnitVariable('t', ['t', 'tonne', 'tonnes'])
    ]
  ))
  energy: Unit = field(default=Unit(
    'ENERGY', 
    [
        UnitVariable('GJ', ['Gj',]),
        UnitVariable('MJ', ['MJ',]),
        UnitVariable('tep', ['tep']),
        UnitVariable('kWh', ['kWh'])
    ]
  ))    
  volume: Unit = field(default=Unit(
    'VOLUME',
    [
        UnitVariable('l', ['l', 'litre']),
        UnitVariable('m3', ['m3', 'm³']),
        UnitVariable('ml', ['ml'])
    ]
  ))

  area: Unit = field(default=Unit(
    'AREA',
    [
        UnitVariable('ha', ['ha']),
        UnitVariable('m2', ['m2', 'm²'])
    ]
  ))
  distance: Unit = field(default=Unit(
    'DISTANCE',
    [
        UnitVariable('m', ['m']),
        UnitVariable('km', ['km'])
    ]
  ))
  time: Unit = field(default=Unit(
    'TIME',
    [
        UnitVariable('h', ['h', 'heure', 'heures']),
    ]
    ))
  quantity: Unit = field(default=Unit(
    'QUANTITY', 
    [
        UnitVariable('unité', ['unité']),
        UnitVariable('repas', ['repas']),
        UnitVariable('euro', ['euro', 'euro dépensé']),
        UnitVariable('livre', ['livre']),
        UnitVariable('personne.mois', ['personne.mois']),
        UnitVariable('passager.km', ['passager.km']),
        UnitVariable('peq.km', ['peq.km']),
        UnitVariable('appareil', ['appareil']),

    ]
    ))

  def supportedUnits(self):
    units = [getattr(self, field.name) for field in fields(self) if issubclass(field.type, Unit)]
    return [u.toDict() for u in units]