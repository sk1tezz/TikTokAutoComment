from ui2funcs.other import write, wait_for_element, restart_tiktok
from utils import gpt
import adb

import uiautomator2 as u2

import time
from random import randint
import asyncio
import requests
from dotenv import dotenv_values

config = dotenv_values(".env")


commenting_link_tasks = []


def send_message(chat_id: int, text: str):
    url = f'https://api.telegram.org/bot{config["BOT_TOKEN"]}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }

    requests.post(url, data=payload)


def add_task_in_commenting_link_tasks(task: dict):
    commenting_link_tasks.append(task)


def get_len_tasks_in_commenting_link_tasks():
    return len(commenting_link_tasks)


def phone_setup(d):
    d.shell("settings put system screen_off_timeout 2147483647")
    d.screen_on()
    d.shell("wm dismiss-keyguard")

    restart_tiktok(d)


def change_account(d, account_index: int):
    screen_width = d.window_size()[0]
    screen_height = d.window_size()[1]

    if not d.xpath('//android.widget.Button[@content-desc="Фото профиля"]').exists:
        d.xpath('//android.widget.FrameLayout[@content-desc="Профиль"]').click()
        d.xpath('//android.widget.Button[@content-desc="Фото профиля"]').wait(timeout=60)

    d.sleep(3)

    element_result = wait_for_element(d, ['//android.widget.ImageView[@content-desc="Меню"]',
                                          '//android.widget.Button[@content-desc="Меню профиля"]'])
    if element_result:
        d.xpath(element_result).click()
    else:
        raise Exception("Error")

    d.xpath('//android.widget.TextView[@text="Настройки и конфиденциальность"]').wait(timeout=60)
    d.sleep(1)
    d.xpath('//android.widget.TextView[@text="Настройки и конфиденциальность"]').click()
    d.xpath('//android.widget.TextView[@content-desc="Настройки и конфиденциальность"]').wait(timeout=60)
    d.sleep(1)
    while not d.xpath('//android.widget.TextView[@text="Сменить аккаунт"]').exists:
        d.swipe(screen_width // 2, screen_height - 300,
                screen_width // 2, 300)
        d.sleep(2)

    d.xpath('//android.widget.TextView[@text="Сменить аккаунт"]').click()

    d.xpath("//androidx.recyclerview.widget.RecyclerView/android.widget.Button").wait(timeout=30)

    accounts = d.xpath("//androidx.recyclerview.widget.RecyclerView/android.widget.Button").all()

    if (
            (len(accounts) - 1 < account_index) or
            (len(accounts) - 1 <= 1) or
            (accounts[account_index].attrib.get("content-desc", None) == "Добавить аккаунт")
    ):
        return None
    else:
        account = accounts[account_index]

        bounds = account.info["bounds"]
        left, top = bounds["left"], bounds["top"]
        right, bottom = bounds["right"], bounds["bottom"]
        all_elements = d.xpath("//*").all()
        inner_elements = []
        for el in all_elements:
            b = el.info["bounds"]
            if (
                    b["left"] >= left and b["right"] <= right and
                    b["top"] >= top and b["bottom"] <= bottom
            ):
                inner_elements.append(el)
        for el in inner_elements:
            if el.attrib.get('content-desc', None) == "Галочка":
                return False

        d.sleep(1)
        accounts[account_index].click()

    d.xpath("//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]").wait(timeout=120)
    d.sleep(20)

    return True


def post_comment(d, comment: str):
    d.xpath("//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]").wait(timeout=60)
    d.sleep(1)
    d.xpath("//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]").click()
    d.xpath('//android.widget.EditText[@text="Добавить комментарий..."]').wait(timeout=60)
    d.sleep(1)
    write(d, d.xpath(f'//android.widget.EditText[@text="Добавить комментарий..."]'), comment)
    d.sleep(1)
    d.xpath('//android.widget.Button[@content-desc="Прокомментировать"]').click()
    d.sleep(3)
    d.press("back")
    d.sleep(1)


def get_link_from_video(d):
    d.xpath("//android.widget.Button[contains(@content-desc, 'Поделиться видео.')]").click()
    d.xpath('//android.widget.Button[@content-desc="Ссылка"]').wait(timeout=60)
    d.sleep(1)
    d.xpath('//android.widget.Button[@content-desc="Ссылка"]').click()
    d.sleep(3)
    return d.clipboard


def open_video_with_link(d, url: str):
    d.open_url(url)

    element_result = wait_for_element(d, [
        '//android.widget.Button[@text="Открыть TikTok"]',
        '//android.widget.ImageView[@content-desc="Воспроизвести"]'
        "//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]"], timeout=120)
    if element_result == '//android.widget.Button[@text="Открыть TikTok"]':
        d.xpath('//android.widget.Button[@text="Открыть TikTok"]').click()
    elif element_result == '//android.widget.ImageView[@content-desc="Воспроизвести"]':
        d.xpath('//android.widget.ImageView[@content-desc="Воспроизвести"]').click()

    d.xpath("//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]").wait(timeout=60)


def swipe_video(d):
    screen_width = d.window_size()[0]
    screen_height = d.window_size()[1]

    d.swipe(screen_width // 2, screen_height - 300,
            screen_width // 2, 300)


def post_comments_in_video_with_link(device_id: str, url: str, comment: str, chatid: int):
    d = u2.connect(device_id)

    phone_setup(d)

    if "com.zhiliaoapp.musically" not in d.app_list():
        return False

    restart_tiktok(d)

    d.xpath("//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]").wait(timeout=60)

    account_index = 0
    while True:
        try:
            change_result = change_account(d, account_index)
        except Exception:
            restart_tiktok(d)
            continue

        if change_result is None:
            break
        elif not change_result:
            for i in range(3):
                d.sleep(1)
                d.press("back")


        d.sleep(1)
        try:
            open_video_with_link(d, url)

            unic_comment = gpt.create_comment(comment)
            post_comment(d, unic_comment)
            send_message(chatid, f"[{url}]: Оставил комментарий - {unic_comment}")
        except Exception:
            restart_tiktok(d)
            continue

        account_index += 1


async def post_comments_in_recommendations(device_id, comment: str, comments_in_one_account: int, comment_period: int,
                                     chatid: int):
    d = u2.connect(device_id)

    phone_setup(d)

    if "com.zhiliaoapp.musically" not in d.app_list():
        return False

    restart_tiktok(d)

    d.xpath("//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]").wait(timeout=60)

    account_index = 0
    comments_count = 0
    last_reset = time.time()

    while True:
        await asyncio.sleep(1)
        swipe_video(d)
        await asyncio.sleep(randint(1, 15))

        current_time = time.time()
        if int(current_time - last_reset) >= int(comment_period):
            if (
                    d.xpath('//android.widget.TextView[@text="Проведите вверх, чтобы пропустить"]').exists
                    or d.xpath('//android.widget.Button[@text="Не интересно"]').exists
            ):
                continue

            unic_comment = gpt.create_comment(comment)
            try:
                post_comment(d, unic_comment)
            except Exception:
                d.press("home")
                await asyncio.sleep(3)
                d.press("home")
                await asyncio.sleep(2)
                d.app_stop("com.zhiliaoapp.musically")
                await asyncio.sleep(2)
                d.app_start("com.zhiliaoapp.musically")
                d.xpath("//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]").wait(
                    timeout=60)
                continue
            comments_count += 1
            last_reset = current_time

            url = get_link_from_video(d)

            send_message(chatid, f"[{url}]: Оставил комментарий - {unic_comment}")

        if comments_count >= int(comments_in_one_account):
            account_index += 1
            while True:
                try:
                    if not change_account(d, account_index):
                        account_index = 0
                        for i in range(3):
                            await asyncio.sleep(1)
                            d.press("back")
                    break
                except Exception:
                    restart_tiktok(d)
                    continue


async def main():
    while True:
        if len(commenting_link_tasks) <= 0:
            await asyncio.sleep(1)
            continue

        devices = adb.get_devices_list()
        for task in commenting_link_tasks:
            post_comments_in_video_with_link(devices[0], task["url"], task["comment"], task["chatid"])
