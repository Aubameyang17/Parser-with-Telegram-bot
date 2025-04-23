from aiogram.fsm.state import StatesGroup, State

class User(StatesGroup):
    air_from = State()
    city_from = State()
    city_to = State()
    air_to = State()
    month = State()
    day = State()