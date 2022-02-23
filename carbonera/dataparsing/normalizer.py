from heapq import merge
import numpy as np
import pandas as pd
import re
from unidecode import unidecode
from .units import Units

class Normalizer():
    def __init__(self):
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

    def normalizeUnit(self, row, denominatorColName, unitColName, supportedUnits):
        row = row.copy()
        
        unitName = None
        unitSymbol = None
        energyType = ['PCI', 'PCS']
        unitEnergyType = None
        
        # Split denominator in case of spaces 
        splitDenom = row[denominatorColName].split()
        
        #TODO: Fix regex to correct this hack -- This is a stupid hack 
        if 'personne.mois' in splitDenom:
            unitName = Units.quantity.name
            unitSymbol = 'personne.mois'
        elif 'passager.km' in splitDenom :
            unitName = Units.quantity.name
            unitSymbol = 'passager.km'
        elif 'peq.km' in splitDenom:
            unitName = Units.quantity.name
            unitSymbol = 'peq.km'
        else:
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
                
        if unitName:
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

    def normalizeName(self, dataFrame):
        df = dataFrame.copy()
        df[['nom_base_francais', 'nom_attribut_francais']] = [ self.mergeUnbalancedWords(*a) for a in tuple(zip(df['nom_base_francais'], df['nom_attribut_francais']))]
        df[['nom_base_anglais', 'nom_attribut_anglais']] = [ self.mergeUnbalancedWords(*a) for a in tuple(zip(df['nom_base_anglais'], df['nom_attribut_anglais']))]
        return df
    
    def mergeUnbalancedWords(self, strColumn1, strColumn2):
        # Handle NA
        if strColumn1 is pd.NA:
            return (strColumn1, strColumn2)

        (cleanStr, isBalanced, word) = self.checkBalancedParenthesis(strColumn1)
        if strColumn2 is pd.NA:
            return (cleanStr, strColumn2)
        
        str2 = strColumn2.strip('"\t()').lower()
        cleanStr2 = f'{word}, {str2}'
        return (cleanStr, cleanStr2)

    def checkBalancedParenthesis(self, value):
        stack = []
        word = []
        cleanStr = []
        for c in value.lower():
            if c in ['\"', '\t']:
                continue
            if c == "(":
                stack.append(c)
            elif stack and c == ")":
                stack.pop()
            elif stack and stack[-1] == "(":
                word.append(c)
            else:
                cleanStr.append(c)
        # Remove useless whitespaces by trimming and removing redundant ones
        cleanStr = ''.join(cleanStr).strip()
        cleanStr = re.sub(' +', ' ', cleanStr)

        cleanWord = ''.join(word).strip()
        return (cleanStr, len(stack) == 0, cleanWord)
