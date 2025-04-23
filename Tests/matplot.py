import matplotlib.pyplot as plt
import psycopg2

conn = psycopg2.connect(dbname="Aeroports", host="127.0.0.1", user="Alex", password="alex")
cursor = conn.cursor()

cursor.execute('SELECT time_from FROM public."867265812flyghts" where name = \'Аэрофлот\' ORDER BY time_from ASC ')
time = cursor.fetchall()
time_mass = []
for el in time:
    time_mass.append(el[0])
cursor.execute('SELECT price FROM public."867265812flyghts" where name = \'Аэрофлот\' ORDER BY time_from ASC ')
price = cursor.fetchall()
price_mass = []
for el in price:
    price_mass.append(el[0])

print(time_mass)
print(price_mass)
days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
sales = [100, 150, 200, 130, 180]
plt.plot(time_mass, price_mass)
plt.title("all sales")
plt.xlabel("day")
plt.ylabel("sales")
plt.show()