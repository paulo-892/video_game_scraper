from tempfile import NamedTemporaryFile
import json
import shutil
import ast
import csv

if __name__ == '__main__':

    # gets names of CSV to be updated and prices by upc document
    old_csv = './test.csv'
    prices_by_upc = './prices_by_upc'
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
            print(i, row)

            # if the row is a game-entry row...
            if (i >= 1):
                # extracts upc
                upc = row[1]
                print(i, upc)

                # looks up price based on upc
                price = full_dict[upc]
                print(i, price)

                # updates row
                row[7] = price
                print(i, row[7])
                print('hiya')

            # writes the new row
            writer.writerow(row)

        shutil.move(tempfile.name, old_csv)
        f.close()
