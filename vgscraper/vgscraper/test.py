import gspread
from oauth2client.service_account import ServiceAccountCredentials
from scrapy import signals

import scrapy

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import dispatcher



# constants
HEADER_ROWS = 1
ID_COL = 0
UPC_COL = 2
COND_COL = 4

CSV_NAME = '../src_csv/video_game_collection - All.csv'

CONDITION_TO_FIELD = {
    'Loose': '#used_price'
    , 'CIB': '#complete_price'
    , 'SIB': '#new_price'
}

mapping_of_spreadsheet_field_to_python_field = {
    'ID': 'id'
    , 'UPC': 'upc'
    , 'Rating': 'condition'
}


class VGSpider(scrapy.Spider):
    # name of spider
    name = "games"

    start_urls = ["https://www.pricecharting.com"]

    def parse(self, response):
        game_metadata_list = self.metadata
        for game_metadata in game_metadata_list:
            yield scrapy.Request(url='https://www.pricecharting.com/search-products?type=prices&q={upc}'.format(
                upc=game_metadata["upc"]),
                                 callback=self.parse_result,
                                 dont_filter=True,
                                 meta={'condition': game_metadata["condition"], 'upc': game_metadata["upc"],
                                       'id': game_metadata["id"]})

    def parse_result(self, response):
        id = response.meta['id']
        upc = response.meta['upc']
        condition = response.meta['condition']

        if condition in ['N/A', 'Digital', 'Rental']:
            return

        # TODO - handle N/A condition
        css_field = CONDITION_TO_FIELD[condition]


        # issue request to page
        price = response.css(css_field + ' span.js-price::text').get()

        # if the price isn't found, returns
        if price is None:
            print('ERROR - Item with UPC ' + str(upc) + ' not found on VGPC')
            return

        price = price.strip().replace('$', '')

        yield {
            id: price
        }


def update_spreadsheet_with_prices(client, price_dict):
    sheet = client.open('test_collection')
    worksheet = sheet.worksheet("All")
    data = worksheet.get_all_records(numericise_ignore=['all'])
    print(data)
    vals = [price_dict[e['ID']] if e['ID'] in price_dict.keys() else "" for e in data]
    cells = worksheet.range("J2:J%d" % len(vals))
    for i, e in enumerate(cells):
        e.value = vals[i]
    worksheet.update_cells(cells, value_input_option='USER_ENTERED')


def scrape_vgpc_for_price_data(metadata):
    process = CrawlerProcess(get_project_settings())

    results = []

    def crawler_results(signal, sender, item, response, spider):
        results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_scraped)

    process.crawl(VGSpider, metadata=metadata)
    process.start()

    return results


def retrieve_game_metadata_from_google_sheet(client):
    # fetches the document
    sheet = client.open('test_collection')
    worksheet = sheet.worksheet("All")
    record_list = worksheet.get_all_records(numericise_ignore=['all'])
    return [
        {
            'id': record['ID']
            , 'upc': record['UPC']
            , 'condition': record['Rating']
        } for record in record_list
    ]


def authorize_google_api():
    scope = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
    ]
    file_name = 'client_key.json'
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name, scope)
    print(creds)
    return gspread.authorize(creds)


if __name__ == '__main__':
    # authorizes Google Drive API
    client = authorize_google_api()

    # gets list of ids from spreadsheet
    game_metadata_dict = retrieve_game_metadata_from_google_sheet(client)

    # scrapes VGPC to get prices for each ID
    results_list = scrape_vgpc_for_price_data(game_metadata_dict)
    # ID 58 not present in results_list!

    # formats result list into dictionary
    results_dict = {
        list(result.keys())[0]: result[list(result.keys())[0]] for result in results_list
    }

    # writes new price data back to spreadsheet
    update_spreadsheet_with_prices(client, results_dict)

    # ISSUE: duplicate UPCs not having prices written


