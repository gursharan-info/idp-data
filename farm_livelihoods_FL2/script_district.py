import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
from selenium import webdriver
import os, shutil, glob, time
#browser exposes an executable file
#Through Selenium test we will invoke the executable file which will then #invoke actual browser
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from shutil import move

dir_path = os.path.join(os.getcwd(), "FL2")
if not os.path.exists(dir_path):
    os.makedirs(dir_path)

year_range = '2020-21'
    
chrome_options = webdriver.ChromeOptions()
prefs = {"download.default_directory" : dir_path, "profile.default_content_setting_values.automatic_downloads": 1}
chrome_options.add_experimental_option("prefs",prefs)
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
#get method to launch the URL
driver.get("https://nrlm.gov.in/FLMPRIndicatorsWiseAction.do?methodName=showDetail")



def get_program_data(program_type):
    programButton = driver.find_element_by_xpath('//input[@value="'+program_type+'"]')
    if programButton.get_attribute("checked") != "true":
        programButton.click()
    time.sleep(1)
    total_data = []
    
    programPath = os.path.join(dir_path, program_type.lower())
    if not os.path.exists(programPath):
        os.makedirs(programPath)
            
    selectState = Select(driver.find_element_by_xpath('//*[@id="stateId"]'))
    stateOptions = selectState.options

    for stateIndex in range(1, len(stateOptions)):
        
        selectState.select_by_index(stateIndex)
        stateText = stateOptions[stateIndex].text
        time.sleep(1)

        selectDistrict = Select(driver.find_element_by_xpath('//*[@id="districtId"]'))
        districtOptions = selectDistrict.options

        statePath = os.path.join(programPath, stateText.lower().replace(" ", "_"))
        if not os.path.exists(statePath):
            os.makedirs(statePath)

        for distIndex in range(1, len(districtOptions)):
            
            selectDistrict.select_by_index(distIndex)
            districtText = districtOptions[distIndex].text

            submitButton = driver.find_element_by_xpath('//input[@value="Submit"]')
            driver.execute_script("arguments[0].click();", submitButton)

            driver.implicitly_wait(2)

            downloadButton = driver.find_element_by_class_name('buttons-excel')
            driver.execute_script("arguments[0].click();", downloadButton)

            time.sleep(1)

            list_of_files = glob.glob(os.path.join(dir_path, 'Farm Livelihood Indicators and Month Wise Report*.xlsx') ) # * means all if need specific format then *.csv
            filename = max(list_of_files,key=os.path.getctime)

            df = pd.read_excel(filename, skiprows=[0])
            columns = ['October','April','May','June','July','August','September']
            df = df.reindex(df.columns.union(columns, sort=False), axis=1, fill_value=np.nan)
            sorted_cols = ['Indicators','Purpose','As on March   2020','FY:  2020-21  Target','October','April','May',
                           'June','July','August','September','Total','% of Achievement','Cumulative  Achievement']
            df = df[sorted_cols]
            df.columns = ['indicator','purpose','on_march_2020','2020-21_target', 'october','april','may','june','july',
                          'august','september','total','percent_achievement','cumulative_achievement']
            
            df.insert(0, 'program_type', program_type.upper())
            df.insert(0, 'year', '2020-2021')
            df.insert(0, 'district', districtText)
            df.insert(0, 'state', stateText)
            df['date_added'] = datetime.today().strftime("%d-%m-%Y")
    #         display(df)

            total_data.append(df)

            move(filename, os.path.join(statePath, districtText.lower().replace(" ", "_")+".xlsx"))
            csv_name = os.path.join(statePath, districtText.lower().replace(" ", "_")+".csv")
            print(csv_name)
            df.to_csv(csv_name, index=False)

            time.sleep(1)
            selectState = Select(driver.find_element_by_xpath('//*[@id="stateId"]'))
            stateOptions = selectState.options
            selectDistrict = Select(driver.find_element_by_xpath('//*[@id="districtId"]'))
            districtOptions = selectDistrict.options
    
    program_df = pd.concat(total_data)
    program_df[['on_march_2020','october','april','may','june','july','august'
           ,'september','total','percent_achievement']] = program_df[['on_march_2020','october','april','may','june','july','august'
           ,'september','total','percent_achievement']].fillna(value=0).astype(np.int64, errors='ignore')
    program_df.to_csv(os.path.join(programPath, f"{program_type.lower()}_combined.csv"), index=False)
    return program_df


clear_checkboxes()
nretp_df = get_program_data('Nretp')
clear_checkboxes()
mksp_df = get_program_data('Mksp')
clear_checkboxes()
sraap_df = get_program_data('Sraap')

master_df = pd.concat([nretp_df,mksp_df,sraap_df])
master_df.to_csv(os.path.join(dir_path, f"FL2_districts_ptype_{year_range}.csv"), index=False)