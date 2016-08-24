# Main runner
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from hs.spiders.casa import CasaSpider
from hs.spiders.immobiliare import ImmobiliareSpider

# Use runner object to run the spider(s)
runner = CrawlerProcess(get_project_settings())
runner.crawl(ImmobiliareSpider)
runner.crawl(CasaSpider)
runner.start()
