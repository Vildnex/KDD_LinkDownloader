import copy
import os
import time

from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

OPEN_ID = "<OPEN_ID>"
PASSWORD = "<PASSWORD>"
DOWNLOAD_DIR = "<DOWNLOAD_FOLDER>"


def check_exists_by_xpath(by: By, value: str, driv: webdriver.Firefox):
    try:
        driv.find_element(by, value)
    except NoSuchElementException:
        return False
    return True


def download_wait(directory, timeout, nfiles=None):
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        files = os.listdir(directory)
        if nfiles and len(files) != nfiles:
            dl_wait = True

        for fname in files:
            if fname.endswith('.part'):
                dl_wait = True

        seconds += 1
    return seconds


options = webdriver.FirefoxOptions()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.dir", DOWNLOAD_DIR)
options.set_preference("browser.download.manager.showWhenStarting", False)
# options.set_preference("browser.download.useDownloadDir", True)
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-netcdf")

driver = webdriver.Firefox(options=options)
driver.get("https://esgf-data.dkrz.de/search/cordex-dkrz/")
accordionToggleItems = driver.find_elements_by_class_name("accordionToggleItem")
for button in accordionToggleItems:
    button.click()

driver.find_element_by_id("checkbox_project_CORDEX-Adjust").click()

driver.find_element_by_id("checkbox_product_bias-adjusted-output").click()

driver.find_element_by_id("checkbox_domain_EUR-11").click()
driver.find_element_by_id("checkbox_domain_EUR-11i").click()

driver.find_element_by_id("checkbox_experiment_rcp45").click()
driver.find_element_by_id("checkbox_experiment_family_All").click()

driver.find_element_by_id("checkbox_rcm_name_RACMO22E").click()

driver.find_element_by_id("checkbox_time_frequency_day").click()

driver.find_element_by_id("checkbox_variable_prAdjust").click()
driver.find_element_by_id("checkbox_variable_tasmaxAdjust").click()
driver.find_element_by_id("checkbox_variable_tasminAdjust").click()

driver.find_element_by_id(
    "checkbox_variable_long_name_Bias-Adjusted Daily Maximum Near-Surface Air Temperature").click()
driver.find_element_by_id(
    "checkbox_variable_long_name_Bias-Adjusted Daily Minimum Near-Surface Air Temperature").click()
driver.find_element_by_id("checkbox_variable_long_name_Bias-Adjusted Near-Surface Air Temperature").click()
driver.find_element_by_id("checkbox_variable_long_name_Bias-Adjusted Precipitation").click()

driver.find_element_by_id("checkbox_cf_standard_name_air_temperature").click()
driver.find_element_by_id("checkbox_cf_standard_name_daily_maximum_near-surface_temperature_maximum").click()
driver.find_element_by_id("checkbox_cf_standard_name_daily_minimum_near-surface_temperature_minimum").click()
driver.find_element_by_id("checkbox_cf_standard_name_precipitation").click()

Select(driver.find_element_by_id('limit')).select_by_value("100")

driver.find_element_by_xpath("//input[@value='Search']").click()

founded_elements = driver.find_elements_by_link_text("THREDDS Catalog")

href_links_founded_elements = [link.get_attribute('href') for link in founded_elements]

thredds_size = len(href_links_founded_elements)
thredds_index = 1
for link_founded in href_links_founded_elements:
    print("THREDDS Catalog {} out of {}".format(thredds_index, thredds_size))
    thredds_index += 1
    driver.get(link_founded)
    files = [link.get_attribute('href') for link in driver.find_elements_by_partial_link_text(".nc")]

    files_size = len(files)
    file_index = 1
    for file in files:
        print("START DOWNLOAD: File {} out of {}".format(file_index, files_size))
        file_index += 1
 
        driver.get(file)
        driver.find_element_by_link_text("HTTPServer").click()

        if check_exists_by_xpath(By.CLASS_NAME, "custom-combobox-input", driver):
            driver.find_element_by_class_name("custom-combobox-input").send_keys(OPEN_ID)
            driver.find_element_by_id("SubmitButton").click()
            timeout = 5
            element_present = EC.presence_of_element_located((By.ID, 'password'))
            WebDriverWait(driver, timeout).until(element_present)
            driver.find_element_by_id("password").send_keys(PASSWORD)
            driver.find_element_by_class_name("button").click()

        download_wait(DOWNLOAD_DIR, 60 * 30)
        print("COMPLETE DOWNLOAD")
