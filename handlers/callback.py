from aiogram import types, Dispatcher, F, Bot

from keyboards.keyboards import user_menu


async def aboutme_hend(query: types.CallbackQuery):
    await query.message.edit_text("Рад, что ты спросил\n"
                         'Я на самом деле редко говорю о себе, но мама говорит, что я классный', reply_markup=user_menu)

async def name_hend(query: types.CallbackQuery, bot: Bot):
    await query.message.edit_text(f'Меня зовут {(await bot.get_me()).full_name}. '
                         f'А как тебя зовут? Хотя, можешь не отвечать, я не смогу прочитать', reply_markup=user_menu)

def register_callbacks(dp: Dispatcher):
    dp.callback_query.register(aboutme_hend, F.data == 'aboutme')
    dp.callback_query.register(name_hend, F.data == 'name')