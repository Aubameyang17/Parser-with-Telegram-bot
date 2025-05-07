import psycopg2
import matplotlib.pyplot as plt
import numpy as np
def plot_company_comparison(city_from, city_to):
    # Подключение к БД
    conn = psycopg2.connect(dbname="Aeroports", host="127.0.0.1", user="Alex", password="alex")
    cursor = conn.cursor()

    # Выполнение запроса
    query = """
    SELECT company, AVG(price) as avg_price, MIN(price) as min_price
    FROM all_flyghts
    WHERE city_from = %s AND city_to = %s
    GROUP BY company
    ORDER BY avg_price;
    """
    cursor.execute(query, (city_from, city_to))
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
    ax.set_title(f'Сравнение авиакомпаний по маршруту {city_from} → {city_to}')
    ax.set_xticks(x)
    ax.set_xticklabels(companies, rotation=45)
    ax.legend()
    ax.grid(axis='y')
    plt.tight_layout()
    plt.show()

    cursor.close()
    conn.close()

plot_company_comparison("MOW", "AER")