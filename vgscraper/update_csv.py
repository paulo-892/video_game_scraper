from tempfile import NamedTemporaryFile
import os
import json
import shutil
import ast
import csv

# constants
HEADER_ROWS = 1
ID_COL = 0
UPC_COL = 2
PRICE_COL = 9

OLD_CSV_FILENAME = './src_csv/video_game_collection - All.csv'
PRICE_MAPPING_FILENAME = './id_to_price/id_to_price.txt'

if __name__ == '__main__':

    tempfile = NamedTemporaryFile(delete=False,mode='w+t')

    # opens both files
    with open(OLD_CSV_FILENAME, 'rt') as oldCSV, tempfile:
        # opens old and new CSV files as CSV
        reader = csv.reader(oldCSV, delimiter=',', quotechar='"')
        writer = csv.writer(tempfile, delimiter=',', quotechar='"')

        # opens other file as dict (requires some steps)
        f = open(PRICE_MAPPING_FILENAME, 'rt')

        strings = (f.read()).split(',')[:-1]
        string_dicts = [json.loads(string) for string in strings]

        full_dict = {}
        for dict in string_dicts:
            full_dict.update(dict)

        ids_to_update = list(full_dict.keys())

        # for each row in the old CSV...
        for i, row in enumerate(reader):

            # if the row is a game-entry row...
            if (i >= HEADER_ROWS):
                id = row[ID_COL]

                if id in ids_to_update:
                    price = full_dict[id]
                    row[PRICE_COL] = price


            # writes the new row
            writer.writerow(row)

        shutil.move(tempfile.name, OLD_CSV_FILENAME)
        #os.remove(prices_by_upc)
        f.close()
