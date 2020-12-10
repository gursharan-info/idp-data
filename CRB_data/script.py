import pandas as pd
from datetime import date, timedelta, datetime
from selenium import webdriver
import os, shutil, glob, time
#browser exposes an executable file
#Through Selenium test we will invoke the executable file which will then #invoke actual browser
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

dir_path = os.path.join(os.getcwd(), "CRB_Data")
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
    
chrome_options = webdriver.ChromeOptions()
prefs = {"download.default_directory" : dir_path, "profile.default_content_setting_values.automatic_downloads": 1}
chrome_options.add_experimental_option("prefs",prefs)
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
#get method to launch the URL

# driver.get("https://gis-prsc.punjab.gov.in/residue/Index.aspx")
#to refresh the browser


def scrapeCRB_singleDay(curr_date, year, driver):
    
    curr_day = curr_date.strftime('%d')
    curr_month = curr_date.strftime('%m')
    curr_year = curr_date.strftime('%Y')

    # Click to open drop-down
    date_input_present = EC.presence_of_element_located((By.XPATH, "//input[@id='StartTime']"))
    WebDriverWait(driver, 10).until(date_input_present)

    # Alternate date input method
    driver.execute_script(f'document.getElementById("StartTime").value = "{curr_day}-{curr_month}-{curr_year}";')

    submit_button = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_sub"]')
    driver.execute_script("arguments[0].click();", submit_button)

    # driver.implicitly_wait(5)
    dropdown_button_present = EC.presence_of_element_located((By.XPATH, '//div[@class="card-body new"]/div/div[@id="container"]/div[4]/div[1]/div[2]/button[@class="highcharts-a11y-proxy-button"]'))
    WebDriverWait(driver, 10).until(dropdown_button_present)

    dropdown_button = driver.find_element_by_xpath('//div[@class="card-body new"]/div/div[@id="container"]/div[4]/div[1]/div[2]/button[@class="highcharts-a11y-proxy-button"]')
    driver.execute_script("arguments[0].click();", dropdown_button)

    download_csv = driver.find_element_by_xpath('//div[@class="card new1"]/div/div/div/div[4]/div[@class="highcharts-contextmenu"]/ul[@class="highcharts-menu"]/li[7]')
    driver.execute_script("arguments[0].click();", download_csv)
    
#     driver.implicitly_wait(2)
    time.sleep(10)
    
    list_of_files = glob.glob(os.path.join(dir_path, 'district-wise-fire*.csv') ) # * means all if need specific format then *.csv
#     print(list_of_files)
    filename = max(list_of_files,key=os.path.getctime)
    print(filename)
    new_filename = os.path.join(dir_path+"\\"+year, r"CRB_"+curr_date.strftime('%d-%m-%Y')+".csv")
    os.rename(filename,new_filename)
    
    df = pd.read_csv(new_filename)
    df.rename(columns={'Category':'district_name', 'District':'fire_count'}, inplace=True)
    df['date'] = curr_date.strftime('%d-%m-%Y')
    df.to_csv(new_filename, index=False)
    
    return df


def startScraping(start_date, end_date, year, URL):
    
    driver.get(URL)
    
    sdate = f"{start_date}-{year}"
    edate = f"{end_date}-{year}"
    s_date = datetime.strptime(sdate, "%d-%m-%Y").date()   # start date
    e_date = datetime.strptime(edate, "%d-%m-%Y").date()  # end date

    all_dates = pd.date_range(s_date,e_date,freq='d')
    print(all_dates)
    
    year_path = os.path.join(os.getcwd(), "CRB_Data\\"+year)
    if not os.path.exists(year_path):
        os.makedirs(year_path)
    
    year_df = []
    
    for curr_date in all_dates:
        while True:
            try:
                date_input_present = EC.presence_of_element_located((By.XPATH, "//input[@id='StartTime']"))
                WebDriverWait(driver, 10).until(date_input_present)
                print(curr_date, "try block")

                current_date_df = scrapeCRB_singleDay(curr_date, year, driver )
                year_df.append(current_date_df)

            except TimeoutException:
                print("Timed out waiting for page to load")
                print(curr_date, "Time out exception")
                driver.refresh()
                continue
    
            except NoSuchElementException:
                print("Element not found exception")
                print(curr_date)
                driver.refresh()
                continue
    
            else:
                break
    
    pd.concat(year_df).to_csv(f"{dir_path}\\{year}\\{year}_combined_{s_date.strftime('%b')}-{e_date.strftime('%b')}.csv", index=False)
    
''' Change the ranges and year as required. Each of the scraping call below would create a seperate folder for each year in the same directory where script is located.
Inside the year folder there would be season folder, which would further contain daily files and combined file for each season.
eg: CRB_Data\2020\apr-may\2020_combined_Apr-May.csv
'''

startScraping("10-04", "31-05", "2016", "https://gis-prsc.punjab.gov.in/residue/Index.aspx")
startScraping("01-09", "30-11", "2016", "https://gis-prsc.punjab.gov.in/residue/Index.aspx")
startScraping("10-04", "31-05", "2017", "https://gis-prsc.punjab.gov.in/residue/Index.aspx")
startScraping("01-09", "30-11", "2017", "https://gis-prsc.punjab.gov.in/residue/Index.aspx")
startScraping("10-04", "31-05", "2018", "https://gis-prsc.punjab.gov.in/residue/Index.aspx")
startScraping("01-09", "30-11", "2018", "https://gis-prsc.punjab.gov.in/residue/Index.aspx")
startScraping("10-04", "31-05", "2019", "https://gis-prsc.punjab.gov.in/residue/Index.aspx")
startScraping("01-09", "30-11", "2019", "https://gis-prsc.punjab.gov.in/residue/Index.aspx")
startScraping("10-04", "31-05", "2020", "https://gis-prsc.punjab.gov.in/residue/Index.aspx")
startScraping("01-09", "30-11", "2020", "https://gis-prsc.punjab.gov.in/residue/Index.aspx")

