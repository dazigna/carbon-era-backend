import pandas as pd
import numpy as np
import requests as r
from unidecode import unidecode
from re import sub, escape
import json
import argparse
from pathlib import Path

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
    return sub("[^0-9a-zA-Z]+", "_", newString)

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

  def testRecurseCategories(self, categories, listOfdicts):
    uniqueCategories = categories.iloc[:,0].dropna().unique()

    for uniqueCat in uniqueCategories:
      query = categories.loc[categories.iloc[:,0].str.match(escape(uniqueCat), na=False)].drop(columns=categories.columns[0], axis=1)


  def recurseCategories(self, categories, listOfdicts, parent=None): 
    if categories.columns.size == 0:
      return

    uniqueCategories = categories.iloc[:,0].dropna().unique()

    for uniqueCat in uniqueCategories:
      query = categories.loc[categories.iloc[:,0].str.match(escape(uniqueCat), na=False)].drop(columns=categories.columns[0], axis=1)

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

  # Create Series to extract units and split each unit into numerator and denominator
  def createUnits(self, dataFrame):
    dataFrame['numerator'] = dataFrame['name'].str.split("/").str[0]
    dataFrame['denominator'] = dataFrame['name'].str.split("/").str[1]
    return dataFrame.to_dict(orient='records')

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
    #Select only valid elements
    self.carbonDf = dataFrameClean.loc[
      (dataFrameClean['total_poste_non_decompose']>0) &
      (dataFrameClean['statut_de_l_element'].isin(["Valide générique","Valide spécifique"])) & 
      (dataFrameClean["unite_francais"].str.contains('kgCO2e'))
      ]
    writableDf = self.carbonDf.replace({np.nan: None})
    self.carbonDb = writableDf.to_dict(orient='records')
    #Create Enums
    self.carbonEnums = self.createEnums(schema)

    # Create units
    dfUnits = pd.DataFrame(self.carbonDf['unite_francais'].unique(), columns=['name'])
    self.carbonUnits = self.createUnits(dfUnits)

    #Create categories
    dataFrameCategories = pd.DataFrame(self.carbonDf['code_de_la_categorie'].unique(), columns=['categories'])
    self.carbonCategories = self.createCategories(dataFrameCategories)

  def writeToJson(self, fileName, jsonData):
    print(f'Writing json file: {fileName}')
    with open(fileName, 'w', encoding='utf-8') as f:
      json.dump(jsonData, f, indent=4)

  def writeToFiles(self, path=None):
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