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

errorList = []
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

        # department
        totalDepartmentInfo = selectDept(conn, driver)
        print(len(totalDepartmentInfo))

        # totalDepartmentInfo = [
        #     [(1, '서울시본청', 1), (31, '서울특별시장', 1), None, None, None],
        #     [(1, '서울시본청', 1), (1, '서울시본청', 1), None, None, None],
        #     [(1, '서울시본청', 1), (2, '감사위원회', 1), (2, '감사담당관', 2), None, None]
        # ]
        # table
        crawlingTable(totalDepartmentInfo, year, month, driver, conn)

        print("==========error list=========")
        for err in errorList:
            print(err)

        conn.close()
        sys.exit()

    except Exception as e:
        print("==========error=========")
        print(e)


def crawlingTable(totalDepartmentInfo, year, month, driver, conn):
    for departmentsInfo in totalDepartmentInfo:
        print(departmentsInfo)
        deptList=[]
        for idx, departmentInfo in enumerate(departmentsInfo):
            if not departmentInfo:
                deptList.append(None)
                continue

            deptList.append(departmentInfo[0])
            optionStr = '//*[@id="dept{}"]/option[text()="{}"]'.format(idx+1, departmentInfo[1])

            driver.find_element(By.XPATH, optionStr).click()
            time.sleep(1.5)
        
        clickDate(driver, year, month)
        saveTable(conn, driver, deptList)


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
def selectDept(conn, driver):
    deptTimeSleep = 0.1
    totalDepartmentInfo = []
    dept0Name = 'seoul'

    dept0Info = saveTopDepartment(conn, dept0Name)
        
    time.sleep(deptTimeSleep)
    dept1Element = driver.find_element(By.CSS_SELECTOR, 'select#dept1')
    time.sleep(deptTimeSleep)

    # classification step 1
    for dept1Option in dept1Element.find_elements(By.CSS_SELECTOR, 'option'):

        dept1Option.click()
        dept1Info = saveDepartment(conn, dept1Option.get_attribute('textContent'), dept0Info[0], 'department1')
        time.sleep(deptTimeSleep)
        print('<1>', dept1Option.get_attribute('textContent'))

        dept2Element = driver.find_element(By.CSS_SELECTOR, 'select#dept2')

        if dept2Element.get_attribute('disabled') == 'true':
            deptList = [
                dept1Info,
                None,
                None,
                None,
                None
            ]
            
            totalDepartmentInfo.append(deptList)
            continue
            

        # classification step 2
        for dept2Option in dept2Element.find_elements(By.CSS_SELECTOR, 'option'):
            dept2Option.click()
            time.sleep(deptTimeSleep)
            dept2Info = saveDepartment(conn, dept2Option.get_attribute('textContent'), dept1Info[0], 'department2')
            print('<2>', dept2Option.get_attribute('textContent'))

            dept3Element = driver.find_element(By.CSS_SELECTOR, 'select#dept3')

            if dept3Element.get_attribute('disabled') == 'true':
                deptList = [
                    dept1Info,
                    dept2Info,
                    None,
                    None,
                    None,
                ]
                
                totalDepartmentInfo.append(deptList)
                continue

            # classification step 3
            for dept3Option in dept3Element.find_elements(By.CSS_SELECTOR, 'option'):
                dept3Option.click()
                time.sleep(deptTimeSleep)
                dept3Info = saveDepartment(conn, dept3Option.get_attribute('textContent'), dept2Info[0], 'department3')
                print('<3>', dept3Option.get_attribute('textContent'))

                dept4Element = driver.find_element(By.CSS_SELECTOR, 'select#dept4')

                if dept4Element.get_attribute('disabled') == 'true': 
                    deptList = [
                        dept1Info,
                        dept2Info,
                        dept3Info,
                        None,
                        None,
                    ]
                    
                    totalDepartmentInfo.append(deptList)
                    continue
                    
                # classification step 4
                for dept4Option in dept4Element.find_elements(By.CSS_SELECTOR, 'option'):
                    dept4Option.click()
                    time.sleep(deptTimeSleep)
                    dept4Info = saveDepartment(conn, dept4Option.get_attribute('textContent'), dept3Info[0], 'department4')
                    print('<4>', dept4Option.get_attribute('textContent'))

                    dept5Element = driver.find_element(By.CSS_SELECTOR, 'select#dept5')

                    if dept5Element.get_attribute('disabled') == 'true':
                        deptList = [
                            dept1Info,
                            dept2Info,
                            dept3Info,
                            dept4Info,
                            None,
                        ]
                        
                        totalDepartmentInfo.append(deptList)
                        continue

                    # classification step 5
                    for dept5Option in dept5Element.find_elements(By.CSS_SELECTOR, 'option'):
                        dept5Option.click()
                        time.sleep(deptTimeSleep)
                        dept5Info = saveDepartment(conn, dept5Option.get_attribute('textContent'), dept4Info[0], 'department5')
                        print('<5>', dept5Option.get_attribute('textContent'))

                        deptList = [
                            dept1Info,
                            dept2Info,
                            dept3Info,
                            dept4Info,
                            dept5Info,
                        ]
                        
                        totalDepartmentInfo.append(deptList)
                        continue
    return totalDepartmentInfo

def saveTopDepartment(conn, name):
    curs = conn.cursor()

    getDept0Info = checkTopDepartment(conn, name)
    
    if getDept0Info:
        return getDept0Info

    insertQuery = 'insert into department0 (name) values(%s)'
    values = (name)
    curs.execute(insertQuery, values)
    conn.commit()

    getDept0Info = checkTopDepartment(conn, name)

    return getDept0Info


def checkTopDepartment(conn, name):
    curs = conn.cursor()

    selectQuery = 'select * from department0 where name="{}"'.format(name)
    curs.execute(selectQuery)
    getDept0Info = curs.fetchone()
    
    return getDept0Info


def saveDepartment(conn, name, parentId, tableName):
    curs = conn.cursor()

    getDeptInfo = checkDepartment(conn, name, parentId, tableName)

    if getDeptInfo:
        return getDeptInfo

    insertQuery = 'insert into {} (name, parentDeptId) values(%s, %s)'.format(tableName)
    values = (name, parentId)
    curs.execute(insertQuery, values)
    conn.commit()

    getDeptInfo = checkDepartment(conn, name, parentId, tableName)

    return getDeptInfo

def checkDepartment(conn, name, parentId, tableName):
    curs = conn.cursor()

    selectQuery = 'select * from {} where name="{}" and parentDeptId={}'.format(tableName, name, parentId)
    curs.execute(selectQuery)
    getDeptInfo = curs.fetchone()

    return getDeptInfo


def saveTable(conn, driver, deptList):
    try:
        tableRows = driver.find_elements(By.CSS_SELECTOR, 'div#mCSB_1_container > table > tbody > tr')

        for tableRow in tableRows:
            rowData = deptList.copy()

            for tableItem in tableRow.find_elements(By.CSS_SELECTOR, 'td'):
                rowData.append(tableItem.get_attribute('textContent').strip())

            if len(rowData) == 6:
                print("해당 월은 사용 내용 없음")
                break
            
            if len(rowData) == 14:
                rowData.append(datetime.today().strftime("%Y/%m/%d %H:%M:%S"))

                data = {
                    "dept1Id": rowData[0],
                    "dept2Id": rowData[1],
                    "dept3Id": rowData[2],
                    "dept4Id": rowData[3],
                    "dept5Id": rowData[4],
                    "purpose": rowData[6],
                    "department": rowData[7],
                    "usedAt": rowData[8].replace('-','/')+':00',
                    "place": rowData[9],
                    "usePurpose": rowData[10],
                    "price": int(rowData[11].replace(',','')),
                    "user": rowData[12],
                    "paymentMethod": rowData[13],
                    "crawlDate": rowData[14],
                }

                insertTableDB(conn, data)

            if len(rowData) == 13:
                rowData.append(datetime.today().strftime("%Y/%m/%d %H:%M:%S"))

                data = {
                    "dept1Id": rowData[0],
                    "dept2Id": rowData[1],
                    "dept3Id": rowData[2],
                    "dept4Id": rowData[3],
                    "dept5Id": rowData[4],
                    "purpose": None,
                    "department": rowData[6],
                    "usedAt": rowData[7].replace('-','/')+':00',
                    "place": rowData[8],
                    "usePurpose": rowData[9],
                    "price": int(rowData[10].replace(',','')),
                    "user": rowData[11],
                    "paymentMethod": rowData[12],
                    "crawlDate": rowData[13],
                }

                insertTableDB(conn, data)
    
    except Exception as e:
        print("==========table error=========")
        print(e)
        errorList.append(deptList)


def insertTableDB(conn, data):
    query = 'insert into seoul (department1Id, department2Id, department3Id, department4Id, department5Id,'\
            'department, usedAt, place, usePurpose, price, user, paymentMethod, crawlDate)'\
            'values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    values = (data['dept1Id'], data['dept2Id'], data['dept3Id'], data['dept4Id'], data['dept5Id'], 
            data['department'], data['usedAt'], data['place'], data['usePurpose'], 
            data['price'], data['user'], data['paymentMethod'], data['crawlDate'])

    curs = conn.cursor()
    curs.execute(query, values)
    conn.commit()


# seoul_crawler(sys.argv[1], sys.argv[2])
seoul_crawler(2019, 6)
