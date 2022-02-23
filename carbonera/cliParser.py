import argparse
from dataparsing.ademeParser import AdemeParser

class ParserRunner():

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