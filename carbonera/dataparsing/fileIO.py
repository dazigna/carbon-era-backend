import json
import csv
from typing import Dict

class FileIOManager():
    def __init__(self) -> None:
        pass

    def writeToJson(self, fileName, jsonData) -> None:
        print(f'Writing json file: {fileName}')
        with open(fileName, 'w', encoding='utf-8') as f:
          json.dump(jsonData, f, indent=4)

    def readJson(self, fileName) -> Dict:
        print(f'Trying to read json file: {fileName}')
        with open(fileName,'r',encoding='utf-8') as r:
            return json.load(r)
    
    def writeCSV(self, fileName, data):
        with open(fileName, 'w') as f:
            f.writelines(data)
    
    def readCSV(self, fileName):
        with open(fileName, 'r') as f:
            csv_reader = csv.reader(f)


            