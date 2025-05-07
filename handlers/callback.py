from aiogram import types, Dispatcher, F, Bot
from aiogram.fsm.context import FSMContext

from handlers.message import show_page, get_popular_cities_to, cursor, plot_company_comparison, plot_day_comparison
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
    city = callback.data.split("_", 2)[2]
    cursor.execute(f"SELECT code FROM aero WHERE city LIKE '{city}';")
    resultfrom = cursor.fetchall()
    resultfrom = resultfrom[0][0]
    newres = resultfrom.split(",")
    resultfrom = newres[0]
    await state.update_data(city_from=city)
    await state.update_data(air_from=resultfrom)
    popular_citys = await get_popular_cities_to()
    keyboard = create_city_keyboard(popular_citys, direction="to")
    await callback.message.answer("🛬 Введите город в который хотите полететь", reply_markup=keyboard)
    await state.set_state(User.air_to.state)


async def select_city_to(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    city = callback.data.split("_", 2)[2]
    cursor.execute(f"SELECT code FROM aero WHERE city LIKE '{city}';")
    resultto = cursor.fetchall()
    if resultto:
        resultto = resultto[0][0]
        newres = resultto.split(",")
        resultto = newres[0]
        if resultto == user_data['air_from']:
            await callback.message.answer(
                "Я не могу вывести статистику, вы ввели один и тот же город в качестве города вылета и прилета, выберите другой")
            return
    await state.update_data(city_to=city)
    await state.update_data(air_to=resultto)
    await callback.message.answer("📅 Выберите месяц для перелета")
    await state.set_state(User.month.state)

async def change_company_month(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    month = int(callback.data.split('_')[2])
    city_from = user_data['per_company_air_from']
    city_to = user_data['per_company_air_to']
    await plot_company_comparison(callback, city_from, city_to, month, state, edit=True)

async def change_day_month(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    month = int(callback.data.split('_')[2])
    city_from = user_data['per_day_air_from']
    city_to = user_data['per_day_air_to']
    await plot_day_comparison(callback, city_from, city_to, month, state, edit=True)


async def select_stat_air_from(callback: types.CallbackQuery, state: FSMContext):
    city = callback.data.split("_")[-1]
    cursor.execute("SELECT code FROM aero WHERE city LIKE %s;", (city,))
    resultfrom = cursor.fetchall()
    resultfrom = resultfrom[0][0]
    newres = resultfrom.split(",")
    resultfrom = newres[0]
    await state.update_data(per_day_air_from=resultfrom)
    await state.update_data(per_day_city_from=city)
    popular_citys = await get_popular_cities_to()
    keyboard = create_city_keyboard(popular_citys, direction="dayto")
    await callback.message.answer("🗒 Супер! теперь введите город прилета для показа статистики ", reply_markup=keyboard)
    await state.set_state(User.per_day_air_to.state)


async def select_stat_air_to(callback: types.CallbackQuery, state: FSMContext):
    city = callback.data.split("_")[-1]
    user_data = await state.get_data()
    cursor.execute("SELECT code FROM aero WHERE city LIKE %s;", (city,))
    resultto = cursor.fetchall()
    if resultto:
        resultto = resultto[0][0]
        newres = resultto.split(",")
        resultto = newres[0]
        if resultto == user_data['per_day_air_from']:
            await callback.message.answer(
                "Я не могу вывести статистику, вы ввели один и тот же город в качестве города вылета и прилета, выберите другой")
            return
    await state.update_data(per_day_air_to=resultto)
    await state.update_data(per_day_city_to=city)
    await callback.message.answer("Отлично, сейчас я покажу как менялась цена по заданому тобой маршруту 😇\n"
                         "Единственное мне не хватает дня предполагаемого вылета 📅, "
                         "можешь пожалуйста ее указать в следующем формате -> 2025-01-01 (год-месяц-день) 🥹\n"
                         "Если ты введешь некоректную дату я не буду тебя попровлять, "
                         "просто напишу что по такой дате нет статистики 😒")
    await state.set_state(User.per_day_date.state)


async def select_company_air_from(callback: types.CallbackQuery, state: FSMContext):
    city = callback.data.split("_")[-1]
    cursor.execute("SELECT code FROM aero WHERE city LIKE %s;", (city,))
    resultfrom = cursor.fetchall()
    resultfrom = resultfrom[0][0]
    newres = resultfrom.split(",")
    resultfrom = newres[0]
    await state.update_data(per_company_air_from=resultfrom)
    await state.update_data(per_company_city_from=city)
    popular_citys = await get_popular_cities_to()
    keyboard = create_city_keyboard(popular_citys, direction="companyto")
    await callback.message.answer("🗒 Супер! теперь введите город прилета для показа статистики ", reply_markup=keyboard)
    await state.set_state(User.per_company_air_to.state)


async def select_company_air_to(callback: types.CallbackQuery, state: FSMContext):
    city = callback.data.split("_")[-1]
    user_data = await state.get_data()
    cursor.execute("SELECT code FROM aero WHERE city LIKE %s;", (city,))
    resultto = cursor.fetchall()
    resultto = resultto[0][0]
    newres = resultto.split(",")
    resultto = newres[0]
    if resultto == user_data['per_company_air_from']:
        await callback.message.answer(
            "Я не могу вывести статистику, вы ввели один и тот же город в качестве города вылета и прилета, выберите другой")
        return
    await state.update_data(per_company_air_to=resultto)
    await state.update_data(per_company_city_to=city)
    user_data = await state.get_data()
    city_from = user_data['per_company_air_from']
    city_to = user_data['per_company_air_to']
    umounth = user_data['per_company_date']
    await callback.message.answer("Отлично, сейчас я покажу как менялась цена в зависимости от компаний 😇")
    await plot_company_comparison(callback, city_from, city_to, umounth, state, edit=True)


def register_callbacks(dp: Dispatcher):
    dp.callback_query.register(aboutme_hend, F.data == 'aboutme')
    dp.callback_query.register(name_hend, F.data == 'name')
    dp.callback_query.register(paginate_callback, F.data.in_(['next', 'prev']))
    dp.callback_query.register(select_city_from, F.data.startswith("select_from_"))
    dp.callback_query.register(select_city_to, F.data.startswith("select_to_"))
    dp.callback_query.register(select_stat_air_from, F.data.startswith("select_dayfrom_"))
    dp.callback_query.register(select_stat_air_to, F.data.startswith("select_dayto_"))
    dp.callback_query.register(select_company_air_from, F.data.startswith("select_companyfrom_"))
    dp.callback_query.register(select_company_air_to, F.data.startswith("select_companyto_"))
    dp.callback_query.register(change_company_month, lambda c: c.data.startswith('month_company_'))
    dp.callback_query.register(change_day_month, lambda c: c.data.startswith('month_day_'))