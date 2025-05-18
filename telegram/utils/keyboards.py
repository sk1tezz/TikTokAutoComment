from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.utils import texts as txt
from telegram import jsondb


def main():
    kb = [
        [KeyboardButton(text=txt.kb_main), KeyboardButton(text=txt.kb_settings)]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def settings():
    if jsondb.get_use_unic_on_links():
        buttons = [
            [InlineKeyboardButton(text=f"Использовать уникализатор на комментинг по ссылкам?: [Да]", callback_data="settings:use_unic_on_links")],
            [InlineKeyboardButton(text="Назад", callback_data="back:main")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text=f"Использовать уникализатор на комментинг по ссылкам?: [Нет]", callback_data="settings:use_unic_on_links")],
            [InlineKeyboardButton(text="Назад", callback_data="back:main")]
        ]


    return InlineKeyboardMarkup(inline_keyboard=buttons)


def start():
    kb = [
        [InlineKeyboardButton(text=txt.kb_link, callback_data=f"start:link"),
         InlineKeyboardButton(text=txt.kb_recommendations, callback_data=f"start:recommendations")],
        [InlineKeyboardButton(text="Назад", callback_data="back:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def commenting_recommendations():
    kb = [
        [KeyboardButton(text=txt.kb_recommendations_stop)]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def back(callback: str):
    buttons = [[InlineKeyboardButton(text="Назад", callback_data=f"back:{callback}")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
