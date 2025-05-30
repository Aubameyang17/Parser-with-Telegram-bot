import asyncio
import time
import psycopg2
import datetime
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By

from sql_file import create_table, info_to_table, take_orders

year = datetime.date.today().year
month = datetime.date.today().month

month_to_number = {'январь': "01", 'февраль': "02", 'март': "03", 'апрель': "04", 'май': "05", 'июнь': "06",
                   'июль': "07", 'август': "08", 'сентябрь': "09", 'октябрь': "10", 'ноябрь': "11", 'декабрь': "12"}


async def osnovnoe(resultfrom, resultto, usermonth, userdate, cursor, conn, name):
    options_chrome = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options_chrome)

    try:
        url = f'https://www.aeroflot.ru/sb/app/ru-ru?utm_referrer=https%3A%2F%2Fwww.aeroflot.ru%2Fru-ru#/search?adults=1&cabin=economy&children=0&childrenaward=0&childrenfrgn=0&infants=0&routes={resultfrom}.{year}{month_to_number[usermonth]}{userdate}.{resultto}&_k=jc07st'

        driver.get(url)
        driver.delete_all_cookies()
        driver.refresh()
        await asyncio.sleep(10)
        elmtsint = driver.find_elements(By.TAG_NAME, "a")

        for el in elmtsint:
            if el.text == "Найти":
                el.click()

        await asyncio.sleep(10)
        polet = driver.find_elements(By.CLASS_NAME, "flight-search")

        for one in polet:
            real = one.find_element(By.CLASS_NAME, "flight-search__inner")
            ko = real.find_elements(By.TAG_NAME, 'div')
            mass = []
            for el in ko:
                mass.append(el.get_attribute('class'))

            try:
                simpind = mass.index("row flight-search__simple")
                priceind = mass.index("flight-search__price-text")

                tdfrom = ko[simpind].find_element(By.CLASS_NAME, "time-destination__from")
                tttime = tdfrom.find_element(By.CLASS_NAME, 'time-destination__time')
                time_from = tttime.text
                destair = tdfrom.find_element(By.CLASS_NAME, 'time-destination__airport')
                airfrom = destair.text
                compname = ko[simpind].find_element(By.CLASS_NAME, 'flight-search__company-name')
                compname = compname.text
                pricemass = ko[priceind].text.split()
                pricemass.pop()
                pricemass.pop(0)
                price = int("".join(pricemass))

                try:
                    leftind = mass.index("flight-search__left")
                    leftsit = ko[leftind].text
                except Exception as ex:
                    print("leftind")
                    #traceback.print_exc()
                    leftsit = ""

                try:
                    terminalen = tdfrom.find_element(By.CLASS_NAME, 'time-destination__terminal')
                    terminal = "Терминал - " + terminalen.text
                except Exception as ex:
                    print("terminal")
                    #traceback.print_exc()
                    terminal = ""

                tdto = ko[simpind].find_element(By.CLASS_NAME, "time-destination__to")
                timeto = tdto.find_element(By.CLASS_NAME, 'time-destination__time')
                timemass = timeto.text.split("\n")
                timeto = timemass[0]
                todestair = tdto.find_element(By.CLASS_NAME, 'time-destination__airport')
                airto = todestair.text

                try:
                    toterminalen = tdto.find_element(By.CLASS_NAME, 'time-destination__terminal')
                    toterminal = "Терминал - " + toterminalen.text
                except Exception as ex:
                    #traceback.print_exc()
                    print("toterminal")
                    toterminal = ""

                try:
                    plusday = tdto.find_element(By.CLASS_NAME, 'time-destination__plusday')
                    plusday = plusday.text
                except Exception as ex:
                    #traceback.print_exc()
                    print("plusday")
                    plusday = ""
                info_to_table(name, time_from, airfrom, terminal, timeto, plusday, airto, toterminal, compname, price, leftsit, cursor, conn)
            except Exception as ex:
                print("row fligtht first")
                #traceback.print_exc()


    except Exception as ex:
        traceback.print_exc()
        print("osnovnoe")
        print("Рейсы не найдены")

    finally:
        driver.quit()  # Закрываем браузер



