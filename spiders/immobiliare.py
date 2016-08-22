import scrapy
from item import ImmobiliareItem
import re

cleanUnicodePrice = re.compile("\D*(\d+\.\d+)\.*")

# Parametrize!
BASEQUERYPATH = "http://www.immobiliare.it/Torino/case_in_vendita-Torino.html?prezzoMassimo=170000&vrt=45.08443000137,7.6526641845703;45.086490430925,7.6260566711426;45.091459396452,7.6166152954102;45.085884429947,7.5761032104492;45.083339155636,7.5675201416016;45.080187706511,7.5496673583984;45.063942865885,7.5443458557129;45.053514639982,7.5687217712402;45.050482822163,7.6300048828125;45.049027492522,7.6344680786133;45.057758914916,7.6348114013672;45.050028035628,7.6661396026611;45.070451964167,7.6776194572449;45.07369108202,7.6676523685455;45.078384635807,7.6715898513794&superficieMinima=60&riscaldamenti=1&noAste=1"
# startUrls = [BASEQUERYPATH + "&pag=" + str(pageNumber) for pageNumber in range(2, 200)]


class ImmobiliareSpider(scrapy.Spider):
    name = "immobiliare"
    allowed_domains = ["immobiliare.it"]
    # start_urls = startUrls
    start_urls = [BASEQUERYPATH]

    # Parse listing search page
    def parse(self, response):
        # Parse all announces ( still ok until: 2016 08 22 )
        for href in response.css('div .annuncio_title strong a::attr(href)').extract():
            url = response.urljoin(href)
            # yield scrapy.Request(url.replace("www.", "m."), callback=self.parse_the_listing)
            yield scrapy.Request(url, callback=self.parse_the_listing)

        # # Search for next page
        # next_page = response.css('div #paginazione > a::attr(href) .next_page_act')
        # if next_page:
        #     url = response.urljoin(next_page[0].extract())
        #     yield scrapy.Request(url, (self))

    # Parse single listing page
    @staticmethod
    def parse_the_listing(response):
        item = ImmobiliareItem()

        # TODO: Pirctures/Blueprints from _INITIAL_DATA js object

        # Immobiliare listing own ID
        # From this:    http://www.immobiliare.it/57204928-Vendita-Bilocale-via-XX-Settembre-27-Grugliasco.html
        # Extract this: 57204928
        item['ID'] = response.url.split("/")[-1].split("-")[0]

        # Listing url
        item['url'] = response.url  # .replace("m.", "www.")

        # Description
        item['description'] = response.xpath(
            '//div[@id="description"]/div[contains(@class,"description-text")]/div/text()'
        ).extract()[0].replace("\n", "").replace("\t", "").strip()

        # Listing reference and date
        rd = response.xpath(
            '//dt[contains(text(), "Riferimento e Data annuncio")]/following::dd[1]/text()'
        ).extract()[0]
        item['listingRef'] = rd.split("-")[0].strip()
        item['listingDate'] = rd.split("-")[1].strip()

        # Contract
        item['contract'] = response.xpath(
            '//dt[contains(text(), "Contratto")]/following::dd[1]/text()'
        ).extract()[0]
        item['propertyType'] = response.xpath(
            '//dt[contains(text(), "Contratto")]/following::dd[1]/text()'
        ).extract()[0]

        # Details
        item['area'] = response.xpath(
            '//dt[contains(text(), "Superficie")]/following::dd[1]/text()'
        ).extract()[0]
        item['rooms'] = response.xpath(
            '//dt[contains(text(), "Locali")]/following::dd[1]/text()'
        ).extract()[0]
        item['floor'] = response.xpath(
            '//dt[contains(text(), "Piano")]/following::dd[1]/text()'
        ).extract()[0]
        item['box'] = response.xpath(
            '//dt[contains(text(), "Box e posti auto")]/following::dd[1]/text()'
        ).extract()[0]
        item['availability'] = response.xpath(
            '//dt[contains(text(), "Disponibilit")]/following::dd[1]/text()'
        ).extract()[0]

        # TODO: Characteristics divided in "available" and "unavailable"

        # extract only the price w/ the regex
        item['price'] = cleanUnicodePrice.match(response.xpath(
            '//dt[contains(text(), "Prezzo")]/following::dd[1]/text()'
        ).extract()[0]).groups()

        # Energy & Conditions
        item['year'] = response.xpath(
            '//dt[contains(text(), "Anno di costruzione")]/following::dd[1]/text()'
        ).extract()[0]
        item['condition'] = response.xpath(
            '//dt[contains(text(), "Stato")]/following::dd[1]/text()'
        ).extract()[0]
        item['heating'] = response.xpath(
            '//dt[contains(text(), "Riscaldamento")]/following::dd[1]/text()'
        ).extract()[0]
        item['energyEP'] = response.xpath(
            '//dt[contains(text(), "Indice di prestazione energetica")]/following::dd[1]/text()'
        ).extract()[0]
        item['energyClass'] = response.xpath(
            '//div[@class="indicator-energy"]/@data-energyclass'
        ).extract()[0]

        # Address
        item['address'] = response.xpath(
            '//div[@class="maps-address"]/p/span/strong/text()'
        ).extract()[0]
        # item['address'] = [x.strip() for x in response.xpath('//div[contains(@class,"indirizzo_")]/text()').extract()]

        item['agency'] = response.xpath(
            '//div[@class="detail-agency-logo"]/img/@alt'
        ).extract()[0]

        yield item
