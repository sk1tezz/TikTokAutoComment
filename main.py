import asyncio
import logging

from dotenv import dotenv_values
from aiogram import Bot, Dispatcher
import psutil

from telegram.handlers import start
from ui2funcs import autocommenting


config = dotenv_values(".env")
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config["BOT_TOKEN"])
dp = Dispatcher()


def kill_appium():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info["name"] == "node.exe":
                proc.terminate()
                proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue


async def main():
    asyncio.create_task(autocommenting.main())
    dp.include_routers(start.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    kill_appium()
    asyncio.run(main())
