import time
import selenium
import pymysql
import simplejson

# from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def seoul_crawler():
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
        # ==========department1 crawler===========
        selectWidgetElementList = driver.find_elements(By.CSS_SELECTOR, 'div.views-exposed-widgets.clearfix > select.select-dept');

        for selDept in selectWidgetElementList:
            if selDept.get_attribute('disabled') == None:
                break


        dept1ElementList = driver.find_elements(By.CSS_SELECTOR, '#dept1 > option')



        dept1TxtList = []
        
        for dept1Element in dept1ElementList:
            dept1List.append(dept1Element.get_attribute('textContent'))
            
        
        for i in dept1List:
            print(i)

    except Exception as e:
        print("==========error=========")
        print(e)


seoul_crawler()