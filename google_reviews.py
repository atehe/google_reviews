from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from csv import writer
from selenium.webdriver.chrome.options import Options
import logging, json, os, sys, time, random
from scrapy.selector import Selector
from selenium import webdriver
import pandas as pd
from selenium.webdriver.chrome.service import Service
from urllib.parse import quote
from selenium_stealth import stealth


def click(element, driver):
    """Use javascript click if selenium click method fails"""
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)


DRIVER_EXECUTABLE_PATH = "./utils/chromedriver"


service = Service(DRIVER_EXECUTABLE_PATH)
driver = webdriver.Chrome(
    service=service,
)
stealth(
    driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)


business = "Adams Photography"
formated = "+".join(business.split())

driver.get(f"https://www.google.com/maps")
# time.sleep(3)

# with open("check.html", "w", encoding="utf8") as html_file:
#     html_file.write(driver.page_source)

# accept_all = WebDriverWait(driver, 30).until(
#     EC.element_to_be_clickable(
#         (By.XPATH, '(//button[contains(.//text(), "Accept all")])[2]')
#     )
# )

# click(accept_all, driver)


def map_search(query):
    search_box = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@id="searchboxinput"]'))
    )
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)


# time.sleep(10)

map_search("Adams Photography")
