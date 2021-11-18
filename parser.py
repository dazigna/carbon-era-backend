import csv
import pandas as pd
import numpy as np
import requests as r
from unidecode import unidecode
from re import sub
from pdb import set_trace as bp
from collections import ChainMap
import json

#convert latin string to snake_case
def normalize(string):
  newString = unidecode(string.lower())
  return sub("[^0-9a-zA-Z]+", "_", newString)

#Assign types to string written types
def normalizeType(string):
  if string == 'string':
    return pd.StringDtype()
  elif string == 'number':
    return np.float64
  elif string == 'integer':
    return pd.Int32Dtype() #Support for Non existing integer in the table
  else:
    return bool

def cleanUpSchema(listOfDict, keyToEvaluate, keysToKeep, keysToRemove):
  return  [{k:dict.get(k) for k in keysToKeep} for dict in listOfDict if not any(key.lower() in dict.get(keyToEvaluate).lower() for key in keysToRemove)]

#Cleaned up schema
# Get Schema from API
dbSchema = r.get('https://data.ademe.fr/data-fair/api/v1/datasets/base-carbone(r)/').json()['schema']


keysToKeep = ['key', 'x-originalName', 'type', 'enum', 'format']
keysToRemove = ['_i', '_rand', '_id']
charsToCheck = ["'", "-"]

#Original schema
originalSchema = cleanUpSchema(dbSchema, 'key', keysToKeep, keysToRemove)
#Normalize 
for dict in originalSchema:
  dict['key'] = normalize(dict.get('key'))
dataColumnsOriginal = [dict.get('key') for dict in originalSchema]
assert not(any([s for s in dataColumnsOriginal if any(xs in s for xs in charsToCheck)]))


#Cleaned up schema
keysToRemove += ['Code_gaz_', 'Valeur_gaz_', '_espagnol', 'qualite', 'commentaire', 'nom_poste_', 'contributeur', 'source', 'reglementation', 'programme', 'date']
cleanedUpSchema = cleanUpSchema(originalSchema, 'key', keysToKeep, keysToRemove)
#Normalize resulting list of objects
for dict in cleanedUpSchema:
  dict['key'] = normalize(dict.get('key'))
  dict['type'] = normalizeType(dict.get('type'))

#Extracts columns names
dataColumnsClean = [dict.get('key') for dict in cleanedUpSchema]

#Extracts types
listTypes = [{dict.get('key'):dict.get('type') for k in keysToKeep} for dict in cleanedUpSchema]

#Condition types to become a dict instead of list of dict for Pandas
dataTypes = {k:v for element in listTypes for k,v in element.items()}

#Extract all enums
enumList = [{dict.get('key'):dict.get('enum')} for dict in cleanedUpSchema]

#Read original CSV with Original col name
dbOriginal = pd.read_csv('BaseCarbonev202.csv', header=0, names=dataColumnsOriginal, delimiter=';', encoding='latin-1', decimal=',').convert_dtypes()

dbClean = pd.DataFrame(dbOriginal,columns=dataColumnsClean)

#Select only valid elements
dbCleanValid = dbClean.loc[
  (dbClean['total_poste_non_decompose']>0) &
  (dbClean['statut_de_l_element'].isin(["Valide générique","Valide spécifique"])) & 
  (dbClean["unite_francais"].str.contains('kgCO2e'))
  ]

listUnit = pd.DataFrame(dbCleanValid['unite_francais'].unique(), columns=['units'])

jsonDb = dbCleanValid.to_json(orient='records', indent=4)
with open('dbcarbon.json', 'w', encoding='utf-8') as f:
  f.write(jsonDb)

with open('dbCarbonEnums.json', 'w', encoding='utf-8') as f:
  json.dump(enumList,f, indent=4)

jsonUnit = listUnit.to_json(orient='columns', indent=4)
with open('dbCarbonUnits.json', 'w', encoding='utf-8') as f:
  f.write(jsonUnit)