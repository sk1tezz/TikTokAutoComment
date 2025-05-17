from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.utils import texts as txt


def start():
    kb = [
        [InlineKeyboardButton(text=txt.kb_link, callback_data=f"start:link"),
         InlineKeyboardButton(text=txt.kb_recommendations, callback_data=f"start:recommendations")]
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
