from tempfile import NamedTemporaryFile
import os
import json
import shutil
import ast
import csv

# constants
HEADER_ROWS = 1
UPC_COL = 1
COND_COL = 3
PRICE_COL = 8

if __name__ == '__main__':

    # gets names of CSV to be updated and prices by upc document
    old_csv = './SS - Video Games [Collection & Completion] - All.csv'
    prices_by_upc = './prices_by_upc.txt'
    tempfile = NamedTemporaryFile(delete=False,mode='w+t')

    # opens both files
    with open(old_csv, 'rt') as oldCSV, tempfile:
        # opens old and new CSV files as CSV
        reader = csv.reader(oldCSV, delimiter=',', quotechar='"')
        writer = csv.writer(tempfile, delimiter=',', quotechar='"')

        # opens other file as dict (requires some steps)
        f = open(prices_by_upc, 'rt')
        string = (f.read()).split(',')
        string = string[0:len(string) - 1]
        dics = [ast.literal_eval(x) for x in string]

        full_dict = {}
        for dic in dics:
            full_dict.update(dic)

        # for each row in the old CSV...
        for i, row in enumerate(reader):

            # if the row is a game-entry row...
            if (i >= HEADER_ROWS):
                # extracts upc
                upc = row[UPC_COL]
                cond = row[COND_COL]

                # if upc is N/A, special case and so return normal row
                if upc == 'N/A':
                    writer.writerow(row)
                    continue

                # combines upc with condition to create identifier
                ident = upc + '-' + cond

                # looks up price based on upc
                price = full_dict[ident]

                # updates row
                row[UPC_COL] = "\'" + str(upc)
                row[PRICE_COL] = price

            # writes the new row
            writer.writerow(row)

        shutil.move(tempfile.name, old_csv)
        os.remove(prices_by_upc)
        f.close()
