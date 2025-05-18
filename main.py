import asyncio
import logging
from datetime import datetime, timezone
import sys

import ntplib
from dotenv import dotenv_values
from aiogram import Bot, Dispatcher
from aiogram.types import User
import psutil

from telegram.handlers import start, settings, main as tgmain
from telegram import jsondb
from ui2funcs import autocommenting


config = dotenv_values(".env")


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'INFO': '\033[92m', 'WARNING': '\033[93m', 'ERROR': '\033[91m', 'CRITICAL': '\033[95m'
    }

    def format(self, record):
        log_fmt = (f"{self.COLORS.get(record.levelname, '')}[%(asctime)s] %(levelname)s "
                   f"[%(name)s]: %(message)s\033[0m")
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
logging.getLogger().handlers[0].setFormatter(ColoredFormatter())


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


def get_ntp_time():
    client = ntplib.NTPClient()
    try:
        response = client.request('pool.ntp.org', version=3)
        current_time = datetime.utcfromtimestamp(response.tx_time).replace(tzinfo=timezone.utc)
        return current_time
    except Exception as e:
        print(f"[Ошибка] Не удалось получить время с NTP: {e}")
        sys.exit(1)


async def main():
    asyncio.create_task(autocommenting.main())
    dp.include_routers(start.router, tgmain.router, settings.router)

    me: User = await bot.get_me()
    logging.getLogger(f"@{me.username}").info("Телеграм бот уcпешно запущен!\n")

    await dp.start_polling(bot)


if __name__ == "__main__":
    expiration_date = datetime(2025, 5, 20, tzinfo=timezone.utc)
    current_time = get_ntp_time()

    if current_time >= expiration_date:
        print("[!] Срок действия скрипта истёк. Запуск невозможен.")
        sys.exit(1)
    else:
        jsondb.init()
        logging.getLogger('aiogram').setLevel(logging.CRITICAL + 1)
        kill_appium()
        asyncio.run(main())
