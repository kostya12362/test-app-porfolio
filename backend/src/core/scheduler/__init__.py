import asyncio
import os
from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger


async def setup_scheduler(cron: str, callback: Callable, timezone: str = "Europe/Paris"):
    scheduler = AsyncIOScheduler()

    # Database dump task daily
    scheduler.add_job(callback, CronTrigger.from_crontab(cron, timezone=timezone))

    scheduler.start()
    logger.info(
        "Press Ctrl+{} to exit".format("Break" if os.name == "nt" else "C")
    )
    while True:
        await asyncio.sleep(1000)