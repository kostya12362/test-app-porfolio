from datetime import datetime, timezone
from loguru import logger

from core.broker import broker
from core.db.utils import AsyncAtomicContextManager, AsyncModelUtils
from social_media.models import Post, Tag, Account
from users.models import TelegramAccount


@broker.subscriber(queue="instagram:posts:save")
async def save_posts(data: dict) -> None:
    items = data['items']
    pool_tags = set()
    async with AsyncAtomicContextManager():
        for item in items:
            uid = item['id'].split('_')[0]
            obj, status = await Post.objects.aupdate_or_create(
                account_id=item['account_id'],
                uid=uid,
                defaults={
                    "likes": item['like_count'],
                    "comments": item['comment_count'],
                    "description": item['description'],
                    "created_at": datetime.fromtimestamp(item['created_at'], tz=timezone.utc),
                    "store_at": datetime.fromtimestamp(item['stored_at'], tz=timezone.utc)
                }
            )
            logger.info(f"Post id = {obj.id} saved uid = {uid} for account id = {item['account_id']}")
        pool_tags.update(item['tags'])
        multi = AsyncModelUtils(Tag, [{"title": i} for i in item['tags']], 'title')
        tags = await multi.update_or_create()
        await obj.tags.aset(tags)
    follow_tags = {
        i.title for i in Tag.objects.filter(
            followed_by__isnull=False,
            followed_by__account_id=data['account_id']
        ).distinct()
    }
    match_tags = follow_tags.intersection(pool_tags)
    if not match_tags:
        return
    logger.info(f"Data push to Telegram")
    async for tg in TelegramAccount.objects.filter(is_active=True):
        data['tg_id'] = tg.id
        data['find_tags'] = match_tags
        await broker.publish(queue=f'telegram:notifications', message=data)


async def push_accounts():
    async for account in Account.objects.all():
        await broker.publish(queue=f'crawler:input:{account.provider.lower()}', message={
            "callback": "start",
            "metadata": {
                "page_size": 10,
                "max_pages": 1,
                "username": account.username,
                "account_id": account.id
            }
        })

    logger.info("Pushed accounts to queue.")
