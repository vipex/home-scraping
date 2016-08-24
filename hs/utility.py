import random
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class UserAgentMiddlewareRandomizer(UserAgentMiddleware):
    """ User agent randomization for Scrapy Downloader middleware """
    def __init__(self, settings, user_agent='Scrapy'):
        super(UserAgentMiddlewareRandomizer, self).__init__()
        self.user_agent = user_agent

        user_agent_list = settings.get('USER_AGENT_LIST')
        if not user_agent_list:
            # If USER_AGENT_LIST settings is not set,
            # Use the default USER_AGENT or whatever was
            # passed to the middleware.
            ua = settings.get('USER_AGENT', user_agent)
            self.user_agent_list = [ua]
        else:
            self.user_agent_list = user_agent_list
        #     with open(user_agent_list, 'r') as f:
        #         self.user_agent_list = [line.strip() for line in f.readlines()]

    @classmethod
    def from_crawler(cls, crawler):
        obj = cls(crawler.settings)
        crawler.signals.connect(obj.spider_opened, signal=signals.spider_opened)
        return obj

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agent_list)
        if user_agent:
            request.headers.setdefault('User-Agent', user_agent)


def validate_value(value):
    """ Simple IF validation, if not return empty string """
    if value:
        return value
    else:
        return ''
