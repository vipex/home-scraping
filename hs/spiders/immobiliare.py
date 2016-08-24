#
# Spider script for Immonbiliare.it
# Last update: August 2016
#
import json
import re

import scrapy

from hs.item import HomeItem
from hs.utility import validate_value

cleanUnicodePrice = re.compile("\D*(\d+\.\d+)\.*")

# Parametrize!
BASEDOMAIN = "http://www.immobiliare.it"
BASEQUERY = "/Torino/case_in_vendita-Torino.html?prezzoMassimo=170000&vrt=45.08443000137,7.6526641845703;45.086490430925,7.6260566711426;45.091459396452,7.6166152954102;45.085884429947,7.5761032104492;45.083339155636,7.5675201416016;45.080187706511,7.5496673583984;45.063942865885,7.5443458557129;45.053514639982,7.5687217712402;45.050482822163,7.6300048828125;45.049027492522,7.6344680786133;45.057758914916,7.6348114013672;45.050028035628,7.6661396026611;45.070451964167,7.6776194572449;45.07369108202,7.6676523685455;45.078384635807,7.6715898513794&superficieMinima=60&riscaldamenti=1&noAste=1"


class ImmobiliareSpider(scrapy.Spider):
    name = "immobiliare"
    allowed_domains = ["immobiliare.it"]
    start_urls = [BASEDOMAIN+BASEQUERY]

    # Parse listing search page
    def parse(self, response):
        # Parse all announces ( still ok until: 2016 08 22 )
        for href in response.css('div .annuncio_title strong a::attr(href)').extract():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_the_listing)

        # Search for next page
        next_page = response.xpath('//div[@id="paginazione"]/a[contains(@class, "next_page_act")]/@href').extract()
        if next_page:
            url = response.urljoin(BASEDOMAIN+next_page[0])
            yield scrapy.Request(url, callback=self.parse)

    # Parse single listing page
    @staticmethod
    def parse_the_listing(response):
        item = HomeItem()
        item['source'] = __name__.split(".")[-1]

        # Immobiliare listing own ID
        # From this:    http://www.immobiliare.it/57204928-Vendita-Bilocale-via-XX-Settembre-27-Grugliasco.html
        # Extract this: 57204928
        item['ID'] = response.url.split("/")[-1].split("-")[0]

        # Listing url
        item['url'] = response.url

        # Extract _INITLIA_DATA json
        jsonobj = response.xpath('//script').re(r'_INITIAL.*=[ ]*({.*});')
        if jsonobj:
            jsonobj = json.loads(jsonobj[0])
        item['json'] = jsonobj

        # Images & Blueprints
        item['images'] = validate_value(jsonobj['multimedia']['immagini']['list'])
        item['blueprints'] = validate_value(jsonobj['multimedia']['planimetrie']['list'])

        # Description
        item['description'] = response.xpath(
            '//div[@id="description"]/div[contains(@class,"description-text")]/div/text()'
        ).extract()[0].replace("\n", "").replace("\t", "").strip()

        # extract only the price w/ the regex
        tmp = response.xpath(
            '//dt[contains(text(), "Prezzo")]/following::dd[1]/span/text()'
        ).extract()
        if tmp:
            if cleanUnicodePrice.match(tmp[0]).groups():
                item['price'] = cleanUnicodePrice.match(tmp[0]).groups()[0]
            else:
                item['price'] = tmp[0]

        # Listing reference and date
        tmp = response.xpath(
            '//dt[contains(text(), "Riferimento e Data annuncio")]/following::dd[1]/text()'
        ).extract()
        if tmp:
            item['listingRef'] = tmp[0].split("-")[0].strip()
            item['listingDate'] = tmp[0].split("-")[1].strip()

        # Contract
        tmp = response.xpath(
            '//dt[contains(text(), "Contratto")]/following::dd[1]/text()'
        ).extract()
        item['contract'] = validate_value(tmp[0])

        tmp = response.xpath(
            '//dt[contains(text(), "Tipo propriet")]/following::dd[1]/text()'
        ).extract()
        item['propertyType'] = validate_value(tmp[0])

        # Details
        tmp = response.xpath(
            '//dt[contains(text(), "Superficie")]/following::dd[1]/text()'
        ).extract()
        item['area'] = validate_value(tmp[0])
        tmp = response.xpath(
            '//dt[contains(text(), "Locali")]/following::dd[1]/text()'
        ).extract()
        item['rooms'] = validate_value(tmp[0])
        tmp = response.xpath(
            '//dt[contains(text(), "Piano")]/following::dd[1]/text()'
        ).extract()
        item['floor'] = validate_value(tmp[0])
        tmp = response.xpath(
            '//dt[contains(text(), "Box e posti auto")]/following::dd[1]/text()'
        ).extract()
        item['box'] = validate_value(tmp[0])
        tmp = response.xpath(
            '//dt[contains(text(), "Disponibilit")]/following::dd[1]/text()'
        ).extract()
        item['availability'] = validate_value(tmp[0])

        # TODO: Characteristics divided in "available" and "unavailable"

        # Energy & Conditions
        tmp = response.xpath(
            '//dt[contains(text(), "Anno di costruzione")]/following::dd[1]/text()'
        ).extract()
        item['year'] = validate_value(tmp[0])
        tmp = response.xpath(
            '//dt[contains(text(), "Stato")]/following::dd[1]/text()'
        ).extract()
        item['condition'] = validate_value(tmp[0])
        tmp = response.xpath(
            '//dt[contains(text(), "Riscaldamento")]/following::dd[1]/text()'
        ).extract()
        item['heating'] = validate_value(tmp[0])
        tmp = response.xpath(
            '//dt[contains(text(), "Indice di prestazione energetica")]/following::dd[1]/text()'
        ).extract()
        item['energyEP'] = validate_value(tmp[0])
        tmp = response.xpath(
            '//div[@class="indicator-energy"]/@data-energyclass'
        ).extract()
        item['energyClass'] = validate_value(tmp[0])

        # Address
        tmp = response.xpath(
            '//div[@class="maps-address"]/p/span/strong/text()'
        ).extract()
        item['address'] = validate_value(tmp[0])

        tmp = response.xpath(
            '//div[@class="detail-agency-logo"]/img/@alt'
        ).extract()
        item['agency'] = validate_value(tmp[0])

        yield item
