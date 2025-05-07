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

def create_month_keyboard(type_stat: str):
    buttons = [
        [InlineKeyboardButton(text="Январь", callback_data=f"month_{type_stat}_1"),
         InlineKeyboardButton(text="Февраль", callback_data=f"month_{type_stat}_2"),
         InlineKeyboardButton(text="Март", callback_data=f"month_{type_stat}_3")],
        [InlineKeyboardButton(text="Апрель", callback_data=f"month_{type_stat}_4"),
         InlineKeyboardButton(text="Май", callback_data=f"month_{type_stat}_5"),
         InlineKeyboardButton(text="Июнь", callback_data=f"month_{type_stat}_6")],
        [InlineKeyboardButton(text="Июль", callback_data=f"month_{type_stat}_7"),
         InlineKeyboardButton(text="Август", callback_data=f"month_{type_stat}_8"),
         InlineKeyboardButton(text="Сентябрь", callback_data=f"month_{type_stat}_9")],
        [InlineKeyboardButton(text="Октябрь", callback_data=f"month_{type_stat}_10"),
         InlineKeyboardButton(text="Ноябрь", callback_data=f"month_{type_stat}_11"),
         InlineKeyboardButton(text="Декабрь", callback_data=f"month_{type_stat}_12")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

