import pandas as pd
import re
from pathlib import Path

from .normalizer import Normalizer
from .cacheManager import CacheManager
from .fileIO import FileIOManager

class AdemeParser():
  def __init__(self):
    self.carbonUnits = pd.DataFrame()
    self.carbonDf = pd.DataFrame()
    self.carbonDb = []
    self.carbonCategories = []
    self.carbonUnitsJson = []
    self.carbonEnums = []
    self.carbonContributors = []
    self.normalizer = Normalizer()
    self.cacheManager = CacheManager()

    return

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
        
  def createUnits(self, df):
    # return df.loc[:, ('unite_francais', 'unit_numerator', 'unit_denominator', 'unit_type', 'unit_name_clean', 'unit_denominator_clean', 'unit_energy_type')].drop_duplicates().sort_values('unit_type')
    return df.loc[:, ('unit_type', 'unit_name_clean', 'unit_numerator', 'unit_denominator_clean', 'unit_energy_type')].drop_duplicates().sort_values('unit_type')

  def createEnums(self, schema):
    return [{dict.get('key'):dict.get('enum')} for dict in schema]
  
  def createContributors(self, df):
    return df.loc[:, 'contributeur'].drop_duplicates().to_list()

  def parse(self):
    databaseSchemaRaw = self.cacheManager.getSchema()

    print(f'Cleaning up schema ...')
    #1. First we need to extract the original Schema and clean it up
    #Original schema
    keysToKeep = ['key', 'x-originalName', 'type', 'enum', 'format']
    keysToRemove = ['_i', '_rand', '_id']
    keyToEvaluate = 'key'
    keysToNormalize = ['key']
    schemaDirty = self.cleanUpSchema(databaseSchemaRaw, keyToEvaluate=keyToEvaluate, keysToKeep=keysToKeep, keysToRemove=keysToRemove)
    
    schemaDirty = self.normalizer.normalizeKeys(schemaDirty, keysToNormalize)
    
    dataColumnsDirty = [dict.get('key') for dict in schemaDirty]
    
    charsToCheck = ["'", "-"]
    assert not(any([s for s in dataColumnsDirty if any(xs in s for xs in charsToCheck)]))
    
    print(f'Creating new schema ...')
    #2. Second we need to create the schema we want to keep, by filtering out the useless values
    keysToRemove += ['Code_gaz_', 'Valeur_gaz_', '_espagnol', 'qualite', 'commentaire', 'nom_poste_', 'source', 'reglementation', 'programme', 'date']
    keysToNormalize += ['type']

    schema = self.cleanUpSchema(schemaDirty, keyToEvaluate=keyToEvaluate, keysToKeep=keysToKeep, keysToRemove=keysToRemove)
    #Normalize resulting list of objects
    self.normalizer.normalizeKeys(schema, keysToNormalize)
    
    #Extracts columns names
    dataColumns = [dict.get('key') for dict in schema]

    print(f'Loading data from URL and filtering ...')
    # Read original CSV from API
    dataFrameDirty = pd.read_csv(self.cacheManager.getDB(), header=0, names=dataColumnsDirty, delimiter=';', encoding='latin-1', decimal=',').convert_dtypes()
    
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
      'kgCO2e/100 feuilles A4',
      'kgCO2e/plant',
      ]

    #Select only valid elements
    self.carbonDf = dataFrameClean.loc[
      (dataFrameClean['total_poste_non_decompose']>0) &
      (dataFrameClean['statut_de_l_element'].isin(["Valide générique","Valide spécifique"])) & 
      (dataFrameClean["unite_francais"].str.contains('kgCO2e')) &
      (dataFrameClean["unite_francais"].isin(unitsToExclude) == False)
      ]
    
    self.carbonDf = self.normalizer.normalizeName(self.carbonDf)
    self.carbonDf = self.normalizer.decomposeAndNormalizedUnits(self.carbonDf, 'unite_francais')

    # Create units
    self.carbonUnits = self.createUnits(self.carbonDf)
    
    self.carbonUnitsJson = self.carbonUnits.where(pd.notnull(self.carbonUnits), None).to_dict(orient='records')
    
    # Properly replace NA and NaN
    self.carbonDb = self.carbonDf.where(pd.notnull(self.carbonDf), None).to_dict(orient='records')
    #Create Enums
    self.carbonEnums = self.createEnums(schema)

    self.carbonContributors = self.createContributors(self.carbonDf)

    #Create categories
    dataFrameCategories = pd.DataFrame(self.carbonDf['code_de_la_categorie'].unique(), columns=['categories'])
    self.carbonCategories = self.createCategories(dataFrameCategories)

  def writeToFiles(self, path=None):
    # JSON Writing
    FileIOManager().writeToJson(Path(path, 'carbonDatabase.json'), self.carbonDb)
    FileIOManager().writeToJson(Path(path, 'carbonUnits.json'), self.carbonUnitsJson)
    FileIOManager().writeToJson(Path(path, 'carbonEnums.json'), self.carbonEnums)
    FileIOManager().writeToJson(Path(path, 'carbonCategories.json'), self.carbonCategories)
    FileIOManager().writeToJson(Path(path, 'carbonContributors.json'), self.carbonContributors)