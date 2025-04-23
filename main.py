import asyncio
import psycopg2
import logging
from config import token
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import os
from dotenv import load_dotenv

from handlers.callback import register_callbacks
from handlers.message import register_message

logger = logging.getLogger(__name__)

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    logger.error("starting bot")
    dp = Dispatcher()
    Token = token
    bot = Bot(Token)
    register_message(dp)
    register_callbacks(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())