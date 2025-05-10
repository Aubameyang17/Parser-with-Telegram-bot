import io
import traceback
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram import Dispatcher, types, Bot
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
import asyncio
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import psycopg2
from aiogram.fsm.context import FSMContext
from pobedaparser import pobeda
from aeroflot_Parser import osnovnoe
from UrAirparser import uralair
from smartaviaparser import smartavia
from keyboards.keyboards import create_city_keyboard, create_month_keyboard
from sql_file import create_table, take_orders
from states.state import User

month_to_number = {'январь': "01", 'февраль': "02", 'март': "03", 'апрель': "04", 'май': "05", 'июнь': "06",
                   'июль': "07", 'август': "08", 'сентябрь': "09", 'октябрь': "10", 'ноябрь': "11", 'декабрь': "12"}
nechet = ['январь', 'март', 'май', 'июль', 'август', 'октябрь', 'декабрь']
chet = ['апрель', 'июнь', 'сентябрь', 'ноябрь']
year = datetime.date.today().year
month = datetime.date.today().month
day = datetime.date.today().day
conn = psycopg2.connect(dbname="Aeroports", host="127.0.0.1", user="Alex", password="alex")
cursor = conn.cursor()


async def run_all_parsers_parallel(resultfrom, resultto, usermonth, userdate, conn, cursor, name, year):
    results = await asyncio.gather(
        osnovnoe(resultfrom, resultto, usermonth, userdate, conn, cursor, name, year),
        pobeda(resultfrom, resultto, usermonth, userdate, conn, cursor, name, year),
        uralair(resultfrom, resultto, usermonth, userdate, conn, cursor, name, year),
        smartavia(resultfrom, resultto, usermonth, userdate, conn, cursor, name, year)
    )
    return results

async def get_popular_cities_from():
    cursor.execute("SELECT airfrom FROM orders GROUP BY airfrom ORDER BY COUNT(*) DESC LIMIT 4")
    result = cursor.fetchall()
    mass = []
    for i in range(len(result)):
        mass.append(result[i][0])
    cities = []
    for el in mass:
        cursor.execute("SELECT city FROM aero WHERE code LIKE %s", (f"%{el}%",))
        city = cursor.fetchone()[0]
        cities.append(city)
    return cities

async def get_popular_cities_to():
    cursor.execute("SELECT airto FROM orders GROUP BY airto ORDER BY COUNT(*) DESC LIMIT 4")
    result = cursor.fetchall()
    mass = []
    for i in range(len(result)):
        mass.append(result[i][0])
    cities = []
    for el in mass:
        cursor.execute("SELECT city FROM aero WHERE code LIKE %s", (f"%{el}%",))
        city = cursor.fetchone()[0]
        cities.append(city)
    return cities


async def show_fake_loading(message, status=True):
    loading_phrases = [
        "🔎 Ищем билеты.",
        "🔎 Ищем билеты..",
        "🔎 Ищем билеты...",
        "🔎 Ищем билеты"
    ]
    loading_msg = await message.answer("🔎 Ищем билеты")
    try:
        while status:
            for text in loading_phrases:
                await asyncio.sleep(1.5)
                await loading_msg.edit_text(text)
    except asyncio.CancelledError:
        # При отмене (когда закончим загрузку) просто удалим сообщение
        await loading_msg.delete()



async def add_user(user_id: int, username: str):
    cursor.execute("SELECT * FROM telegramusers WHERE user_id = %s", (user_id,))
    chek_user = cursor.fetchone()
    if chek_user is None:
        cursor.execute(
            "INSERT INTO telegramusers (user_id, username) VALUES (%s, %s)",
            (user_id, username)
        )
        conn.commit()


def run_async_in_thread(coro):
    return asyncio.run(coro)



async def start_command(message: types.Message):
    await add_user(message.from_user.id, message.from_user.username)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text='/start'), types.KeyboardButton(text='/air'), types.KeyboardButton(text='/repeat')]
    ])
    await message.answer(f'Добрый день, {message.from_user.full_name} 😉\n'
                         f'Рад вас видеть, напишите /air, чтобы начать искать билеты '
                         f'или /repeat чтобы повторить предыдущий запрос, вы также можете написать команду '
                         f'/help которая расскажет о других доступных командах', reply_markup=kb)

async def help_command(message: types.Message):
    await message.answer(f'Добрый день, {message.from_user.full_name} 😌\n'
                         f'Сейчас я расскажу какие команды доступны в этой версии бота:\n'
                         f'/start - начальная команда которая вас поприветсвует\n'
                         f'/air - эта команда позволит вам сделать запрос на просмотр билетов\n'
                         f'/repeat - с помощью этой команды вы сможите повторить ваш предыдущий запрос\n'
                         f'/stats - эта команда вас познвкомит с правилами вывода статистики\n'
                         f'/stats_per_company - эта команда позволит вам увидеть '
                         f'сравнение цен по компаниям на определенное направление\n'
                         f'/stats_per_day - эта команда покажет статистику изменения '
                         f'цен по дням на определенное направление')

async def air_from_handler(message: types.Message, state: FSMContext):
    popular_citys = await get_popular_cities_from()
    keyboard = create_city_keyboard(popular_citys, direction="from")
    await message.answer("🛫 Откуда полетим?", reply_markup=keyboard)
    await state.set_state(User.air_from.state)


async def air_to_handler(message: types.Message, state: FSMContext):
    cursor.execute("SELECT code FROM aero WHERE LOWER(city) LIKE %s;", (message.text.lower(),))
    resultfrom = cursor.fetchall()
    if resultfrom:
        resultfrom = resultfrom[0][0]
        newres = resultfrom.split(",")
        resultfrom = newres[0]
    else:
        await message.answer("Такого города не существует, попробуйте еще раз")
        return
    await state.update_data(air_from=resultfrom)
    await state.update_data(city_from=message.text)
    popular_citys = await get_popular_cities_to()
    keyboard = create_city_keyboard(popular_citys, direction="to")
    await message.answer("🛬 Введите город в который хотите полететь", reply_markup=keyboard)
    await state.set_state(User.air_to.state)



async def month_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cursor.execute("SELECT code FROM aero WHERE lower(city) LIKE %s;", (message.text.lower(),))
    resultto = cursor.fetchall()
    if resultto:
        resultto = resultto[0][0]
        newres = resultto.split(",")
        resultto = newres[0]
        if resultto == user_data['air_from']:
            await message.answer(
                "Вы хотите полетать по городу? Могу посоветовать не повторять 11 сентября и сменить город назначения")
            return
    else:
        await message.answer("Такого города не существует, попробуйте еще раз")
        return
    await state.update_data(air_to=resultto)
    await state.update_data(city_to=message.text)
    await message.answer("📅 Выберите месяц для перелета")
    await state.set_state(User.month.state)

async def day_handler(message: types.Message, state: FSMContext):
    global year
    if message.text.lower() in month_to_number.keys():
        pass
    else:
        await message.answer("Такого месяца не существует, попробуйте еще раз")
        return
    await state.update_data(month=message.text.lower())
    await message.answer("📅 На какое число смотреть билеты? ")
    await state.set_state(User.day.state)


async def vivod_handler(message: types.Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    global year
    newyear = year
    try:
        userdate = int(message.text)
    except Exception:
        await message.answer("Это не число 😔")
        return
    if int(month_to_number[user_data['month']]) == month and userdate < day or int(
            month_to_number[user_data['month']]) < month:
        newyear = int(newyear) + 1
        await message.answer("Такой даты в этом году уже нет, поэтому был выбран следующий год")
    elif user_data['month'] in chet and int(userdate) in range(1, 31):
        pass
    elif user_data['month'] in nechet and int(userdate) in range(1, 32):
        pass
    elif user_data['month'] == 'Февраль' and int(year) % 4 == 0 and int(userdate) in range(1, 30):
        pass
    elif user_data['month'] == 'Февраль' and int(year) % 4 != 0 and int(userdate) in range(1, 29):
        pass
    else:
        await message.answer("Такой даты нет в выбраном месяце 😔")
        return
    await state.update_data(day=message.text)
    await state.update_data(year=newyear)
    user_data = await state.get_data()
    await message.answer(
        f"Отлично, сейчас посмотрим какие есть предложения по билетам из {user_data['city_from']} в "
        f"{user_data['city_to']} {userdate} {user_data['month']} {newyear}г. 🕒")
    create_table(str(message.from_user.id), cursor, conn)
    userid = message.from_user.id
    name = '"' + str(userid) + "flyghts" + '"'
    loading_task = asyncio.create_task(show_fake_loading(message))

    try:
        resultt = await asyncio.to_thread(
            run_async_in_thread,
            run_all_parsers_parallel(
                user_data['air_from'],
                user_data['air_to'],
                user_data['month'],
                userdate,
                cursor,
                conn,
                name,
                newyear
            )
        )
    finally:
        loading_task.cancel()
    cursor.execute('SELECT * FROM ' + name + ' ORDER BY price asc')
    result = cursor.fetchall()
    if result:
        await state.update_data(all_flights=result, page=0)
        await show_page(message, result, 0, user_data)
    else:
        await message.answer(
            "Рейсы не найдены, попробуйте выбрать другие даты. 😔\n"
            "Также могла произойти ошибка — попробуйте снова."
        )
    try:
        take_orders(name, userid, user_data['air_from'], user_data['air_to'], user_data['month'], user_data['day'],
                            cursor, conn)
    except Exception:
        traceback.print_exc()
        print("take orders")


async def show_page(message: types.Message, flights, page, user_data):
    total_flights = len(flights)

    if page < 0:
        page = 0
    elif page >= total_flights:
        page = total_flights - 1

    el = flights[page]

    text = ""
    time_from, airfrom, timeto, plusday, airto, compname, price, leftsit = el[1:9]
    plusday = plusday.replace('+', '\+')
    cursor.execute("SELECT city FROM aero WHERE code LIKE %s", (f"%{airfrom}%",))
    city_from = cursor.fetchone()[0]
    city_from = city_from.replace('-', '\-')
    cursor.execute("SELECT city FROM aero WHERE code LIKE %s", (f"%{airto}%",))
    city_to = cursor.fetchone()[0]
    city_to = city_to.replace('-', '\-')
    text += (f"Cтраница {page + 1}/{total_flights}\n"
                f"✈ \**{compname}*\*\n"
                f"_{city_from}_ \({airfrom}\) \- _{city_to}_ \({airto}\) \n📅 __Вылет__: {user_data['day']} "
                f"{user_data['month']} {plusday}  \|  ⏰  {time_from} \- {timeto}\n"
                f"💰  Цена: _\*{price}₽\*_\n💺 {leftsit}\n\n")

    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="prev"),
            InlineKeyboardButton(text="➡️ Вперед", callback_data="next")
        ]
    ])
    await message.answer(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN_V2)


async def repeat_order(message: types.Message, state: FSMContext):
    newyear = year
    cursor.execute(f"SELECT airfrom from orders WHERE id_user = {message.from_user.id} ORDER BY id desc")
    airfrom_table = cursor.fetchone()[0]
    cursor.execute(f"SELECT airto from orders WHERE id_user = {message.from_user.id} ORDER BY id desc")
    airto_table = cursor.fetchone()[0]
    cursor.execute(f"SELECT month from orders WHERE id_user = {message.from_user.id} ORDER BY id desc")
    month_table = cursor.fetchone()[0]
    cursor.execute(f"SELECT userdate from orders WHERE id_user = {message.from_user.id} ORDER BY id desc")
    day_table = cursor.fetchone()[0]
    if int(month_to_number[month_table]) == month and int(day_table) < day or int(month_to_number[month_table]) < month:
        newyear = int(newyear) + 1

    if airfrom_table:
        await message.answer(
            f"Хорошо, давай вновь посмотрим какие есть предложения по билетам из {airfrom_table} в "
            f"{airto_table} {day_table} {month_table} {newyear} 🕒")
        create_table(str(message.from_user.id), cursor, conn)
        userid = message.from_user.id
        name = '"' + str(userid) + "flyghts" + '"'
        resultt = await run_all_parsers_parallel(airfrom_table, airto_table,
                                                     month_table, day_table, cursor, conn, name, newyear)
        cursor.execute('SELECT * FROM ' + name + ' ORDER BY price asc')
        result = cursor.fetchall()
        if result:
            await state.update_data(air_from=airfrom_table)
            await state.update_data(air_to=airto_table)
            await state.update_data(month=month_table)
            await state.update_data(day=day_table)
            user_data = await state.get_data()
            await state.update_data(all_flights=result, page=0)
            await show_page(message, result, 0, user_data)
        else:
            await message.answer(
                "Рейсы не найдены, попробуйте выбрать другие даты. 😔\n"
                "Также могла произойти ошибка — попробуйте снова."
            )
        try:
            take_orders(name, userid, airfrom_table, airto_table, month_table, day_table, cursor, conn)
        except Exception:
            traceback.print_exc()
            print("take orders")
    else:
        await message.answer("Похоже что ты еще не создавал запросы или система дала сбой и "
                                 "информация о твоих последних запросах исчезла 😔 \n"
                                 "Попробуй создать новый запрос используя команду /air")

async def statistics(message: types.Message):
    await message.answer("📈 Привет! Ты перешел в отдел статистики! 🥸 "
                         "Значит ты готов увидеть всякие графички и картинки, чтож, это похвально, "
                         "но мне нужна некоторая информация от тебя🗿\n"
                         "выбери что именно ты хочешь увидеть из статистики\n"
                         "Я могу вывести тебе график изменения цен тебе лишь нужно написать /stats_per_day "
                         "и указать необходимую дату\n"
                         "Я также могу показать график цен от различных авиакомпаний чтобы ты увидел какая дешевле"
                         "надо просто написать /stats_per_company\n")

async def stats_per_day(message: types.Message, state: FSMContext):
    popular_citys = await get_popular_cities_from()
    keyboard = create_city_keyboard(popular_citys, direction="dayfrom")
    await message.answer("Для отображения статистики мне надо будет чтобы ты указал город вылета "
                         "(в именнительном падеже если что, только тссс...)", reply_markup=keyboard)
    await state.set_state(User.per_day_air_from.state)


async def stat_air_to_handler(message: types.Message, state: FSMContext):
    cursor.execute("SELECT code FROM aero WHERE LOWER(city) LIKE %s;", (message.text.lower(),))
    resultfrom = cursor.fetchall()
    if resultfrom:
        resultfrom = resultfrom[0][0]
        newres = resultfrom.split(",")
        resultfrom = newres[0]
    else:
        await message.answer("Такого города не существует, попробуйте еще раз 😔")
        return
    await state.update_data(per_day_air_from=resultfrom)
    await state.update_data(per_day_city_from=message.text)
    popular_citys = await get_popular_cities_to()
    keyboard = create_city_keyboard(popular_citys, direction="dayto")
    await message.answer("🗒 Супер! теперь введите город прилета для показа статистики ", reply_markup=keyboard)
    await state.set_state(User.per_day_air_to.state)


async def data_stats(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cursor.execute("SELECT code FROM aero WHERE lower(city) LIKE %s;", (message.text.lower(),))
    resultto = cursor.fetchall()
    if resultto:
        resultto = resultto[0][0]
        newres = resultto.split(",")
        resultto = newres[0]
        if resultto == user_data['per_day_air_from']:
            await message.answer(
                "Я не могу вывести статистику, вы ввели один и тот же город в качестве города вылета и прилета, выберите другой")
            return
    else:
        await message.answer("Такого города не существует, попробуйте еще раз")
        return
    await state.update_data(per_day_air_to=resultto)
    await state.update_data(per_day_city_to=message.text)
    await message.answer("Отлично, сейчас я покажу как менялась цена по заданому тобой маршруту 😇\n"
                         "Единственное мне не хватает дня предполагаемого вылета 📅, "
                         "можешь пожалуйста ее указать в следующем формате -> 2025-01-01 (год-месяц-день) 🥹\n"
                         "Если ты введешь некоректную дату я не буду тебя попровлять, "
                         "просто напишу что по такой дате нет статистики 😒")
    await state.set_state(User.per_day_date.state)


async def stats_per_day_magic(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    city_from = user_data['per_day_air_from']
    city_to = user_data['per_day_air_to']
    umounth = month
    departure_date = message.text
    await state.update_data(stat_date=departure_date)
    await plot_day_comparison(message, city_from, city_to, umounth, state)

async def plot_day_comparison(message_or_callback, city_from, city_to, umonth, state: FSMContext, edit=False):
    user_data = await state.get_data()
    conn = psycopg2.connect(dbname="Aeroports", host="127.0.0.1", user="Alex", password="alex")
    cursor = conn.cursor()
    query = """
    SELECT 
    order_date::date AS day,
    company,
    MIN(price) AS min_price
    FROM all_flyghts
    WHERE city_from = %s AND city_to = %s and fly_date = %s AND EXTRACT(MONTH FROM order_date) = %s
    GROUP BY day, company
    ORDER BY day;


    """
    df = pd.read_sql_query(query, conn, params=(city_from, city_to, user_data['stat_date'], umonth))

    # Построим график
    plt.figure(figsize=(12, 6))

    for company in df['company'].unique():
        company_data = df[df['company'] == company]
        plt.plot(company_data['day'], company_data['min_price'], label=company, marker='o')

    plt.title("Динамика минимальных цен по дням")
    plt.xlabel("Дата вылета")
    plt.ylabel("Минимальная цена (₽)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Сохраняем график во временный файл
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    image = buffer
    photo = BufferedInputFile(image.read(), filename="price_dynamics.png")
    full_city_from_name = user_data['per_day_city_from']
    full_city_to_name = user_data['per_day_city_to']
    if len(str(umonth)) == 1:
        re_month = "0" + str(umonth)
        key = next((key for key, value in month_to_number.items() if value == re_month), None)
    else:
        key = next((key for key, value in month_to_number.items() if value == str(umonth)), None)
    keyboard = create_month_keyboard(type_stat='day')
    if edit:
        await message_or_callback.message.edit_media(
            types.InputMediaPhoto(media=photo,
                                  caption=f"📊 Динамика цен: {full_city_from_name} → {full_city_to_name} "
                                          f"на {user_data['stat_date']} за {key.title()}"),
            reply_markup=keyboard
        )
    else:
        await message_or_callback.answer_photo(
            photo=photo,
            caption=f"📊 📊 Динамика цен: {full_city_from_name} → {full_city_to_name} "
                    f"на {user_data['stat_date']} за {key.title()}",
            reply_markup=keyboard
        )

async def stat_per_company(message: types.Message, state: FSMContext):
    umounth = month
    await state.update_data(per_company_date=umounth)
    popular_citys = await get_popular_cities_from()
    keyboard = create_city_keyboard(popular_citys, direction="companyfrom")
    await message.answer("Для отображения статистики мне надо будет чтобы ты указал город вылета "
                         "(в именнительном падеже если что, только тссс...)", reply_markup=keyboard)
    await state.set_state(User.per_company_air_from.state)

async def per_company_air_to_handler(message: types.Message, state: FSMContext):
    cursor.execute("SELECT code FROM aero WHERE LOWER(city) LIKE %s;", (message.text.lower(),))
    resultfrom = cursor.fetchall()
    if resultfrom:
        resultfrom = resultfrom[0][0]
        newres = resultfrom.split(",")
        resultfrom = newres[0]
    else:
        await message.answer("Такого города не существует, попробуйте еще раз 😔")
        return
    await state.update_data(per_company_air_from=resultfrom)
    await state.update_data(per_company_city_from=message.text)
    popular_citys = await get_popular_cities_to()
    keyboard = create_city_keyboard(popular_citys, direction="companyto")
    await message.answer("🗒 Супер! теперь введите город прилета для показа статистики ", reply_markup=keyboard)
    await state.set_state(User.per_company_air_to.state)


async def per_company_data_stats(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cursor.execute("SELECT code FROM aero WHERE lower(city) LIKE %s;", (message.text.lower(),))
    resultto = cursor.fetchall()
    if resultto:
        resultto = resultto[0][0]
        newres = resultto.split(",")
        resultto = newres[0]
        if resultto == user_data['per_company_air_from']:
            await message.answer(
                "Я не могу вывести статистику, вы ввели один и тот же город в качестве города вылета и прилета, выберите другой")
            return
    else:
        await message.answer("Такого города не существует, попробуйте еще раз")
        return
    await state.update_data(per_company_air_to=resultto)
    await state.update_data(per_company_city_to=message.text)
    user_data = await state.get_data()
    city_from = user_data['per_company_air_from']
    city_to = user_data['per_company_air_to']
    await message.answer("Отлично, сейчас я покажу как менялась цена в зависимости от компаний 😇")
    await plot_company_comparison(message, city_from, city_to, user_data['per_company_date'], state)

async def plot_company_comparison(message_or_callback, city_from, city_to, umonth, state: FSMContext, edit=False):
    user_data = await state.get_data()
    conn = psycopg2.connect(dbname="Aeroports", host="127.0.0.1", user="Alex", password="alex")
    cursor = conn.cursor()

    # Выполнение запроса
    query = """
    SELECT company, AVG(price) as avg_price, MIN(price) as min_price
    FROM all_flyghts
    WHERE city_from = %s AND city_to = %s AND EXTRACT(MONTH FROM fly_date) = %s
    GROUP BY company
    ORDER BY avg_price;
    """
    cursor.execute(query, (city_from, city_to, umonth))
    data = cursor.fetchall()

    # Обработка результатов
    companies = [row[0] for row in data]
    avg_prices = [row[1] for row in data]
    min_prices = [row[2] for row in data]

    x = np.arange(len(companies))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars_avg = ax.bar(x - width / 2, avg_prices, width, label='Средняя цена', color='skyblue')
    bars_min = ax.bar(x + width / 2, min_prices, width, label='Минимальная цена', color='lightgreen')
    # Добавим подписи к столбцам
    for bar in bars_avg:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 100, f'{int(height)}', ha='center', va='bottom', fontsize=9)

    for bar in bars_min:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 100, f'{int(height)}', ha='center', va='bottom', fontsize=9)

    ax.set_ylabel('Цена')
    full_city_from_name = user_data['per_company_city_from']
    full_city_to_name = user_data['per_company_city_to']
    if len(str(umonth)) == 1:
        re_month = "0" + str(umonth)
        key = next((key for key, value in month_to_number.items() if value == re_month), None)
    else:
        key = next((key for key, value in month_to_number.items() if value == str(umonth)), None)
    ax.set_title(f'Сравнение авиакомпаний по маршруту {full_city_from_name} → {full_city_to_name} месяц: {key.title()}')
    ax.set_xticks(x)
    ax.set_xticklabels(companies, rotation=45)
    ax.legend()
    ax.grid(axis='y')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    cursor.close()
    conn.close()

    keyboard = create_month_keyboard(type_stat='company')

    photo = BufferedInputFile(buf.read(), filename="chart.png")

    if edit:
        await message_or_callback.message.edit_media(
            types.InputMediaPhoto(media=photo,
                                  caption=f"📊 Сравнение компаний: {full_city_from_name} → "
                                          f"{full_city_to_name}, месяц {key.title()}"),
            reply_markup=keyboard
        )
    else:
        await message_or_callback.answer_photo(
            photo=photo,
            caption=f"📊 Сравнение компаний: {full_city_from_name} → {full_city_to_name}, месяц {key.title()}",
            reply_markup=keyboard
        )


def register_message(dp: Dispatcher):
    dp.message.register(start_command, CommandStart())
    dp.message.register(help_command, Command('help'))
    dp.message.register(air_from_handler, Command("air"))
    dp.message.register(air_to_handler, User.air_from)
    dp.message.register(month_handler, User.air_to)
    dp.message.register(day_handler, User.month)
    dp.message.register(vivod_handler, User.day)

    dp.message.register(repeat_order, Command("repeat"))

    dp.message.register(statistics, Command("stats"))
    dp.message.register(stat_per_company, Command("stats_per_company"))
    dp.message.register(stats_per_day, Command("stats_per_day"))
    dp.message.register(stat_air_to_handler, User.per_day_air_from)
    dp.message.register(data_stats, User.per_day_air_to)
    dp.message.register(stats_per_day_magic, User.per_day_date)

    dp.message.register(per_company_air_to_handler, User.per_company_air_from)
    dp.message.register(per_company_data_stats, User.per_company_air_to)
    #dp.message.register(state_handler, User.number)
