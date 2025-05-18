from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from telegram import jsondb
from telegram.utils import keyboards as kb


router = Router()


@router.message(F.text == "⚙ Настройки")
async def settings(message: Message):
    await message.answer("⚙", reply_markup=ReplyKeyboardRemove())
    await message.answer('Какие настройки вы хотите изменить?', reply_markup=kb.settings())


@router.callback_query(F.data == "settings:use_unic_on_links")
async def use_default_likes(callback: CallbackQuery):
    await callback.answer()
    jsondb.toggle_use_unic_on_links()
    await callback.message.delete()
    await callback.message.answer('Какие настройки вы хотите изменить?', reply_markup=kb.settings())
