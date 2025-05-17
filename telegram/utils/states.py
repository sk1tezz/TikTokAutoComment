from aiogram.fsm.state import StatesGroup, State


class Commenting_Link(StatesGroup):
    commenting_link = State()


class Commenting_Recommendations(StatesGroup):
    commenting_recommendations = State()


class Pages(StatesGroup):
    pages = State()
