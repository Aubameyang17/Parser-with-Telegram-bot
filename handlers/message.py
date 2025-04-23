import traceback

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
import asyncio
import datetime
import psycopg2
from aiogram.fsm.context import FSMContext

from pobedaparser import pobeda
from aeroflot_Parser import osnovnoe
from keyboards.keyboards import user_menu
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



async def add_user(user_id, username):
    cursor.execute(f"select * from telegramusers where user_id = {user_id};")
    chek_user = cursor.fetchone()
    if chek_user is None:
        cursor.execute(f"INSERT INTO telegramusers (user_id, username) VALUES ({user_id}, '{username}')")
        conn.commit()


async def start_command(message: types.Message):
    await add_user(message.from_user.id, message.from_user.username)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text='/start'), types.KeyboardButton(text='/air')]
    ])
    await message.answer(f'Добрый день, {message.from_user.full_name}\n'
                         f'Рад вас видеть, напишите /air, чтобы начать искать билеты', reply_markup=kb)

async def air_from_handler(message: types.Message, state: FSMContext):
    await message.answer("Откуда полетим?")
    await state.set_state(User.air_from.state)


async def air_to_handler(message: types.Message, state: FSMContext):
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
    await message.answer("Введите город в который хотите полететь")
    await state.set_state(User.air_to.state)


async def month_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cursor.execute(f"SELECT code FROM aero WHERE lower(city) LIKE %s;", (message.text.lower(),))
    resultto = cursor.fetchall()
    if resultto:
        resultto = resultto[0][0]
        newres = resultto.split(",")
        resultto = newres[0]
        if resultto == user_data['air_from']:
            await message.answer("Вы хотите полетать по городу? Могу посоветовать не повторять 11 сентября и сменить город назначения")
            return
    else:
        await message.answer("Такого города не существует, попробуйте еще раз")
        return
    await state.update_data(air_to=resultto)
    await state.set_state(User.month.state)
    await message.answer("Выберите месяц для перелета")

async def day_handler(message: types.Message, state: FSMContext):
    if message.text.lower() in month_to_number.keys():
        if int(month_to_number[message.text.lower()]) < month:
            await message.answer(
                "Такой месяц уже прошел, если вы хотите посмотреть билеты на следующий год дождитесь обновлений бота")
            return
    else:
        await message.answer("Такого месяца не существует, попробуйте еще раз")
        return
    await state.update_data(month=message.text.lower())
    await message.answer("На какое число смотреть билеты? ")
    await state.set_state(User.day.state)


async def vivod_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    try:
        userdate = int(message.text)
    except Exception:
        await message.answer("Это не число")
        return
    if int(month_to_number[user_data['month']]) == month and userdate < day:
        await message.answer("Этот день уже прошел, если вы хотите посмотреть билеты на следующий год дождитесь обновлений бота")
        return
    elif user_data['month'] in chet and int(userdate) in range(1, 31):
        pass
    elif user_data['month'] in nechet and int(userdate) in range(1, 32):
        pass
    elif user_data['month'] == 'Февраль' and int(year) % 4 == 0 and int(userdate) in range(1, 30):
        pass
    elif user_data['month'] == 'Февраль' and int(year) % 4 != 0 and int(userdate) in range(1, 29):
        pass
    else:
        await message.answer("Такой даты нет в выбраном месяце")
        return
    await message.answer(f"Откуда {user_data['air_from']} куда {user_data['air_to']} месяц {user_data['month']} день {userdate}")
    name = create_table(str(message.from_user.id), cursor, conn)
    osnova = asyncio.create_task(osnovnoe(user_data['air_from'], user_data['air_to'], user_data['month'], userdate, cursor, conn, name))
    pobedna = asyncio.create_task(pobeda(user_data['air_from'], user_data['air_to'], user_data['month'], userdate, cursor, conn, name))
    await osnova
    await pobedna
    userid = message.from_user.id
    name = '"' + str(userid) + "flyghts" + '"'
    cursor.execute('SELECT * FROM ' + name + ' ORDER BY price asc')
    result = cursor.fetchall()
    if result:
        stroka = "Вот три самых дешевых предложения, если хотите увидеть все варианты напишите /all:\n\n"
        count = 0
        for el in result:
            try:
                if count > 2:
                    raise Exception()
            except Exception:
                continue
            time_from = el[1]
            airfrom = el[2]
            cursor.execute(f"SELECT city FROM aero WHERE code LIKE '%{airfrom}%'")
            city_from = cursor.fetchone()
            city_from = city_from[0]
            terminal = el[3]
            timeto = el[4]
            plusday = el[5]
            airto = el[6]
            cursor.execute(f"SELECT city FROM aero WHERE code LIKE '%{airto}%'")
            city_to = cursor.fetchone()
            city_to = city_to[0]
            toterminal = el[7]
            compname = el[8]
            price = el[9]
            leftsit = el[10]
            podstroka = f"*{compname}*\n{city_from}({airfrom}) - {city_to}({airto}) \n <b>Вылет</b> {userdate} {user_data['month']} | {time_from} - {timeto} {plusday}\n<i>Цена:</i> *{price}*\n{leftsit}"
            #podstroka = f"<b>Вылет</b> в {time_from} из г.{city_from}({airfrom}) {terminal}\nПрилет в {timeto} {plusday} в г.{city_to}({airto}) {toterminal}\n{compname} от {price} {leftsit}\n\n"
            stroka += podstroka
            count += 1
        await message.answer(stroka, parse_mode=ParseMode.HTML)
    else:
        await message.answer("Рейсы не найдены, попробуйте другие даты\n"
                             "Также в боте могла произойти ошибка, попробуйте написать свой запрос еще раз")

    try:
        take_orders(name, userid, user_data['air_from'], user_data['air_to'], user_data['month'], userdate, cursor, conn)
    except Exception:
        traceback.print_exc()
        print("take orders")

async def show_all_flights(message: types.Message):
    name = '"' + str(message.from_user.id) + "flyghts" + '"'
    cursor.execute('SELECT * FROM ' + name + ' ORDER BY price asc')
    result = cursor.fetchall()
    if result:
        stroka = "Вот все предложения по вашему запросу:\n\n"
        for el in result:
            time_from = el[1]
            airfrom = el[2]
            cursor.execute(f"SELECT city FROM aero WHERE code LIKE '%{airfrom}%'")
            city_from = cursor.fetchone()
            city_from = city_from[0]
            terminal = el[3]
            timeto = el[4]
            plusday = el[5]
            airto = el[6]
            cursor.execute(f"SELECT city FROM aero WHERE code LIKE '%{airto}%'")
            city_to = cursor.fetchone()
            city_to = city_to[0]
            toterminal = el[7]
            compname = el[8]
            price = el[9]
            leftsit = el[10]
            podstroka = f"Вылет в {time_from} из г.{city_from}({airfrom}) {terminal}\nПрилет в {timeto} {plusday} в г.{city_to}({airto}) {toterminal}\n{compname} от {price} {leftsit}\n\n"
            stroka += podstroka
        await message.answer(stroka)
    else:
        await message.answer("Рейсы не найдены, попробуйте другие даты\n"
                             "Также в боте могла произойти ошибка, попробуйте написать свой запрос еще раз")





def register_message(dp: Dispatcher):
    dp.message.register(start_command, CommandStart())
    dp.message.register(air_from_handler, Command("air"))
    dp.message.register(show_all_flights, Command("all"))
    dp.message.register(air_to_handler, User.air_from)
    dp.message.register(month_handler, User.air_to)
    dp.message.register(day_handler, User.month)
    dp.message.register(vivod_handler, User.day)
    #dp.message.register(state_handler, User.number)
