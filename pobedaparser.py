import asyncio

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import datetime
import traceback
from sql_file import info_to_table

month = datetime.date.today().month

month_to_number = {'январь': "01", 'февраль': "02", 'март': "03", 'апрель': "04", 'май': "05", 'июнь': "06",
                   'июль': "07", 'август': "08", 'сентябрь': "09", 'октябрь': "10", 'ноябрь': "11", 'декабрь': "12"}

async def pobeda(resultfrom, resultto, usermonth, userdate, cursor, conn, name, year):
    options_chrome = webdriver.ChromeOptions()
    driverpobeda = webdriver.Chrome(options=options_chrome)

    try:
        url = f"https://ticket.flypobeda.ru/websky/?origin-city-code%5B0%5D={resultfrom}&destination-city-code%5B0%5D={resultto}&date%5B0%5D={userdate}.{month_to_number[usermonth]}.{year}&segmentsCount=1&adultsCount=1&youngAdultsCount=0&childrenCount=0&infantsWithSeatCount=0&infantsWithoutSeatCount=0&lang=ru#/search"
        driverpobeda.get(url)
        wait = WebDriverWait(driverpobeda, 20)
        driverpobeda.delete_all_cookies()
        driverpobeda.refresh()
        table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "flightTable")))
        content = table.find_elements(By.CLASS_NAME, "contentRow")
        for el in content:
            peresadka = el.find_element(By.CLASS_NAME, "popup_js")
            try:
                if peresadka.text != "Прямой рейс":
                    raise Exception()
            except Exception:
                continue
            ttime = el.find_element(By.CLASS_NAME, 'time')
            time_from = ttime.text.split(" – ")[0]
            time_to = ttime.text.split(" – ")[1]
            time_mass = time_to.split()
            if len(time_mass) > 1:
                time_to = time_mass[0]
                plusday = time_mass[1]
            else:
                plusday = ""
            dest = el.find_element(By.CLASS_NAME, 'destinations__label')
            city_from_mass = dest.text.split(" – ")[0]
            city_from = city_from_mass.split()[0]
            city_to_mass = dest.text.split(" – ")[1]
            city_to = city_to_mass.split()[0]
            price = el.find_element(By.CLASS_NAME, 'price-cell__text')
            price = price.text.split()
            priceint = price.pop()
            priceint = int("".join(price))
            compname = "Победа"
            leftsit = ""
            info_to_table(name, time_from, resultfrom, time_to, plusday, resultto, compname,
                          priceint, leftsit, cursor, conn)

    except Exception as ex:
        traceback.print_exc()
        print("Рейсы не найдены")

    finally:
        driverpobeda.quit()  # Закрываем браузер