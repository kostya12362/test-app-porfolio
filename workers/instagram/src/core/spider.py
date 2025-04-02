import json
import asyncio
import inspect
from typing import Any
import aio_pika
from scrapy import Request, signals, Spider
from scrapy.exceptions import DontCloseSpider
from twisted.internet.threads import deferToThread
from faststream.rabbit import RabbitBroker


class AioPikaQueueSpider(Spider):
    RMQ_URI: str
    INPUT_QUEUE_NAME: str = None
    broker: RabbitBroker = None

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        if not self.INPUT_QUEUE_NAME:
            self.INPUT_QUEUE_NAME = f'crawler:input:{self.name}'
        self.broker = RabbitBroker(self.RMQ_URI, logger=None)
        self.loop = asyncio.get_event_loop()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs) -> Spider:
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)

        # Help unclosed spider to wait for new messages
        crawler.signals.connect(spider.spider_idle, signal=signals.spider_idle)
        return spider

    def spider_opened(self) -> None:
        self.logger.info("Spider opened, starting aio_pika consumer.")
        self.loop.create_task(self.consume_input_queue())  # noqa
        self.loop.create_task(self.broker.start())

    def spider_idle(self) -> None:
        self.logger.info("Spider is idle, waiting for new messages...")
        raise DontCloseSpider

    async def consume_input_queue(self) -> None:
        self.broker.subscriber(self.INPUT_QUEUE_NAME)(self._callback)

    async def _callback(self, data: dict) -> None:
        print(data)
        try:
            name = data.pop('callback', 'start')
            callback = getattr(self, name)
            if inspect.isasyncgenfunction(callback):
                async for req in callback(**data):
                    if isinstance(req, Request):
                        deferToThread(self.crawler.engine.slot.scheduler.enqueue_request, req)
                    else:
                        raise ValueError('"start" must yield a Request object')
            else:
                for req in callback(**data):
                    if isinstance(req, Request):
                        self.crawler.engine.slot.scheduler.enqueue_request(req)
                    else:
                        raise ValueError('"start" must yield a Request object')
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    def spider_closed(self):
        self.logger.info("Spider closed, closing aio_pika connection.")
        if getattr(self, "connection", None) is not None:
            self.loop.create_task(self.broker.close())

    async def start(self, **kwargs):
        pass
