from tempfile import NamedTemporaryFile
import json
import shutil
import csv
import scrapy

# constants
HEADER_ROWS = 1
UPC_COL = 1
COND_COL = 3

class VGSpider(scrapy.Spider):
    # name of spider
    name = "games"

    # start URL
    start_urls = ['https://www.pricecharting.com/']

    def parse(self, response):

        filename = './SS - Video Games [Collection & Completion] - All.csv'

        # opens the file in read-only mode
        with open(filename, 'rt') as csvFile:

            # creates a CSV reader for the file
            reader = csv.reader(csvFile, delimiter=',', quotechar='"')

            # opens a recipient file
            #f = open('price_by_upc', 'w+')

            prices_by_upc = {}

            # for each row in the CSV...
            for i, row in enumerate(reader):
                # ignores any non-game entries
                if (i >= HEADER_ROWS):
                    # extracts the upc
                    upc = row[UPC_COL]

                    # if there are multiple of same upc, removes ID and sends regular upc to request
                    sep = '-'
                    alt_upc = upc.split(sep, 1)[0]
                    cond = row[COND_COL]
                    
                    data = {
                        'q': alt_upc,
                        'type': 'videogames',
                    }

                    # if upc is N/A, special case and so return
                    if upc == 'N/A':
                        continue

                    # finds the price by the upc and adds it to the dictionary
                    res = yield scrapy.FormRequest(url='https://www.pricecharting.com/search-products', dont_filter=True, formdata=data, callback=self.parse_result, meta={'upc': upc, 'cond': cond})

    def parse_result(self, response):
        # extract several fields
        cond = response.meta['cond']
        upc = response.meta['upc']

        # convert condition into proper request
        field = None
        if cond == 'Loose':
            field = '#used_price'
        elif cond == 'CIB':
            field = '#complete_price'
        elif cond == 'SIB':
            field = '#new_price'
        else:
            print('ERROR - Item with UPC ' + str(upc) + ' has unrecognized condition ' + cond)
            return

        # issue request to page
        result = response.css(field + ' span.js-price::text').get()

        # if the price isn't found, returns
        if result is None:
            print('ERROR - Item with UPC ' + str(upc) + ' not found on VGPC')
            return

        # formats the price
        encoded_result = str.strip(result.encode('ascii','replace'))
        price = encoded_result.replace('$','')
        
        # writes the results to a file
        with open('prices_by_upc.txt', 'a') as f:
            f.write(json.dumps({response.meta['upc']:price}))
            f.write(',')
            f.close()