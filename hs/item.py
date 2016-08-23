import scrapy


class HomeItem(scrapy.Item):
    source = scrapy.Field()
    json = scrapy.Field()

    images = scrapy.Field()
    blueprints = scrapy.Field()

    ID = scrapy.Field()
    url = scrapy.Field()

    description = scrapy.Field()

    listingRef = scrapy.Field()
    listingDate = scrapy.Field()

    contract = scrapy.Field()
    propertyType = scrapy.Field()
    area = scrapy.Field()
    rooms = scrapy.Field()
    floor = scrapy.Field()
    box = scrapy.Field()
    availability = scrapy.Field()

    price = scrapy.Field()

    year = scrapy.Field()
    condition = scrapy.Field()
    heating = scrapy.Field()
    energyEP = scrapy.Field()
    energyClass = scrapy.Field()

    address = scrapy.Field()

    agency = scrapy.Field()
