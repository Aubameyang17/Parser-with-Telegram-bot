from aiogram import types

user_menu = types.InlineKeyboardMarkup(inline_keyboard=[
    [types.InlineKeyboardButton(text='Обо мне', callback_data='aboutme'),
     types.InlineKeyboardButton(text='Имя', callback_data='name')]
])

