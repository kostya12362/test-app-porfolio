from datetime import datetime, timezone
from loguru import logger

from core.broker import broker

from users.models import TelegramAccount


@broker.subscriber(queue="telegram:account:save")
async def telegram_save_account(data: dict) -> None:
    print(data)
    obj, _ = await TelegramAccount.objects.aupdate_or_create(
        id=data['id'],
        defaults={
            "username": data['username'],
            "created_at": datetime.fromisoformat(data['created_at']),
            "is_active": data.get('is_active', True)
        }
    )
    print(obj)
    logger.info(f"Telegram account id = {data['id']} saved")
