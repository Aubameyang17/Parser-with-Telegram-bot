from aiogram.fsm.state import StatesGroup, State

class User(StatesGroup):
    air_from = State()
    air_to = State()
    month = State()
    day = State()