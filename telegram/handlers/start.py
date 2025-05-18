from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from telegram.utils import keyboards as kb, texts as txt
from telegram.utils.states import Commenting_Link, Commenting_Recommendations

from ui2funcs.autocommenting import (post_comments_in_recommendations, add_task_in_commenting_link_tasks,
                                     get_len_tasks_in_commenting_link_tasks)
import adb

import asyncio

router = Router()

running_tasks = {}


@router.message(F.text == txt.kb_main)
async def start(message: Message):
    devices = adb.get_devices_list()
    if len(devices) > 0:
        await message.answer("🚀", reply_markup=ReplyKeyboardRemove())
        await message.answer("Выберите на что накручивать:", reply_markup=kb.start())
    else:
        await message.answer("Для работы софта подключите устройство")


@router.callback_query(F.data == "start:link")
async def commenting_link(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await callback.message.edit_text("Пришлите: «Ссылка на видео | Текст комментария»", reply_markup=kb.back("start"))
    await state.set_state(Commenting_Link.commenting_link)


@router.message(Commenting_Link.commenting_link)
async def commenting_link_finish(message: Message):
    try:
        url, comment = message.text.split(" | ")

        if ".tiktok.com" not in url:
            await message.answer("Вы указали некорректную ссылку на видео. Введите новый текст")
            return

        add_task_in_commenting_link_tasks({"url": url, "comment": comment, "chatid": message.from_user.id})

        await message.answer(f"Успешно создал задачу:\n"
                             f"Ссылка на видео: {url}\n"
                             f"Текст комментария: {comment}\n", reply_markup=kb.back("start"))
    except ValueError:
        await message.answer("Вы не указали один из аргументов. Введите новый текст")


@router.callback_query(F.data == "start:recommendations")
async def commenting_recommendations(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    len_tasks = get_len_tasks_in_commenting_link_tasks()
    if len_tasks > 0:
        await callback.message.answer(f"Подождите пока софт пройдёт все задачи. Кол-во задач: {len_tasks}")
        await callback.message.answer("Выберите на что накручивать:", reply_markup=kb.start())
        return

    await callback.message.edit_text("Пришлите: «Текст комментария | Лимит комментариев с одного аккаунта | Период "
                                     "между комментариями (в секундах)»", reply_markup=kb.back("start"))
    await state.set_state(Commenting_Recommendations.commenting_recommendations)


@router.message(Commenting_Recommendations.commenting_recommendations)
async def commenting_recommendations_finish(message: Message, state: FSMContext):
    try:
        comment, comments_in_one_account, comment_period = message.text.split(" | ")

        if type(comments_in_one_account) == str:
            if not comments_in_one_account.isdigit():
                await message.answer("Вы указали неверный лимит комментариев с одного аккаунта. Введите новый текст")
                return
        if type(comment_period) == str:
            if not comment_period.isdigit():
                await message.answer("Вы указали неверный период между комментариями. Введите новый текст")
                return

        await message.answer(f"Успешно запустил комментинг по рекомендациям:\n"
                             f"Текст комментария: {comment}\n"
                             f"Лимит комментариев с одного аккаунта: {comments_in_one_account}\n"
                             f"Период между комментариями: {comment_period} сек\n",
                             reply_markup=kb.commenting_recommendations())

        task1_obj = asyncio.create_task(post_comments_in_recommendations(adb.get_devices_list()[0], comment,
                                                                         comments_in_one_account, comment_period,
                                                                         message.from_user.id))
        running_tasks["tasks"] = [task1_obj]

        await state.clear()
    except ValueError:
        await message.answer("Вы не указали один из аргументов. Введите новый текст")


@router.message(F.text == "⛔️ Остановить задачу")
async def commenting_recommendations_stop(message: Message):
    if "tasks" not in running_tasks:
        await message.answer("⚠ Нет активных задач!", reply_markup=ReplyKeyboardRemove())
        await message.answer("Выберите на что накручивать:", reply_markup=kb.start())
    else:
        for task in running_tasks["tasks"]:
            task.cancel()
        running_tasks.pop("tasks", None)

        await message.answer('Задача остановлена ⛔️', reply_markup=ReplyKeyboardRemove())
        await message.answer("Выберите на что накручивать:", reply_markup=kb.start())


@router.callback_query(F.data == "back:start")
async def back(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Выберите на что накручивать:", reply_markup=kb.start())
    await state.clear()
