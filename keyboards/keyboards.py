from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

user_menu = types.InlineKeyboardMarkup(inline_keyboard=[
    [types.InlineKeyboardButton(text='Обо мне', callback_data='aboutme'),
     types.InlineKeyboardButton(text='Имя', callback_data='name')]
])

def create_city_keyboard(cities: list[str], direction: str) -> InlineKeyboardMarkup:
    title_cities = []
    for el in cities:
        title_cities.append(el.title())
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=title_cities[0], callback_data=f"select_{direction}_{title_cities[0]}"),
         types.InlineKeyboardButton(text=title_cities[1], callback_data=f"select_{direction}_{title_cities[1]}"),
         types.InlineKeyboardButton(text=title_cities[2], callback_data=f"select_{direction}_{title_cities[2]}"),
         types.InlineKeyboardButton(text=title_cities[3], callback_data=f"select_{direction}_{title_cities[3]}")]
    ])
    return keyboard


