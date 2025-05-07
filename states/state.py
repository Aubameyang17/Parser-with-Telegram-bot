from aiogram.fsm.state import StatesGroup, State

class User(StatesGroup):
    air_from = State()
    air_to = State()
    month = State()
    day = State()
    city_from = State()
    city_to = State()

    all_flights = State()
    year = State()

    per_day_air_from = State()
    per_day_city_from = State()
    per_day_air_to = State()
    per_day_city_to = State()
    per_day_date = State()

    per_company_air_from = State()
    per_company_city_from = State()
    per_company_air_to = State()
    per_company_city_to = State()
    per_company_date = State()

