import json
import logging

logger = logging.getLogger(__name__)


class SavePostsPipeline:
    OUTPUT_QUEUE_NAME = "instagram:posts:save"

    def __init__(self):
        self.broker = None

    def open_spider(self, spider):
        self.broker = spider.broker

    async def process_item(self, item: dict, spider):
        try:
            await self.broker.publish(queue=self.OUTPUT_QUEUE_NAME, message=item)
            logger.info("Published result to output_queue.")
        except Exception as e:
            logger.error(f"Error publishing result: {e}")
        return item
