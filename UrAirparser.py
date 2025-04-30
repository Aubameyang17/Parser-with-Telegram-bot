import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import json
import urllib.parse
from datetime import date

from sql_file import info_to_table

options_chrome = webdriver.ChromeOptions()
month_to_number = {'январь': "01", 'февраль': "02", 'март': "03", 'апрель': "04", 'май': "05", 'июнь': "06",
                   'июль': "07", 'август': "08", 'сентябрь': "09", 'октябрь': "10", 'ноябрь': "11", 'декабрь': "12"}
#options_chrome.add_argument("--incognito")
# options.add_argument("--headless")
#options_chrome.add_experimental_option("excludeSwitches", ["enable-automation"])
#options_chrome.add_experimental_option('useAutomationExtension', False)
options_chrome.add_argument("--disable-blink-features=AutomationControlled")

def generate_ural_url(departure_code: str, arrival_code: str, departure_date: date, passengers: int = 1) -> str:
    base_url = "https://book.uralairlines.ru/?model="
    model = {
        "departureDate": departure_date.strftime("%Y-%m-%dT00:00:00"),
        "departureLocation": departure_code,
        "arrivalLocation": arrival_code,
        "tripType": "O",  # One-way
        "passengers": [{"passengerNum": passengers, "type": "adult"}],
        "language": "RU",
        "currency": "RUB",
        "operation": "booking"
    }
    encoded_model = urllib.parse.quote(json.dumps(model, ensure_ascii=False))
    full_url = base_url + encoded_model

    return full_url



async def uralair(resultfrom, resultto, usermonth, userdate, cursor, conn, name, year):
    driver = webdriver.Chrome(options=options_chrome)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
      '''
    })
    try:
        url = generate_ural_url(
            departure_code=resultfrom,
            arrival_code=resultto,
            departure_date=date(year, int(month_to_number[usermonth]), int(userdate))
        )
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "flight"))
        )

        flights = driver.find_elements(By.CLASS_NAME, "flight")

        for flight in flights:
            route = flight.find_elements(By.CLASS_NAME, "airport-code")
            air_city = route[0].text
            air_from = air_city.split()[1]

            air_to_city = route[1].text
            air_to = air_to_city.split()[1]

            times = flight.find_elements(By.CLASS_NAME, "time")
            time_from = times[0].text
            time_to = times[1].text

            pricemass = flight.find_element(By.CSS_SELECTOR, ".col.price").text
            price = pricemass.split()
            price.pop()
            price.pop(0)
            price = int("".join(price))
            plusday = ''
            leftsit = ''
            compname = "Уральские Авиалинии"
            info_to_table(name, time_from, air_from, time_to, plusday, air_to, compname, price, leftsit, cursor, conn)

    except Exception as ex:
        traceback.print_exc()
        print("Рейсы не найдены")

    finally:
        driver.quit()  # Закрываем браузер
