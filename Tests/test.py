import datetime
import time
import traceback
import os
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

options_chrome = webdriver.ChromeOptions()
#options_chrome.add_argument("--incognito")
# options.add_argument("--headless")
#options_chrome.add_experimental_option("excludeSwitches", ["enable-automation"])
#options_chrome.add_experimental_option('useAutomationExtension', False)
options_chrome.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=options_chrome)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    'source': '''
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
  '''
})

conn = psycopg2.connect(dbname="Aeroports", host="127.0.0.1", user="Alex", password="alex")
cursor = conn.cursor()
year = datetime.date.today().year
month = datetime.date.today().month
month_to_number = {'Январь': "01", 'Февраль': "02", 'Март': "03", 'Апрель': "04", 'Май': "05", 'Июнь': "06",
                   'Июль': "07", 'Август': "08", 'Сентябрь': "09", 'Октябрь': "10", 'Ноябрь': "11", 'Декабрь': "12"}
nechet = ['Январь', 'Март', 'Май', 'Июль', 'Август', 'Октябрь', 'Декабрь']
chet = ['Апрель', 'Июнь', 'Сентябрь', 'Ноябрь']

def take_info():
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
    return resultfrom, resultto, usermonth, userdate

def pobeda():
    try:
        #air_from, air_to, usermonth, userdate = take_info()
        url1 = f"https://book.uralairlines.ru/?model=%7B%22departureDate%22%3A%222025-03-25T00%3A00%3A00%22," \
              f"%22returnDate%22%3Anull,%22departureLocation%22%3A%22SVX%22,%22arrivalLocation%22%3A%22MOW%22," \
              f"%22displayType%22%3A2,%22tripType%22%3A%22O%22,%22promo%22%3Anull,%22passengers%22%3A%5B%7B%22" \
              f"passengerNum%22%3A1,%22type%22%3A%22adult%22,%22hasInfant%22%3Afalse,%22isSubsidizedType%22%3Afalse," \
              f"%22isSubsidizedFedType%22%3Afalse,%22isPreferentialFedType%22%3Afalse,%22isDisabledSubsidizedType%22" \
              f"%3Afalse,%22isKaliningradSubsidizedType%22%3Afalse,%22isFarEastSubsidizedType%22%3Afalse," \
              f"%22isAgeSubsidizedType%22%3Afalse,%22canHavePrivileges%22%3Afalse%7D%5D,%22sessionMarker%22%3Anull," \
              f"%22isPrivileges%22%3Afalse,%22flights%22%3A%5B%5D,%22subsidyType%22%3Anull,%22language%22%3A%22RU%22," \
              f"%22metaSearchEngine%22%3Anull,%22currency%22%3A%22RUB%22,%22operation%22%3A%22booking%22,%22error%22" \
              f"%3Anull,%22validationFieldsErrors%22%3Anull,%22isInvalid%22%3Afalse,%22certificateNumber%22%3Anull," \
              f"%22certificateSurname%22%3Anull,%22login%22%3Anull,%22token%22%3Anull%7D"
        url = "https://www.aviasales.ru/search/LED0204SVX1"
        driver.get(url)
        driver.delete_all_cookies()
        driver.refresh()
        time.sleep(10)
        sr = driver.find_element(By.CLASS_NAME, "app__content")
        btn = sr.find_elements(By.TAG_NAME, "button")
        for el in btn:
            if el.text == "Показать ещё билеты":
                print("ok")
                el.click()
        time.sleep(10)
        #print(sr.text)
        """table = driver.find_element(By.CLASS_NAME, "flights-list")
        div = table.find_elements(By.TAG_NAME, 'div')
        for k in div:
            if k.get_attribute('class') == "flight selected" or k.get_attribute('class') == "flight":
                print(k.get_attribute('class'))
                print(k.text)
                break"""



        time.sleep(10)

    except Exception as ex:
        traceback.print_exc()
        print("Рейсы не найдены")

    finally:
        driver.quit()  # Закрываем браузер

pobeda()