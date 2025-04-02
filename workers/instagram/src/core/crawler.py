import scrapy
from core.log import setup_logger
from scrapy.crawler import CrawlerProcess
from twisted.internet import asyncioreactor


def create_crawler_process(
        spider: type[scrapy.Spider],
) -> None:
    asyncioreactor.install()
    settings = {
        'DOWNLOAD_TIMEOUT': 18000,
        'DNS_TIMEOUT': 300,
        "LOG_LEVEL": "INFO",
        "LOG_ENABLED": False,
        'DOWNLOAD_DELAY': 0.5,
        'ASYNCIO_EVENT_LOOP': True,
    }
    if getattr(spider, 'custom_settings', None):
        log_enabled = spider.custom_settings.get('LOG_ENABLED', True)
        if log_enabled:
            spider.custom_settings['LOG_ENABLED'] = False
            setup_logger()
    else:
        setup_logger()
    process = CrawlerProcess(settings=settings)
    process.crawl(spider)
    process.start()
