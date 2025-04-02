from faststream.rabbit import RabbitBroker
from django.conf import settings
from loguru import logger

broker = RabbitBroker(settings.BROKER.uri, logger=logger)
