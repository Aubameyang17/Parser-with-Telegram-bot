from aiogram import types, Dispatcher, F, Bot
from aiogram.fsm.context import FSMContext

from handlers.message import show_page
from keyboards.keyboards import user_menu


async def aboutme_hend(query: types.CallbackQuery):
    await query.message.edit_text("Рад, что ты спросил\n"
                         'Я на самом деле редко говорю о себе, но мама говорит, что я классный', reply_markup=user_menu)

async def name_hend(query: types.CallbackQuery, bot: Bot):
    await query.message.edit_text(f'Меня зовут {(await bot.get_me()).full_name}. '
                         f'А как тебя зовут? Хотя, можешь не отвечать, я не смогу прочитать', reply_markup=user_menu)

async def paginate_callback(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    page = user_data.get('page', 0)
    flights = user_data.get('all_flights', [])

    if callback.data == "next":
        page += 1
    elif callback.data == "prev" and page > 0:
        page -= 1

    if page < 0:
        page = 0
    elif page >= len(flights):
        page = len(flights) - 1

    await state.update_data(page=page)

    await callback.message.delete()
    await show_page(callback.message, flights, page, user_data)

    await callback.answer()

def register_callbacks(dp: Dispatcher):
    dp.callback_query.register(aboutme_hend, F.data == 'aboutme')
    dp.callback_query.register(name_hend, F.data == 'name')
    dp.callback_query.register(paginate_callback, F.data.in_(['next', 'prev']))