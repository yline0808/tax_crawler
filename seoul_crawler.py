import time
import selenium
import pymysql
import simplejson
import sys

# from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def seoul_crawler(year, month):
    print(year, month)

    json_data = open('./config.json').read()
    json = simplejson.loads(json_data)

    host = json["database"]["host"]
    port = json["database"]["port"]
    user = json["database"]["user"]
    password = json["database"]["password"]
    db = json["database"]["db"]
    
    conn = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8')
    cursor = conn.cursor()
    print('db connection success!!!')

    # cursor.execute(sql) 
    # conn.commit() 
    # conn.close() 

    sleep_time = 10
    start_time = time.ctime()

    try:
        # display = Display(visible=0, size=(800, 800))
        # display.start()

        options = Options()

        prefs = {
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_setting_values.popups': 2,
            'profile.default_content_settings.state.flash': 0,
            'profile.managed_default_content_settings.images': 2,
            'download.prompt_for_download': False
        }

        options.add_experimental_option("prefs", prefs)
        # options.binary_location = '/opt/google/chrome/google-chrome'
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-infobars')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--disable-popup-blocking')
        # options.add_argument('--kiosk')
        options.add_argument('--start-maximized')
        # options.add_argument('--user-data-dir=' + CHROME_PROFILE)
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36")

        CHROME_PATH = './driver/chromedriver.exe'
        driver = webdriver.Chrome(executable_path=CHROME_PATH, chrome_options=options)


        crawling_date = int(time.time())

        url = json["url"]["seoul"]
        driver.get(url)

        time.sleep(3)
        
        totalUrl = []
        dept1NameList = []
        dept2NameList = []
        dept3NameList = []
        dept4NameList = []

        # check year and month
        isYearExist = False
        isMonthExixt = False

        yearElements = driver.find_elements(By.CSS_SELECTOR, 'select#select-year > option')
        for yearElement in yearElements:
            if year == int(yearElement.get_attribute('textContent')):
                print(year)

        # ==========department1 crawler===========
        dept1Element = driver.find_element(By.CSS_SELECTOR, 'select#dept1')

        for dept1Option in dept1Element.find_elements(By.CSS_SELECTOR, 'option'):
            dept1NameList.append(dept1Option.get_attribute('textContent'))
            dept1Option.click()
            time.sleep(2)
            print('<1>', dept1Option.get_attribute('textContent'))

            isDept2Disabled = driver.find_element(By.CSS_SELECTOR, 'select#dept2').get_attribute('disabled')

            # driver.find_element(By.CSS_SELECTOR, 'select#select-year > option[value="{}"]'.format(year)).click()


            if isDept2Disabled == True:
                driver.find_element(By.CSS_SELECTOR, 'select#select-year > option[value="{}"]'.format(year)).click()

            dept2Element = driver.find_element(By.CSS_SELECTOR, 'select#dept2')

            for dept2Option in dept2Element.find_elements(By.CSS_SELECTOR, 'option'):
                dept2NameList.append(dept2Option.get_attribute('textContent'))
                dept2Option.click()
                time.sleep(2)
                print('<2>', dept2Option.get_attribute('textContent'))

                isDept3Disabled = driver.find_element(By.CSS_SELECTOR, 'select#dept3').get_attribute('disabled')

                if isDept3Disabled == True: break

                dept3Element = driver.find_element(By.CSS_SELECTOR, 'select#dept3')

                for dept3Option in dept3Element.find_elements(By.CSS_SELECTOR, 'option'):
                    dept3NameList.append(dept3Option.get_attribute('textContent'))
                    dept3Option.click()
                    time.sleep(2)
                    print('<3>', dept3Option.get_attribute('textContent'))

                    isDept4Disabled = driver.find_element(By.CSS_SELECTOR, 'select#dept4').get_attribute('disabled')

                    if isDept4Disabled == True: break

                    dept4Element = driver.find_element(By.CSS_SELECTOR, 'select#dept4')

                    for dept4Option in dept4Element.find_elements(By.CSS_SELECTOR, 'option'):
                        dept4NameList.append(dept4Option.get_attribute('textContent'))
                        dept4Option.click()
                        time.sleep(2)

                        print('<4>', dept4Option.get_attribute('textContent'))

    except Exception as e:
        print("==========error=========")
        print(e)



# seoul_crawler(sys.argv[1], sys.argv[2])
seoul_crawler(2019, 7)