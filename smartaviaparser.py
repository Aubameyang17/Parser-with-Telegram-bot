import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from sql_file import info_to_table

month_to_number = {'январь': "01", 'февраль': "02", 'март': "03", 'апрель': "04", 'май': "05", 'июнь': "06",
                   'июль': "07", 'август': "08", 'сентябрь': "09", 'октябрь': "10", 'ноябрь': "11", 'декабрь': "12"}

async def smartavia(resultfrom, resultto, usermonth, userdate, cursor, conn, name, year):
    options_chrome = webdriver.ChromeOptions()
    #options_chrome.add_argument("--headless")
    #options_chrome.add_argument('--no-sandbox')
    options_chrome.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options_chrome)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            'source': '''
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
          '''
    })
    try:
        url = f"https://flysmartavia.com/search/{resultfrom}-{userdate}{month_to_number[usermonth]}-{resultto}-1"
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        driver.delete_all_cookies()
        driver.refresh()
        driver.add_cookie({"name": "L", "value": "eRFWSAh0Y3AJB1p2a1YJc2IFc3hGRFN+IgE0KBdXKCU5KFUK.1727100950.15897.341115.799d39c8bea359755a1b586f88758cb7"})
        driver.add_cookie({"name": "Session_id", "value": "3:1741809678.5.0.1727100950874:-uXuWw:35ba.1.2:1|1193153127.0.2.3:1727100950|3:10304369.100727.h7-o4P3Cv6g-L_Y_kpld3Eny03A"})
        driver.add_cookie({"name": "_ga", "value": "GA1.1.2141062939.1735221878"})
        driver.add_cookie({"name": "_ga_EDLXJW5FQY", "value": "GS1.1.1741860884.3.0.1741860884.60.0.0"})
        driver.add_cookie({"name": "_yasc", "value": "6yz7nPGwmEEKmouQNrTAH6iT4bSv0IBRmQKvA9FU0yJkBeN0d3a02KntA62T84x4iDQscasEQWYkhm7JLTDhUEfD3jSVt5ip8Q=="})
        driver.add_cookie({"name": "_yasc", "value": "Dcy1LF+AuI4iFiYNYhHaEqFgCbL/MpjFTN5VdTLCuJHmIQNdNhgx32fsny3gClQC51IS"})
        driver.add_cookie({"name": "_ym_d", "value": "1738327182"})
        driver.add_cookie({"name": "avia_ab", "value": "strikethrough_price_svcs_add%3Ddisabled%3Bstrikethrough_price_svcs_main%3Denabled"})
        driver.add_cookie({"name": "bh", "value": "Ek8iTm90IEEoQnJhbmQiO3Y9IjgiLCAiQ2hyb21pdW0iO3Y9IjEzMiIsICJZYUJyb3dzZXIiO3Y9IjI1LjIiLCAiWW93c2VyIjt2PSIyLjUiGgUieDg2IioCPzA6CSJXaW5kb3dzIkIIIjE5LjAuMCJKBCI2NCJSZiJOb3QgQShCcmFuZCI7dj0iOC4wLjAuMCIsICJDaHJvbWl1bSI7dj0iMTMyLjAuNjgzNC44MzQiLCAiWWFCcm93c2VyIjt2PSIyNS4yLjIuODM0IiwgIllvd3NlciI7dj0iMi41IloCPzBg+vjKvgZqIdzK4f8IktihsQOfz+HqA/v68OcN6//99g+h6J+UD/OBAg=="})
        #able = driver.find_elements(By.CLASS_NAME, "js-variant-card-wrapper")
        table = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "js-variant-card-wrapper")))
        for el in table:
            fin = el.find_elements(By.CLASS_NAME, "inner")
            tin = el.find_elements(By.CLASS_NAME, "name")
            time_from = fin[0].find_element(By.CLASS_NAME, 'time').text
            #print(time_from + " - " + time_to + plusday)
            air_from = tin[0].text
            time_to = fin[1].find_element(By.CLASS_NAME, 'time').text
            # print(time_from + " - " + time_to + plusday)
            air_to = tin[1].text
            if air_to != resultto:
                pass
            else:
                pricemass = el.find_element(By.CSS_SELECTOR, '.price.nowrap').text
                price = pricemass.split()
                price.pop()
                price = int("".join(price))
                terminal = ""
                compname = "Smartavia"
                leftsit = ""
                plusday = ''
                info_to_table(name, time_from, air_from, time_to, plusday, air_to, compname, price, leftsit, cursor, conn)


    except Exception as ex:
        traceback.print_exc()
        print("Рейсы не найдены")

    finally:
        driver.quit()  # Закрываем браузер

