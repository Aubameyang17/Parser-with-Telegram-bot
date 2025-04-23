import asyncio
import datetime
import time

import psycopg2

conn = psycopg2.connect(dbname="Aeroports", host="127.0.0.1", user="Alex", password="alex")
cursor = conn.cursor()
month_to_number = {'Январь': "01", 'Февраль': "02", 'Март': "03", 'Апрель': "04", 'Май': "05", 'Июнь': "06",
                   'Июль': "07", 'Август': "08", 'Сентябрь': "09", 'Октябрь': "10", 'Ноябрь': "11", 'Декабрь': "12"}

async def fun1(x):
    pass
    """for i in range(0, 10):
        try:
            if i % 3 == 0:
                raise Exception()
            print(i, " continue")
        except Exception:
            continue
"""



async def fun2(x):
    month = "Февраль"
    if int(month_to_number[month]) < datetime.date.today().month:
        print(int(month_to_number[month]), datetime.date.today().month)


async def main():
    task1 = asyncio.create_task(fun1(4))
    task2 = asyncio.create_task(fun2(4))

    await task1
    await task2


print(time.strftime('%X'))

asyncio.run(main())

print(time.strftime('%X'))