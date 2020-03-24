from tempfile import NamedTemporaryFile
import json
import shutil
import csv
import scrapy

class VGSpider(scrapy.Spider):
    # name of spider
    name = "games"

    # start URL
    start_urls = ['https://www.pricecharting.com/']

    def parse(self, response):

        filename = './test.csv'

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
                if (i >= 1):
                    # extracts the upc
                    upc = row[1]

                    # if there are multiple of same upc, removes ID and sends regular upc to request
                    sep = '-'
                    alt_upc = upc.split(sep, 1)[0]
                    cond = row[3]
                    
                    data = {
                        'q': alt_upc,
                        'type': 'videogames',
                    }
                    print('heyooo1', cond)
                    # finds the price by the upc and adds it to the dictionary
                    res = yield scrapy.FormRequest(url='https://www.pricecharting.com/search-products', dont_filter=True, formdata=data, callback=self.parse_result, meta={'upc': upc, 'cond': cond})
                    print('heyooo2', cond)

    def parse_result(self, response):
        cond = response.meta['cond']
        
        if cond == 'Loose':
            price = (str.strip(((response.css('#used_price span.js-price::text').get()).encode('ascii','replace')))).replace('$','')
        elif cond == 'CIB':
            price = (str.strip(((response.css('#complete_price span.js-price::text').get()).encode('ascii','replace')))).replace('$','')
        elif cond == 'SIB':
            price = (str.strip(((response.css('#new_price span.js-price::text').get()).encode('ascii','replace')))).replace('$','')
        else:
            print('Error - unknown condition')

        print(cond, price)

        with open('prices_by_upc', 'a') as f:
            f.write(json.dumps({response.meta['upc']:price}))
            f.write(',')
            f.close()