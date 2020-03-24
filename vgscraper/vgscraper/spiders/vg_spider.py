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
                    upc = row[1]
                    data = {
                        'q': upc,
                        'type': 'videogames',
                        
                    }

                    # finds the price by the upc and adds it to the dictionary
                    res = yield scrapy.FormRequest(url='https://www.pricecharting.com/search-products', formdata=data, callback=self.parse_result, meta={'upc': upc})

                # writes the dict to the file
            #f.write(json.dumps(prices_by_upc))
            #f.close()

    def parse_result(self, response):
        price = (str.strip(((response.css('#used_price span.js-price::text').get()).encode('ascii','replace')))).replace('$','')

        with open('prices_by_upc', 'wb') as f:
            f.write(json.dumps({response.meta['upc']:price}))
            f.close()