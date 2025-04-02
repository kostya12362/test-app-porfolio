import os
import asyncio

from loguru import logger

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from faststream.rabbit import RabbitBroker

from core.logger import setup_logger

# Bot token can be obtained via https://t.me/BotFather
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

broker = RabbitBroker(os.getenv('RMQ_URI'), logger=logger)

# Initialize Bot instance with default bot properties which will be passed to all API calls
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()


@broker.subscriber(queue="telegram:notifications")
async def new_post(data: dict) -> None:
    tg_id = data.pop('tg_id')
    text = f"Find post with tags: {', '.join(data['find_tags'])}"
    await bot.send_message(chat_id=tg_id, text=text, parse_mode=ParseMode.HTML)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await broker.publish(
        queue="telegram:account:save",
        message={
            "id": message.from_user.id,
            "username": message.from_user.username,
            "created_at": message.date.isoformat(),
        }
    )
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!\n")


async def main() -> None:
    await broker.start()
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    setup_logger()
    asyncio.run(main())
