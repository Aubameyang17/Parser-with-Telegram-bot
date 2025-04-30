from aiogram import types, Dispatcher, F, Bot
from aiogram.fsm.context import FSMContext

from handlers.message import show_page, get_popular_cities_to, get_db_cursor
from keyboards.keyboards import user_menu, create_city_keyboard
from states.state import User


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


async def select_city_from(callback: types.CallbackQuery, state: FSMContext):
    conn, cursor = get_db_cursor()
    try:
        city = callback.data.split("_", 2)[2]
        cursor.execute(f"SELECT code FROM aero WHERE city LIKE '{city}';")
        resultfrom = cursor.fetchall()
        resultfrom = resultfrom[0][0]
        newres = resultfrom.split(",")
        resultfrom = newres[0]
        await state.update_data(city_from=city)
        await state.update_data(air_from=resultfrom)
        popular_citys = get_popular_cities_to(cursor)
        keyboard = create_city_keyboard(popular_citys, direction="to")
        await callback.message.answer("🛬 Введите город в который хотите полететь", reply_markup=keyboard)
        await state.set_state(User.air_to.state)
    finally:
        cursor.close()
        conn.close()

async def select_city_to(callback: types.CallbackQuery, state: FSMContext):
    conn, cursor = get_db_cursor()
    try:
        city = callback.data.split("_", 2)[2]
        cursor.execute(f"SELECT code FROM aero WHERE city LIKE '{city}';")
        resultto = cursor.fetchall()
        resultto = resultto[0][0]
        newres = resultto.split(",")
        resultto = newres[0]
        await state.update_data(city_to=city)
        await state.update_data(air_to=resultto)
        await callback.message.answer("📅 Выберите месяц для перелета")
        await state.set_state(User.month.state)
    finally:
        cursor.close()
        conn.close()



def register_callbacks(dp: Dispatcher):
    dp.callback_query.register(aboutme_hend, F.data == 'aboutme')
    dp.callback_query.register(name_hend, F.data == 'name')
    dp.callback_query.register(paginate_callback, F.data.in_(['next', 'prev']))
    dp.callback_query.register(select_city_from, F.data.startswith("select_from_"))
    dp.callback_query.register(select_city_to, F.data.startswith("select_to_"))