from tempfile import NamedTemporaryFile
import json
import shutil
import csv
import scrapy
import urllib

import re
import os
from datetime import datetime

# constants
HEADER_ROWS = 1
ID_COL = 0
UPC_COL = 2
COND_COL = 4

CSV_NAME = './vgscraper/test.csv'

CONDITION_TO_FIELD = {
    'Loose': '#used_price'
    , 'CIB': '#complete_price'
    , 'SIB': '#new_price'
}

class VGSpider(scrapy.Spider):
    # name of spider
    name = "games"

    start_urls = ["https://www.pricecharting.com"]

    def parse(self, response):

        with open(CSV_NAME, 'rt') as csvFile:

            # creates a CSV reader for the file
            reader = csv.reader(csvFile, delimiter=',', quotechar='"')

            uuid_to_game_metadata = {}

            # for each row in the CSV...
            for i, row in enumerate(reader):
                # ignores any non-game entries
                # if i >= 2:
                #     break
                if i >= HEADER_ROWS:
                    # extracts row details
                    uuid = row[ID_COL]
                    upc = row[UPC_COL]
                    condition = row[COND_COL]

                    if upc == 'N/A':
                        continue

                    separator = '-'
                    # strips quotes and handles the separators
                    uuid_to_game_metadata[uuid] = {
                        'raw_upc': upc
                        , 'clean_upc': upc.split(separator)[0].replace("\'", "")
                        , 'condition': condition
                    }

                    for uuid, metadata in uuid_to_game_metadata.items():
                        yield scrapy.Request(url='https://www.pricecharting.com/search-products?type=prices&q={clean_upc}'.format(clean_upc=metadata["clean_upc"]), 
                            callback=self.parse_result, meta={'condition': metadata["condition"], 'clean_upc': metadata["clean_upc"], 'raw_upc': metadata["raw_upc"], 
                            'uuid': uuid})


    def parse_result(self, response):
        uuid = response.meta['uuid']
        raw_upc = response.meta['raw_upc']
        clean_upc = response.meta['clean_upc']
        condition = response.meta['condition']

        css_field = CONDITION_TO_FIELD[condition]

        # issue request to page
        price = response.css(css_field + ' span.js-price::text').get()

        # if the price isn't found, returns
        if price is None:
            print('ERROR - Item with UPC ' + str(raw_upc) + ' not found on VGPC')
            return


        price = price.strip().replace('$', '')

        with open('./id_to_price/id_to_price.txt', 'a') as f:
            f.write(json.dumps({uuid: price}))
            f.write(',')
            f.close()
