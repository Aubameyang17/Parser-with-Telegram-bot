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