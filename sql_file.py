def info_to_table(name, time_from, airfrom, timeto, plusday, airto, compname, price, leftsit, cursor, conn):
    parametrs = (time_from, airfrom, timeto, plusday, airto, compname, price, leftsit)
    cursor.execute('INSERT INTO ' + name + ' (time_from, airfrom, time_to, plusday, airto, name, price, left_sit) '
                                           'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', parametrs)
    conn.commit()


def take_orders(name, userid, airfrom, airto, usermonth, userdate, cursor, conn):
    cursor.execute('SELECT price FROM ' + name + ' ORDER BY price asc')
    pricet = cursor.fetchone()
    price = pricet[0]
    parametrs = userid, airfrom, airto, usermonth, price, userdate
    cursor.execute('INSERT INTO orders (id_user, airfrom, airto, month, lowprice, userdate) '
                   'VALUES (%s, %s, %s, %s, %s, %s)', parametrs)
    conn.commit()


def create_table(userid, cursor, conn):
    name = '"' + userid + "flyghts" + '"'
    kostil = "'" + userid + "flyghts" + "'"
    cursor.execute(f"select * from pg_tables where tablename = {kostil}")
    res = cursor.fetchall()
    if res:
        cursor.execute(f"TRUNCATE TABLE {name}")
    else:
        cursor.execute("CREATE TABLE if not exists " + name + " (id SERIAL PRIMARY KEY, time_from VARCHAR(50),  "
                   "airfrom VARCHAR(50), time_to VARCHAR(50), plusday VARCHAR(50), "
                   "airto VARCHAR(50), name VARCHAR(50), price integer, "
                   "left_sit VARCHAR(50), date date default current_date)")

    conn.commit()
    return name


"""def take_info():
    userfrom = input("Откуда полетим? ")
    cursor.execute(f"SELECT code FROM aero WHERE lower(city) LIKE %s;", (userfrom.lower(),))
    resultfrom = cursor.fetchall()
    if resultfrom:
        resultfrom = resultfrom[0][0]
    else:
        print("Такого города не существует, попробуйте еще раз")
        return take_info()
    userto = input("Введите город в который хотите полететь: ")
    cursor.execute(f"SELECT * FROM aero WHERE city LIKE %s;", (userto,))
    resultto = cursor.fetchall()
    if resultto:
        resultto = resultto[0][0]
    else:
        print("Такого города не существует, попробуйте еще раз")
        return take_info()
    usermonth = input("Выберите месяц для перелета: ")
    if usermonth in month_to_number.keys():
        pass
    else:
        print("Такого месяца не существует, попробуйте еще раз")
        return take_info()
    userdate = input("На какое число смотреть билеты? ")
    if usermonth in chet and int(userdate) in range(1, 31):
        pass
    elif usermonth in nechet and int(userdate) in range(1, 32):
        pass
    elif usermonth == 'Февраль' and int(year) % 4 == 0 and int(userdate) in range(1, 30):
        pass
    elif usermonth == 'Февраль' and int(year) % 4 != 0 and int(userdate) in range(1, 29):
        pass
    else:
        print("Такой даты нет в выбраном месяце")
        return take_info()
    return resultfrom, resultto, usermonth, userdate"""