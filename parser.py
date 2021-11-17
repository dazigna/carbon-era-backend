import csv
import pandas as pd
import numpy as np
import requests as r
from unidecode import unidecode
from re import sub
from pdb import set_trace as bp
from collections import ChainMap

#convert latin string to snake_case
def normalize(string):
  newString = unidecode(string.lower())
  return sub("[^0-9a-zA-Z]+", "_", newString)

#Assign types to string written types
def normalizeType(string):
  if string == 'string':
    return str
  elif string == 'number':
    return np.float64
  elif string == 'integer':
    return pd.Int32Dtype() #Support for Non existing integer in the table
  else:
    return bool


# Get Schema from API
dbSchema = r.get('https://data.ademe.fr/data-fair/api/v1/datasets/base-carbone(r)/').json()['schema']

#Keys to remove - either calculated keys or useless keys
keysToRemove = ['_i', '_rand', '_id', 'Code_gaz_', 'Valeur_gaz_']

#Keys to extract - useful for csv parsing 
extractedKeys =  ['key', 'x-originalName', 'type', 'enum', 'format']

# simple way of filtering to remove the calculated keys -> yields empty objects in place
filteredSchema = [{k: dict.get(k) for k in extractedKeys if dict.get('x-calculated') == None} for dict in dbSchema]

# Completely filter out the useless keys
filteredSchemaFull = [{k:dict.get(k) for k in extractedKeys if dict.get('x-calculated') == None} for dict in dbSchema if not any(xs.lower() in dict.get('key').lower() for xs in keysToRemove)]

#Normalize resulting list of objects
for dict in filteredSchema:
  dict['key'] = normalize(dict.get('key'))
  dict['type'] = normalizeType(dict.get('type'))

#Extracts columns names
dataColumns = [dict.get('key') for dict in filteredSchema]
#Quick test we didn't mess up the normalization
chars = ["'", "-"]
assert not(any([s for s in dataColumns if any(xs in s for xs in chars)]))

#Extracts types
listTypes = [{dict.get('key'):dict.get('type') for k in extractedKeys} for dict in filteredSchema]

#Condition types to become a dict instead of list of dict for Pandas
dataTypes = {k:v for element in listTypes for k,v in element.items()}

breakpoint()
csv = pd.read_csv('BaseCarbonev202.csv', header=0, names=dataColumns, usecols=dataColumns, delimiter=';', encoding='latin-1', dtype=dataTypes,  thousands=',', decimalstr=',')
# Remove all accents from db
#  
uniqueStructure = csv['Structure'].unique()
uniqueElement = csv["Type de l'élément"].unique()
statusElement = csv["Statut de l'élément"].unique()

elementValides = csv.loc[csv["Statut de l'élément"] == "Valide générique"]
elementsValidesSpecifiques = csv.loc[csv["Statut de l'élément"] == "Valide spécifique"]