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
from datetime import datetime


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
        # ===============================config===================================


        # -------------------------------start------------------------------------
        driver = webdriver.Chrome(executable_path=CHROME_PATH, chrome_options=options)

        crawling_date = int(time.time())

        url = json["url"]["seoul"]
        driver.get(url)

        time.sleep(3)

        # check date
        isYearExist, isMonthExist = checkDate(driver, year, month)

        if(not isYearExist or not isMonthExist):
            print('year or month is not exist')
            sys.exit()

        # select department
        selectDept(conn, driver, year, month)

    except Exception as e:
        print("==========error=========")
        print(e)


# check year and month
def checkDate(driver, year, month):
    isYearExist = False
    isMonthExist = False

    yearElements = driver.find_elements(By.CSS_SELECTOR, 'select#select-year > option')
    for yearElement in yearElements:
        if year == int(yearElement.get_attribute('value')):
            isYearExist = True
            break
    
    monthElements = driver.find_elements(By.CSS_SELECTOR, 'select#select-month > option')
    for monthElement in monthElements:
        if month == int(monthElement.get_attribute('value')):
            isMonthExist = True
            break
    
    return isYearExist, isMonthExist


# select date function
def clickDate(driver, year, month):
    driver.find_element(By.CSS_SELECTOR, 'select#select-year > option[value="{}"]'.format(year)).click()
    driver.find_element(By.CSS_SELECTOR, 'select#select-month > option[value="{}"]'.format(month)).click()
    driver.find_element(By.CSS_SELECTOR, 'input.btn.btn-submit').click()
    time.sleep(1)


# crawling
def selectDept(conn, driver, year, month):
    totalUrl = []
    dept1NameList = []
    dept2NameList = []
    dept3NameList = []
    dept4NameList = []
    dept5NameList = []

    dept1Element = driver.find_element(By.CSS_SELECTOR, 'select#dept1')

    # classification step 1
    for dept1Option in dept1Element.find_elements(By.CSS_SELECTOR, 'option'):
        dept1NameList.append(dept1Option.get_attribute('textContent'))
        dept1Option.click()
        time.sleep(2)
        print('<1>', dept1Option.get_attribute('textContent'))

        dept2Element = driver.find_element(By.CSS_SELECTOR, 'select#dept2')

        if dept2Element.get_attribute('disabled') == 'true':
            deptList = [
                dept1Option.get_attribute('textContent'),
                None,
                None,
                None,
                None
            ]
            clickDate(driver, year, month)
            crawling_table(conn, driver, deptList)

        # classification step 2
        for dept2Option in dept2Element.find_elements(By.CSS_SELECTOR, 'option'):
            dept2NameList.append(dept2Option.get_attribute('textContent'))
            dept2Option.click()
            time.sleep(2)
            print('<2>', dept2Option.get_attribute('textContent'))

            dept3Element = driver.find_element(By.CSS_SELECTOR, 'select#dept3')

            if dept3Element.get_attribute('disabled') == 'true':
                deptList = [
                    dept1Option.get_attribute('textContent'),
                    dept2Option.get_attribute('textContent'),
                    None,
                    None,
                    None
                ]
                clickDate(driver, year, month)
                crawling_table(conn, driver, deptList)

            # classification step 3
            for dept3Option in dept3Element.find_elements(By.CSS_SELECTOR, 'option'):
                dept3NameList.append(dept3Option.get_attribute('textContent'))
                dept3Option.click()
                time.sleep(2)
                print('<3>', dept3Option.get_attribute('textContent'))

                dept4Element = driver.find_element(By.CSS_SELECTOR, 'select#dept4')

                if dept4Element.get_attribute('disabled') == 'true': 
                    deptList = [
                        dept1Option.get_attribute('textContent'),
                        dept2Option.get_attribute('textContent'),
                        dept3Option.get_attribute('textContent'),
                        None,
                        None
                    ]
                    clickDate(driver, year, month)
                    crawling_table(conn, driver, deptList)
                    
                # classification step 4
                for dept4Option in dept4Element.find_elements(By.CSS_SELECTOR, 'option'):
                    dept4NameList.append(dept4Option.get_attribute('textContent'))
                    dept4Option.click()
                    time.sleep(2)
                    print('<4>', dept4Option.get_attribute('textContent'))

                    dept5Element = driver.find_element(By.CSS_SELECTOR, 'select#dept5')

                    if dept5Element.get_attribute('disabled') == 'true':
                        deptList = [
                            dept1Option.get_attribute('textContent'),
                            dept2Option.get_attribute('textContent'),
                            dept3Option.get_attribute('textContent'),
                            dept4Option.get_attribute('textContent'),
                            None
                        ]
                        clickDate(dirver, year, month)
                        crawling_table(conn, driver, deptList)

                    # classification step 5
                    for dept5Option in dept5Element.find_elements(By.CSS_SELECTOR, 'option'):
                        dept5NameList.append(dept5Option.get_attribute('textContent'))
                        dept5Option.click()
                        time.sleep(2)
                        print('<5>', dept5Option.get_attribute('textContent'))

                        deptList = [
                            dept1Option.get_attribute('textContent'),
                            dept2Option.get_attribute('textContent'),
                            dept3Option.get_attribute('textContent'),
                            dept4Option.get_attribute('textContent'),
                            dept5Option.get_attribute('textContent'),
                        ]
                        clickDate(driver, year, month)
                        crawling_table(conn, driver, deptList)


def crawling_table(conn, driver, deptList):
    tableRows = driver.find_elements(By.CSS_SELECTOR, 'div#mCSB_1_container > table > tbody > tr')

    for tableRow in tableRows:
        # rowData = deptList.copy()
        rowData = [None, None, None, None, None]

        for tableItem in tableRow.find_elements(By.CSS_SELECTOR, 'td'):
            rowData.append(tableItem.get_attribute('textContent').strip())
        
        rowData.append(datetime.today().strftime("%Y/%m/%d %H:%M:%S"))

        data = {
            "dept1Id": None,
            "dept2Id": None,
            "dept3Id": None,
            "dept4Id": None,
            "dept5Id": None,
            "purpose": rowData[5],
            "department": rowData[6],
            "usedAt": rowData[7],
            "place": rowData[8],
            "usePurpose": rowData[9],
            "price": rowData[10],
            "user": rowData[11],
            "paymentMethod": rowData[12],
            "crawlDate": rowData[13],
        }

        print(data)
        insertTableDB(conn, data, rowData[:5])
        
    sys.exit()


def insertTableDB(conn, data, deptList):
    # query = 'insert into seoul (department1Id, department2Id, department3Id, department4Id, department5Id,'\
    #         'purpose, department, usedAt, place, usePurpose, price, user, paymentMethod, crawlDate)'\
    #         'values(`{}`, `{}`, `{}`, `{}`, `{}`, %s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(*list(map(lambda x: x if x else "NULL", deptList)))
    # values = (data['dept1Id'], data['dept2Id'], data['dept3Id'], data['dept4Id'], data['dept5Id'], 
    #         data['purpose'], data['department'], data['usedAt'], data['place'], data['usePurpose'], 
    #         data['price'], data['user'], data['paymentMethod'], data['crawlDate'])

    query = 'insert into seoul (purpose, department, usedAt, place, usePurpose, price, user, paymentMethod, crawlDate)'\
            'values(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
    values = (data['purpose'], data['department'], data['usedAt'], data['place'], data['usePurpose'], 
            data['price'], data['user'], data['paymentMethod'], data['crawlDate'])

    curs = conn.cursor()
    curs.execute(query, values)
    conn.commit()


# def insertDepartmentDB(parent_id=None, name):
#     print("")

# seoul_crawler(sys.argv[1], sys.argv[2])
seoul_crawler(2019, 6)