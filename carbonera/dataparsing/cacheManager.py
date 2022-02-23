from typing import Dict
import requests as r
from pathlib import Path
import lox
from fileIO import FileIOManager

class CacheManager():
    
    def __init__(self) -> None:
        self.schemaUrl = 'https://data.ademe.fr/data-fair/api/v1/datasets/base-carbone(r)/'
        self.databaseUrl = 'https://data.ademe.fr/data-fair/api/v1/datasets/base-carbone(r)/full'
        self.schemaFileName = 'schema.json'
        self.dBFileName = 'db.csv'
   
    def getSchema(self) -> Dict:
        try:
            return FileIOManager().readJson(self.schemaFileName)
        except:
            print("Failed reading schema file")
            return self.downloadSchema()

    def getDB(self):
        if not Path(self.dBFileName).is_file():
            self.downloadDB()
        print('DB ready to go')
        return self.dBFileName
    
    def downloadDB(self):
        print("downloading DB")
        with r.get(self.databaseUrl, stream = True) as response:
            with open(self.dBFileName, 'wb') as f:
                for chunk in response.iter_content(chunk_size = 1024):
                    f.write(chunk)

    def downloadSchema(self) -> Dict:
        print("Downloading Schema")
        databaseSchemaRaw = r.get(self.schemaUrl).json()['schema']
        FileIOManager().writeToJson(self.schemaFileName, databaseSchemaRaw)
        return databaseSchemaRaw
        

def main():
    manager = CacheManager()
    schema = manager.getSchema()
    db = manager.getDB()

if __name__ == '__main__':
    main()
