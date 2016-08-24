#
# Spider script for Casa.it
# Last update: August 2016
#
import json
import re

import scrapy

from hs.item import HomeItem
from hs.utility import validate_value

cleanUnicodePrice = re.compile("\D*(\d+\.\d+)\.*")

# Parametrize!
BASEDOMAIN = "http://www.casa.it"
BASEQUERY = "/vendita-residenziale/in-parella++torino%2c+to%2c+piemonte%3b+pozzo+strada++torino%2c+to%2c+piemonte%3b+cenisia++torino%2c+to%2c+piemonte%3b+cit+turin++torino%2c+to%2c+piemonte%3b+san+donato++torino%2c+to%2c+piemonte%3b+centro++giardini+reali++repubblica++torino%2c+to%2c+piemonte%3b+crocetta++torino%2c+to%2c+piemonte%3b+san+paolo++torino%2c+to%2c+piemonte%3b+rivoli++to%2c+piemonte%3b+grugliasco++to%2c+piemonte%3b+collegno++to%2c+piemonte/lista-1"


def find_feature(feats, name):
    for f in feats:
        if f['label'].lower() == name.lower():
            return f['value']

    return ''


class CasaSpider(scrapy.Spider):
    name = "casa"
    allowed_domains = ["casa.it"]
    start_urls = [BASEDOMAIN + BASEQUERY]

    # Parse listing search page
    def parse(self, response):
        # Parse all announces

        # Extract __INITIAL_STATE__ json object containing all page listings
        jsonobj = response.xpath('//script').re(r'window.__INITIAL_STATE__.*=[ ]*({.*});')
        if jsonobj:
            jsonobj = json.loads(jsonobj[0])

        # Parse all announces
        for l in jsonobj['listing']['listing']:
            url = response.urljoin(BASEDOMAIN + "/" + l['url'])
            yield scrapy.Request(url, callback=self.parse_the_listing)

        # Search for next page
        next_page = response.xpath('//div[@class="next"]/span/a/@href').extract()
        if next_page:
            url = response.urljoin(BASEDOMAIN + next_page[0])
            yield scrapy.Request(url, callback=self.parse)

    # Parse single listing page
    @staticmethod
    def parse_the_listing(response):
        item = HomeItem()
        item['source'] = __name__.split(".")[-1]

        # Immobiliare listing own ID
        # From this:    http://www.casa.it/immobile-appartamento-piemonte-torino-31075636
        # Extract this: 31075636
        item['ID'] = response.url.split("/")[-1].split("-")[-1]

        # Listing url
        item['url'] = response.url

        # Extract _INITLIA_DATA json
        jsonobj = response.xpath('//script').re(r'window.__INITIAL_STATE__.*=[ ]*({.*});')
        if jsonobj:
            jsonobj = json.loads(jsonobj[0])
        if jsonobj['detail']['_map']:
            item['json'] = jsonobj['detail']['_map']
            jsonobj = jsonobj['detail']['_map']
        else:
            return

        # Images & Blueprints
        item['images'] = item['blueprints'] = []
        for i in jsonobj['media']:
            if i['type'] == 'mainphoto' or i['type'] == 'photo':
                item['images'].append(i)
            elif i['type'] == 'floorplan':
                item['blueprints'].append(i)

        # Description
        item['description'] = validate_value(jsonobj['description'])

        item['price'] = validate_value(jsonobj['price'])

        item['listingRef'] = validate_value(jsonobj['rif'])
        item['listingDate'] = validate_value(jsonobj['modifiedDate'])

        item['contract'] = validate_value(jsonobj['channel'])
        item['propertyType'] = validate_value(jsonobj['type'])
        item['area'] = validate_value(jsonobj['landsize'])
        item['rooms'] = validate_value(jsonobj['bedrooms'])
        item['floor'] = find_feature(jsonobj['features'], 'Piano')
        item['box'] = validate_value(jsonobj['parkingspaces'])
        item['availability'] = find_feature(jsonobj['features'], 'Stato al rogito')

        item['year'] = find_feature(jsonobj['features'], 'Anno di costruzione')
        item['condition'] = find_feature(jsonobj['features'], 'Condizioni')
        item['heating'] = find_feature(jsonobj['features'], 'Riscaldamento')
        item['energyEP'] = validate_value(jsonobj['energyClass']['ipe'])
        item['energyClass'] = validate_value(jsonobj['energyClass']['class'])

        item['address'] = validate_value(jsonobj['address'])

        item['agency'] = validate_value(jsonobj['agency'])

        yield item
