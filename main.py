import asyncio
import logging
from dotenv import dotenv_values

from aiogram import Bot, Dispatcher
from telegram.handlers import start
from ui2funcs import autocommenting


config = dotenv_values(".env")
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config["BOT_TOKEN"])
dp = Dispatcher()


async def main():
    asyncio.create_task(autocommenting.main())
    dp.include_routers(start.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
