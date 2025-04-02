import asyncio
from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI

from core.broker import broker
from core.scheduler import setup_scheduler
from users.api.routers import router as users_router
from users.registry import telegram_save_account  # noqa

from social_media.api.routers import router as social_media_router
from social_media.registry import save_posts, push_accounts  # noqa

__all__ = (
    "routers",
    "lifespan",
)

routers: list[APIRouter] = [
    users_router,
    social_media_router,
]


@asynccontextmanager
async def lifespan(application: FastAPI):
    async with broker:
        await broker.start()
        task = asyncio.create_task(setup_scheduler(cron='*/2 * * * *', callback=push_accounts))
        yield
        task.cancel()
