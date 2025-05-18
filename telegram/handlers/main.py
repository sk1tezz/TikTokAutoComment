from aiogram import Router, F
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from telegram.utils import keyboards as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(f"Добро пожаловать @{message.from_user.username}!", reply_markup=kb.main())
    await state.clear()


@router.callback_query(F.data == "back:main")
async def back(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Возвращаюсь в главное меню!", reply_markup=kb.main())
    await state.clear()
