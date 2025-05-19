from ui2funcs.other import write, wait_for_element, restart_tiktok
from telegram import jsondb
from utils import gpt
import adb

import time
from random import randint, choice
import asyncio
import logging

import requests
from dotenv import dotenv_values
import uiautomator2 as u2

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


def check_used_account(d, account_element):
    bounds = account_element.info["bounds"]
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
            return True

    return False


def go_to_change_account(d):
    screen_width = d.window_size()[0]
    screen_height = d.window_size()[1]

    while True:
        element_result = wait_for_element(d, ['//android.widget.Button[@content-desc="Фото профиля"]',
                                              "//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]",
                                              '//android.widget.TextView[@text="Сменить аккаунт"]',
                                              "//androidx.recyclerview.widget.RecyclerView/android.widget.Button"])

        if element_result == '//android.widget.Button[@content-desc="Фото профиля"]':
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
        elif element_result == "//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]":
            d.xpath('//android.widget.FrameLayout[@content-desc="Профиль"]').click()
            d.xpath('//android.widget.Button[@content-desc="Фото профиля"]').wait(timeout=60)
        elif element_result == '//android.widget.TextView[@text="Сменить аккаунт"]':
            d.xpath('//android.widget.TextView[@text="Сменить аккаунт"]').click()
        elif element_result == "//androidx.recyclerview.widget.RecyclerView/android.widget.Button":
            break
        else:
            raise Exception("Error")
        d.sleep(3)


def get_accounts_name(d):
    go_to_change_account(d)

    d.sleep(1)
    accounts = d.xpath("//androidx.recyclerview.widget.RecyclerView/android.widget.Button").all()

    accounts_result = []
    for account in accounts:
        account_name = account.attrib.get("content-desc", None)
        if account_name != "Добавить аккаунт":
            if not check_used_account(d, account):
                accounts_result.append(account_name)

    return accounts_result


def change_account(d, account_name):
    go_to_change_account(d)
    d.sleep(1)
    d.xpath(f'//android.widget.Button[@content-desc="{account_name}"]').click()


def post_comment(d, text: str):
    d.xpath("//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]").wait(timeout=60)
    d.sleep(1)
    d.xpath("//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]").click()

    element_result = wait_for_element(d, ['//android.widget.TextView[@text="Этот автор отключил комментарии"]',
                                          '//android.widget.EditText[@text="Добавить комментарий..."]'])
    if element_result == '//android.widget.TextView[@text="Этот автор отключил комментарии"]':
        return False
    elif element_result == '//android.widget.EditText[@text="Добавить комментарий..."]':
        d.xpath('//android.widget.EditText[@text="Добавить комментарий..."]').wait(timeout=60)
        d.sleep(1)
        write(d, d.xpath(f'//android.widget.EditText[@text="Добавить комментарий..."]'), text)
        d.sleep(1)
        d.xpath('//android.widget.Button[@content-desc="Прокомментировать"]').click()
        d.sleep(3)
        d.press("back")
        d.sleep(1)
    else:
        raise Exception("Error")

    return True


def get_link_from_video(d):
    d.xpath("//android.widget.Button[contains(@content-desc, 'Поделиться видео.')]").click()
    d.xpath('//android.widget.Button[@content-desc="Ссылка"]').wait(timeout=60)
    d.sleep(1)
    d.xpath('//android.widget.Button[@content-desc="Ссылка"]').click()
    d.sleep(3)
    return d.clipboard


def open_video_with_link(d, url: str):
    d.open_url(url)

    d.sleep(1)
    while True:
        element_result = wait_for_element(d, [
            '//android.widget.Button[@text="Открыть TikTok"]',
            '//android.widget.ImageView[@content-desc="Воспроизвести"]',
            '//android.widget.Button[@resource-id="com.android.chrome:id/message_primary_button" and '
            '@text="Продолжить"]'
        ], timeout=30)

        d.sleep(1)

        if element_result:
            d.xpath(element_result).click()
            if element_result == '//android.widget.ImageView[@content-desc="Воспроизвести"]':
                break
        else:
            break

    d.xpath("//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]").wait(timeout=60)


def swipe_video(d):
    screen_width = d.window_size()[0]
    screen_height = d.window_size()[1]

    d.swipe(screen_width // 2, screen_height - 300,
            screen_width // 2, 300)


def post_comments_in_video_with_link(device_id: str, url: str, comment: str, chatid: int):
    logger = logging.getLogger(device_id)

    d = u2.connect(device_id)

    logger.info("Успешно подключился к устройству")

    if "com.zhiliaoapp.musically" not in d.app_list():
        return False

    phone_setup(d)

    logger.info("Настроил устройство")

    while True:
        try:
            (d.xpath("//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]")
             .wait(timeout=60))
            break
        except Exception as e:
            logger.info(f"Не удалось запустить тик ток. Ошибка: {e}. Перезапускаю приложение")
            restart_tiktok(d)
            continue

    logger.info("Запустил тик ток")

    while True:
        try:
            logger.info("Меняю аккаунт")
            accounts = get_accounts_name(d)
            if len(accounts) <= 0:
                for i in range(3):
                    d.sleep(1)
                    d.press("back")
                logger.warning("Не удалось сменить аккаунт. Продолжаю работу")
            else:
                change_account(d, choice(accounts))
                d.xpath("//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]").wait(
                    timeout=120)
                logger.info("Успешно сменил аккаунт. Жду 20 сек для применения аккаунта")
                d.sleep(20)
            break

        except Exception as e:
            logger.error(f"Ошибка при смене аккаунта: {e}. Перезапускаю тик ток")
            restart_tiktok(d)
            continue

    while True:
        try:
            logger.info(f'Открываю видео по ссылке: "{url}"')
            open_video_with_link(d, url)

            if jsondb.get_use_unic_on_links():
                unic_comment = gpt.create_comment(comment)
                logger.info(f'Уникализировал комментарий: "{unic_comment}"')
            else:
                unic_comment = comment

            if post_comment(d, unic_comment):
                logger.info(f'Запостил коментарий комментарий: "{unic_comment}"')
                output_text = f"{url} | {unic_comment}"
            else:
                logger.warning(f"Автор отключил комментарии под видео")
                output_text = f"[{url}]: Автор отключил комментарии под видео"

            try:
                send_message(chatid, output_text)
                logger.warning(f'Отправил отстук: "{output_text}"')
            except Exception:
                pass
            break
        except Exception as e:
            logger.error(f"Ошибка при отправлении комментария: {e}. Перезапускаю тик ток")
            restart_tiktok(d)
            continue

    logger.critical("Успешно завершил работу\n")
    return True


async def post_comments_in_recommendations(device_id, comment: str, comments_in_one_account: int, comment_period: int,
                                           chatid: int):
    logger = logging.getLogger(device_id)

    d = u2.connect(device_id)

    logger.info("Успешно подключился к устройству")

    if "com.zhiliaoapp.musically" not in d.app_list():
        return False

    phone_setup(d)

    logger.info("Настроил устройство")

    while True:
        try:
            (d.xpath("//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]")
             .wait(timeout=60))
            break
        except Exception as e:
            logger.info(f"Не удалось запустить тик ток. Ошибка: {e}. Перезапускаю приложение")
            restart_tiktok(d)
            continue

    logger.info("Запустил тик ток")

    accounts = get_accounts_name(d)
    for i in range(3):
        d.sleep(1)
        d.press("back")
    d.sleep(1)

    comments_count = 0
    last_reset = time.time()

    while True:
        await asyncio.sleep(1)
        swipe_video(d)
        watch_video = randint(1, 15)
        logger.info(f"Просматриваю видео: {watch_video} сек")
        await asyncio.sleep(watch_video)

        current_time = time.time()
        if int(current_time - last_reset) >= int(comment_period):
            if (
                    d.xpath('//android.widget.TextView[@text="Проведите вверх, чтобы пропустить"]').exists
                    or d.xpath('//android.widget.Button[@text="Не интересно"]').exists
            ):
                continue

            unic_comment = gpt.create_comment(comment)
            logger.info(f'Уникализировал комментарий: "{unic_comment}"')
            try:
                if post_comment(d, unic_comment):
                    logger.info(f'Запостил коментарий комментарий: "{unic_comment}"')
                else:
                    logger.info(f'Автор отключил комментарии на видео. Продолжаю работу')
                    continue
            except Exception as e:
                logger.error(f"Ошибка при отправлении комментария: {e}. Перезапускаю тик ток")
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

            output_text = f"{url} | {unic_comment}"
            try:
                send_message(chatid, output_text)
                logger.warning(f'Отправил отстук: "{output_text}"')
            except Exception:
                pass

        if comments_count >= int(comments_in_one_account):
            accounts.pop(0)
            while True:
                try:
                    if len(accounts) <= 0:
                        accounts = get_accounts_name(d)
                        continue
                    else:
                        logger.info("Меняю аккаунт")
                        change_account(d, accounts[0])
                        d.xpath(
                            "//android.widget.Button[contains(@content-desc, 'Прочитать или оставить комментарии.')]").wait(
                            timeout=120)
                        logger.info("Успешно сменил аккаунт. Жду 20 сек для применения аккаунта")
                        d.sleep(20)
                    break
                except Exception as e:
                    logger.error(f"Ошибка при смене аккаунта: {e}. Перезапускаю тик ток")
                    restart_tiktok(d)
                    continue


async def main():
    while True:
        if len(commenting_link_tasks) > 0:
            devices = adb.get_devices_list()
            task = commenting_link_tasks.pop(0)
            logging.warning(f"Успешно взял задачу: {task}")
            post_comments_in_video_with_link(devices[0], task["url"], task["comment"], task["chatid"])
        else:
            await asyncio.sleep(1)

