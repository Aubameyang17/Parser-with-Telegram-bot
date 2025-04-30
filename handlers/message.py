import traceback
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
import asyncio
import datetime
import psycopg2
from aiogram.fsm.context import FSMContext
from pobedaparser import pobeda
from aeroflot_Parser import osnovnoe
from UrAirparser import uralair
from smartaviaparser import smartavia
from keyboards.keyboards import user_menu, create_city_keyboard
from sql_file import create_table, take_orders
from states.state import User

month_to_number = {'январь': "01", 'февраль': "02", 'март': "03", 'апрель': "04", 'май': "05", 'июнь': "06",
                   'июль': "07", 'август': "08", 'сентябрь': "09", 'октябрь': "10", 'ноябрь': "11", 'декабрь': "12"}
nechet = ['январь', 'март', 'май', 'июль', 'август', 'октябрь', 'декабрь']
chet = ['апрель', 'июнь', 'сентябрь', 'ноябрь']
year = datetime.date.today().year
month = datetime.date.today().month
day = datetime.date.today().day

def get_db_cursor():
    conn = psycopg2.connect(
        bname="Aeroports", host="127.0.0.1", user="Alex", password="alex"
    )
    return conn, conn.cursor()


async def run_all_parsers_parallel(resultfrom, resultto, usermonth, userdate, cursor, conn, name, year):
    results = await asyncio.gather(
        osnovnoe(resultfrom, resultto, usermonth, userdate, cursor, conn, name, year),
        pobeda(resultfrom, resultto, usermonth, userdate, cursor, conn, name, year),
        uralair(resultfrom, resultto, usermonth, userdate, cursor, conn, name, year),
        smartavia(resultfrom, resultto, usermonth, userdate, cursor, conn, name, year)
    )
    return results

def get_popular_cities_from(limit=4):
    conn, cursor = get_db_cursor()
    try:
        cursor.execute("SELECT airfrom FROM orders GROUP BY airfrom ORDER BY COUNT(*) DESC LIMIT %s", (limit,))
        result = cursor.fetchall()
        mass = []
        for i in range(len(result)):
            mass.append(result[i][0])
        cities = []
        for el in mass:
            cursor.execute("SELECT city FROM aero WHERE code LIKE %s", (f"%{el}%",))
            cities.append(cursor.fetchone()[0])
        return cities
    finally:
        cursor.close()
        conn.close()

def get_popular_cities_to(limit=4):
    conn, cursor = get_db_cursor()
    try:
        cursor.execute("SELECT airto FROM orders GROUP BY airto ORDER BY COUNT(*) DESC LIMIT %s", (limit,))
        result = cursor.fetchall()
        mass = []
        for i in range(len(result)):
            mass.append(result[i][0])
        cities = []
        for el in mass:
            cursor.execute("SELECT city FROM aero WHERE code LIKE %s", (f"%{el}%",))
            cities.append(cursor.fetchone()[0])
        return cities
    finally:
        cursor.close()
        conn.close()


async def add_user(user_id, username):
    conn, cursor = get_db_cursor()
    try:
        cursor.execute(f"select * from telegramusers where user_id = {user_id};")
        chek_user = cursor.fetchone()
        if chek_user is None:
            cursor.execute(f"INSERT INTO telegramusers (user_id, username) VALUES ({user_id}, '{username}')")
            conn.commit()
    finally:
        cursor.close()
        conn.close()


async def start_command(message: types.Message):
    await add_user(message.from_user.id, message.from_user.username)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text='/start'), types.KeyboardButton(text='/air'), types.KeyboardButton(text='/repeat')]
    ])
    await message.answer(f'Добрый день, {message.from_user.full_name} 😉\n'
                         f'Рад вас видеть, напишите /air, чтобы начать искать билеты '
                         f'или /repeat чтобы повторить предыдущий запрос', reply_markup=kb)

async def air_from_handler(message: types.Message, state: FSMContext):
    conn, cursor = get_db_cursor()
    try:
        popular_citys = get_popular_cities_from(cursor)
        keyboard = create_city_keyboard(popular_citys, direction="from")
        await message.answer("🛫 Откуда полетим?", reply_markup=keyboard)
        await state.set_state(User.air_from.state)
    finally:
        cursor.close()
        conn.close()


async def air_to_handler(message: types.Message, state: FSMContext):
    conn, cursor = get_db_cursor()
    try:
        cursor.execute(f"SELECT code FROM aero WHERE LOWER(city) LIKE %s;", (message.text.lower(),))
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
        popular_citys = get_popular_cities_to(cursor)
        keyboard = create_city_keyboard(popular_citys, direction="to")
        await message.answer("🛬 Введите город в который хотите полететь", reply_markup=keyboard)
        await state.set_state(User.air_to.state)
    finally:
        cursor.close()
        conn.close()


async def month_handler(message: types.Message, state: FSMContext):
    conn, cursor = get_db_cursor()
    try:
        user_data = await state.get_data()
        cursor.execute(f"SELECT code FROM aero WHERE lower(city) LIKE %s;", (message.text.lower(),))
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
    finally:
        cursor.close()
        conn.close()

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


async def vivod_handler(message: types.Message, state: FSMContext):
    conn, cursor = get_db_cursor()
    try:
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
        resultt = await run_all_parsers_parallel(user_data['air_from'], user_data['air_to'],
                                                 user_data['month'], userdate, cursor, conn, name, newyear)
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
    finally:
        cursor.close()
        conn.close()


async def show_page(message: types.Message, flights, page, user_data):
    conn, cursor = get_db_cursor()
    try:
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
    finally:
        cursor.close()
        conn.close()


async def repeat_order(message: types.Message, state: FSMContext):
    conn, cursor = get_db_cursor()
    try:
        newyear = year
        cursor.execute(f"SELECT airfrom from orders WHERE id_user = {message.from_user.id} ORDER BY id desc")
        airfrom_table = cursor.fetchone()[0]
        cursor.execute(f"SELECT airto from orders WHERE id_user = {message.from_user.id} ORDER BY id desc")
        airto_table = cursor.fetchone()[0]
        cursor.execute(f"SELECT month from orders WHERE id_user = {message.from_user.id} ORDER BY id desc")
        month_table = cursor.fetchone()[0]
        cursor.execute(f"SELECT userdate from orders WHERE id_user = {message.from_user.id} ORDER BY id desc")
        day_table = cursor.fetchone()[0]
        if int(month_to_number[month_table]) == month and day_table < day or int(month_to_number[month_table]) < month:
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
    finally:
        cursor.close()
        conn.close()


def register_message(dp: Dispatcher):
    dp.message.register(start_command, CommandStart())
    dp.message.register(air_from_handler, Command("air"))
    dp.message.register(repeat_order, Command("repeat"))
    dp.message.register(air_to_handler, User.air_from)
    dp.message.register(month_handler, User.air_to)
    dp.message.register(day_handler, User.month)
    dp.message.register(vivod_handler, User.day)
    #dp.message.register(state_handler, User.number)
