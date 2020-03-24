from tempfile import NamedTemporaryFile
import json
import shutil
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

        # opens other file as dict (requires conversion)
        f = open(prices_by_upc, 'rt')
        dic = eval(f.read())

        # for each row in the old CSV...
        for i, row in enumerate(reader):
            print(row)

            # if the row is a game-entry row...
            if (i >= 4):
                # extracts upc
                upc = row[1]

                # looks up price based on upc
                price = dic[upc]

                # updates row
                row[7] = price

            # writes the new row
            writer.writerow(row)

        shutil.move(tempfile.name, old_csv)
        f.close()
