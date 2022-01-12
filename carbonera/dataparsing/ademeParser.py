from dataclasses import dataclass, field, fields
from typing import Dict, List
import pandas as pd
import numpy as np
import requests as r
from requests.api import get
from unidecode import unidecode
import re
# from re import sub, escape, match, search, compile
import json
import argparse
from pathlib import Path
from timeit import default_timer as timer
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
        UnitVariable('euro', ['euro,']),
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

class AdemeParser():
  def __init__(self):
    self.schemaUrl = 'https://data.ademe.fr/data-fair/api/v1/datasets/base-carbone(r)/'
    self.databaseUrl = 'https://data.ademe.fr/data-fair/api/v1/datasets/base-carbone(r)/full'
    self.carbonCategories = []
    self.carbonUnits = []
    self.carbonEnums = []
    self.carbonDf = pd.DataFrame()
    self.carbonDb = []
    print(f'Init Ademe parser with schema URL {self.schemaUrl} and databaseUrl {self.databaseUrl}')
    return

  #convert latin string to snake_case
  def normalizeString(self, string):
    newString = unidecode(string.lower())
    return re.sub("[^0-9a-zA-Z]+", "_", newString)

  #Assign types to string written types
  def normalizeType(self, string):
    if string == 'string':
      return pd.StringDtype()
    elif string == 'number':
      return np.float64
    elif string == 'integer':
      return pd.Int32Dtype() #Support for Non existing integer in the table
    else:
      return bool

  def normalizeKeys(self, listOfDict, keysToNormalize):
    
    for dict in listOfDict:
      for k in keysToNormalize:
        dict[k] = self.normalizeString(dict.get(k))
    
    return listOfDict

  def cleanUpSchema(self, listOfDict, keyToEvaluate, keysToKeep, keysToRemove):
    cleanedUp = [{k:dict.get(k) for k in keysToKeep} for dict in listOfDict if not any(key.lower() in dict.get(keyToEvaluate).lower() for key in keysToRemove)]
    
    return cleanedUp

  def recurseCategories(self, categories, listOfdicts, parent=None): 
    if categories.columns.size == 0:
      return

    uniqueCategories = categories.iloc[:,0].dropna().unique()

    for uniqueCat in uniqueCategories:
      query = categories.loc[categories.iloc[:,0].str.match(re.escape(uniqueCat), na=False)].drop(columns=categories.columns[0], axis=1)

      if query.columns.size == 0 or query.isna().all().all():
        continue

      listOfdicts.append({"parent": parent, "name": uniqueCat, "subCategories": query.iloc[:,0].dropna().unique().tolist()})

      self.recurseCategories(query, listOfdicts, uniqueCat)

  # Create dataframe for categories and build a parent-child model -> Adjacent list model
  def createCategories(self, dataFrame):
    # lower case, split and expand categories table
    dataFrameSplitCategories = dataFrame['categories'].str.lower().str.split('>', expand=True).add_prefix('cat')
    #Trim whitespaces
    dataFrameSplitCategories = dataFrameSplitCategories.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    categories = []
    self.recurseCategories(dataFrameSplitCategories, categories)

    return categories

  def normalizeUnit(self, row, denominatorColName, unitColName, supportedUnits):
    row = row.copy()
    
    # Split denominator in case of spaces 
    splitDenom = row[denominatorColName].split()
    
    unitName = None
    unitSymbol = None
    energyType = ['PCI', 'PCS']
    unitEnergyType = None
    for unit in supportedUnits:
        unitVariables = unit.get('variables')
        for v in unitVariables:
            for s in v.get('values'):
                for d in splitDenom:
                    if d.upper() in energyType:
                        unitEnergyType = d
                    if re.match(rf'(?i)(?<!\S){s}(?!\S)', re.escape(d), re.IGNORECASE):
                        unitName = unit.get('name')
                        unitSymbol = v.get('symbol')
                        # print('breaking exec')
                        break
                else:
                    continue
                break
            else: 
                continue
            break
      
      # set(supportedUnits[0].get('values')).intersection(set(row[denominatorColName].split()))
        

    # unitMatch = next((item for item in supportedUnits if any(s.lower() in row[denominatorColName].lower() for s in item.get('values'))), None)
# set(supportedUnits[0].get('values')).intersection(set(row[denominatorColName].split()))
    # unitMatch = next((item for item in supportedUnits if any(re.match(rf'(?i)(?<!\S){s}(?!\S)', re.escape(row[denominatorColName]), re.IGNORECASE) for s in item.get('values'))), None)
    # match(rf'(?i)(?<!\S){}(?!\S)', escape(row[denominatorColName]), re.IGNORECASE)
    if unitName:
      # denominator_clean = next((item for item in unitMatch.get('values') if item.lower() in row[denominatorColName].lower()), None)
      row['unit_type'] = unitName  # unitMatch.get('name')
      row['unit_name_clean'] = row[unitColName].replace(row[denominatorColName], unitSymbol )  #row[unitColName].replace(row[denominatorColName], denominator_clean )
      row['unit_denominator_clean'] = unitSymbol #denominator_clean
      row['unit_energy_type'] = unitEnergyType

    return row
  
  # Create new columns in DF to decompose and normalize units
  # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
  def decomposeAndNormalizedUnits(self, dataFrame, colName):
    df = dataFrame.copy()
    splitUnits = df[colName].str.split("/")
    df.loc[:, 'unit_numerator'] = splitUnits.str[0]
    df.loc[:, 'unit_denominator'] = splitUnits.str[1:].str.join('/')
    
    supportedUnits = Units().supportedUnits()

    return df.apply(self.normalizeUnit, args=('unit_denominator', colName, supportedUnits,), axis=1)    

  def createUnits(self, df):
    return df.loc[:, ('unite_francais', 'unit_numerator', 'unit_denominator', 'unit_type', 'unit_name_clean', 'unit_denominator_clean', 'unit_energy_type')].drop_duplicates().sort_values('unit_type')
  
  def createEnums(self, schema):
    return [{dict.get('key'):dict.get('enum')} for dict in schema]
  
  def parse(self):
    print(f'Querying Schema ...')
    # Get Schema from API
    databaseSchemaRaw = r.get(self.schemaUrl).json()['schema']

    print(f'Cleaning up schema ...')
    #1. First we need to extract the original Schema and clean it up
    #Original schema
    keysToKeep = ['key', 'x-originalName', 'type', 'enum', 'format']
    keysToRemove = ['_i', '_rand', '_id']
    keyToEvaluate = 'key'
    keysToNormalize = ['key']
    schemaDirty = self.cleanUpSchema(databaseSchemaRaw, keyToEvaluate=keyToEvaluate, keysToKeep=keysToKeep, keysToRemove=keysToRemove)
    
    schemaDirty = self.normalizeKeys(schemaDirty, keysToNormalize)
    
    dataColumnsDirty = [dict.get('key') for dict in schemaDirty]
    
    charsToCheck = ["'", "-"]
    assert not(any([s for s in dataColumnsDirty if any(xs in s for xs in charsToCheck)]))
    
    print(f'Creating new schema ...')
    #2. Second we need to create the schema we want to keep, by filtering out the useless values
    keysToRemove += ['Code_gaz_', 'Valeur_gaz_', '_espagnol', 'qualite', 'commentaire', 'nom_poste_', 'contributeur', 'source', 'reglementation', 'programme', 'date']
    keysToNormalize += ['type']

    schema = self.cleanUpSchema(schemaDirty, keyToEvaluate=keyToEvaluate, keysToKeep=keysToKeep, keysToRemove=keysToRemove)
    #Normalize resulting list of objects
    self.normalizeKeys(schema, keysToNormalize)
    
    #Extracts columns names
    dataColumns = [dict.get('key') for dict in schema]

    print(f'Loading data from URL and filtering ...')
    # Read original CSV from API
    dataFrameDirty = pd.read_csv(self.databaseUrl, header=0, names=dataColumnsDirty, delimiter=';', encoding='latin-1', decimal=',').convert_dtypes()
    
    #Filter out original dataframe with clean schema
    dataFrameClean = pd.DataFrame(dataFrameDirty, columns=dataColumns)

    print(f'Creating valid outputs ...')
    #Units we don't support
    unitsToExclude = [
      'kgCO2e/tonne de clinker',
      'kgCO2e/kg NTK',
      'kgCO2e/kg DCO éliminée',
      'kgCO2e/kg BioGNC',
      'kgCO2e/tonne de N',
      'kgCO2e/kgH2/100km',
      'kgCO2e/kg de matière active',
      'kgCO2e/kg de cuir traité',
      'kgCO2e/kgH2',
      'kgCO2e/tonne de K2O',
      'kgCO2e/keuro',
      'kgCO2e/tonne de P2O5',
      'kgCO2e/kg d\'azote épandu',
      'kgCO2e/tonne produites',
      'kgCO2e/m² SHON',
      'kgCO2e/m²',
      'kgCO2e/m2 SHON',
      'kgCO2e/m² de paroi',
      'kgCO2e/m3.km',
      'kgCO2e/t.km',
      'kgCO2e/kWhPCI',
      'kgCO2e/kWhPCS',
      'kgCO2e/ha.an',
      'kgCO2e/tonne.km',
      'kgCO2e/m² de toiture',
      'kgCO2e/m² de sol',
      '100 feuilles A4',
      'plant',
      ]

    #Select only valid elements
    self.carbonDf = dataFrameClean.loc[
      (dataFrameClean['total_poste_non_decompose']>0) &
      (dataFrameClean['statut_de_l_element'].isin(["Valide générique","Valide spécifique"])) & 
      (dataFrameClean["unite_francais"].str.contains('kgCO2e')) &
      (dataFrameClean["unite_francais"].isin(unitsToExclude) == False)
      ]
    
    self.carbonDf = self.decomposeAndNormalizedUnits(self.carbonDf, 'unite_francais')
    
    # Create units

    start = timer()
    self.carbonUnits = self.createUnits(self.carbonDf)
    end = timer()
    print(f'computed in {end-start}')
    print(self.carbonUnits)

    writableDf = self.carbonDf.replace({np.nan: None})
    
    self.carbonDb = writableDf.to_dict(orient='records')
    #Create Enums
    self.carbonEnums = self.createEnums(schema)

  

    #Create categories
    dataFrameCategories = pd.DataFrame(self.carbonDf['code_de_la_categorie'].unique(), columns=['categories'])
    self.carbonCategories = self.createCategories(dataFrameCategories)

  def writeToJson(self, fileName, jsonData):
    print(f'Writing json file: {fileName}')
    with open(fileName, 'w', encoding='utf-8') as f:
      json.dump(jsonData, f, indent=4)

  def writeToFiles(self, path=None):
    writableDf = self.carbonDf.replace({np.nan: None})

    # JSON Writing
    self.writeToJson(Path(path, 'carbonDatabase.json'), self.carbonDb)
    self.writeToJson(Path(path, 'carbonUnits.json'), self.carbonUnits)
    self.writeToJson(Path(path, 'carbonEnums.json'), self.carbonEnums)
    self.writeToJson(Path(path, 'carbonCategories.json'), self.carbonCategories)

  
def main():
  argParser = argparse.ArgumentParser(description="Parse and clean up Ademe data")
  argParser.add_argument('-o', type=str, dest='filePath', default='.', help='output directory')
  args = argParser.parse_args()

  if args.filePath:
    print(f'Files will be written to {args.filePath}')
  
  dataParser = AdemeParser()
  dataParser.parse()
  dataParser.writeToFiles(args.filePath)

if __name__ == '__main__':
  main()