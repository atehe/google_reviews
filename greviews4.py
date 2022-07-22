from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from csv import writer
from selenium.webdriver.chrome.options import Options
import logging, json, os, sys, time, random
from scrapy.selector import Selector
from seleniumwire import webdriver
import pandas as pd
from selenium.webdriver.chrome.service import Service
from urllib.parse import quote
from selenium_stealth import stealth
import datetime
import pandas as pd


DRIVER_EXECUTABLE_PATH = "./utils/chromedriver"


def click(element, driver):
    """Use javascript click if selenium click method fails"""
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)


def map_search(query):
    search_box = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@id="searchboxinput"]'))
    )
    search_box.clear()
    search_box.send_keys(query)
    print(f"Searching {query}...")
    time.sleep(2)
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@id="searchbox-searchbutton"]'))
    )
    click(search_button, driver)
    time.sleep(10)


def parse_search():
    try:

        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@role='feed']/div/div[@role='article']")
            )
        )

        search_result_items = driver.find_elements(
            by=By.XPATH, value="//div[@role='feed']/div/div[@role='article']"
        )
        print("Selecting Vendor...")
        click(search_result_items[0], driver)
        time.sleep(5)
        to_review_page()
        return is_review
    except:
        is_review = to_review_page()
        return is_review


def to_review_page():
    more_reviews = None
    counter = 0
    while not more_reviews:
        try:
            more_reviews = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//button[contains(@jsaction,"moreReviews")]',
                    )
                )
            )

            print("Moving to review page")
            click(more_reviews, driver)
            return True
        except:
            print("Reviews not found")
            return False


def getReviews(url, tag, is_review=True):
    if not is_review:
        return [], None

    noofdays = 10000000
    script = """u = "{0}"
    AddDays = -{0}
    someDate = new Date()
    result = someDate.setDate(someDate.getDate() + AddDays)
    rangeD = new Date(result)
    function sleep(ms) {
          return new Promise(resolve => setTimeout(resolve, ms));
       }
    ur = u.split("!2m2!1i")
    ur[0] = ur[0] + "!2m2!1i"
    ur.splice(1, 0, "")
    i = 0
    responses = []
    while (true) {
        response = {}
        if (i === 0) {
            s = ""
        } else {
            s = i.toString()
        }
        sleep(150)
        ur[1] = s
        url = ur.join("")
        data1 = await fetch(url)
            .then(response => response.text())
            .then(function(data){return JSON.parse(data.slice(5))})
        if (data1[2] === null){
            break
        }
        response.url = url
        test = false
        response.reviews = []
        for (jj in data1[2]){
            if (data1[2][jj].at(27) < rangeD){
                test = true
                break
            }
            response.reviews.push(data1[2][jj])
        }
        responses.push(response)
        if (i===3){
            break
        }
        i++
    }
    return responses
    """.split(
        "\n"
    )

    def clean_text(txt):
        try:
            txt = str(txt)
        except:
            pass
        if txt:
            txt = (
                txt.replace("\n", "")
                .replace("\r", "")
                .replace("|", "")
                .replace("\t", "")
            )
            return txt

    try:
        place = driver.find_element(
            by=By.XPATH, value="//h1[contains(@class,'fontHeadlineLarge')]/span"
        ).text
        if not place:
            place = clean_text(url.split("place/")[1].split("/")[0].replace("+", " "))
    except:
        place = clean_text(url.split("place/")[1].split("/")[0].replace("+", " "))
    while True:
        try:
            total_star = float(
                driver.execute_script(
                    """return document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.jANrlb > div.fontDisplayLarge").innerText"""
                )
            )
            total_reviews = int(
                driver.execute_script(
                    """ return document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.jANrlb > div.fontBodySmall").textContent"""
                )
                .split(" ")[0]
                .replace(",", "")
            )
            star_5_percent = (
                int(
                    driver.execute_script(
                        """ return document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.ExlQHd > table > tbody > tr:nth-child(1)").ariaLabel"""
                    )
                    .split(" ")[2]
                    .replace(",", "")
                )
                / total_reviews
            )
            star_4_percent = (
                int(
                    driver.execute_script(
                        """ return document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.ExlQHd > table > tbody > tr:nth-child(2)").ariaLabel"""
                    )
                    .split(" ")[2]
                    .replace(",", "")
                )
                / total_reviews
            )
            star_3_percent = (
                int(
                    driver.execute_script(
                        """ return document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.ExlQHd > table > tbody > tr:nth-child(3)").ariaLabel"""
                    )
                    .split(" ")[2]
                    .replace(",", "")
                )
                / total_reviews
            )
            star_2_percent = (
                int(
                    driver.execute_script(
                        """ return document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.ExlQHd > table > tbody > tr:nth-child(4)").ariaLabel"""
                    )
                    .split(" ")[2]
                    .replace(",", "")
                )
                / total_reviews
            )
            star_1_percent = (
                int(
                    driver.execute_script(
                        """ return document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.ExlQHd > table > tbody > tr:nth-child(5)").ariaLabel"""
                    )
                    .split(" ")[2]
                    .replace(",", "")
                )
                / total_reviews
            )
            break
        except Exception as e:
            continue

    star_5_percent = round(star_5_percent * 100, ndigits=2)
    star_4_percent = round(star_4_percent * 100, ndigits=2)
    star_3_percent = round(star_3_percent * 100, ndigits=2)
    star_2_percent = round(star_2_percent * 100, ndigits=2)
    star_1_percent = round(star_1_percent * 100, ndigits=2)
    print(
        star_5_percent, star_4_percent, star_3_percent, star_2_percent, star_1_percent
    )

    driver.execute_script(
        """b = document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf")
    b.scrollBy(0,10000)
    """
    )
    time.sleep(3)

    data_url = None
    while not data_url:
        req = driver.requests
        for i in req:
            if "listentitiesreviews" in i.url:
                data_url = i.url.replace("!3e1!", "!3e2!")
                break
    print("Extracting reviews")

    def dater(data_url1):
        script[0] = script[0].format(data_url)
        script[1] = script[1].format(str(noofdays))
        try:
            responses = driver.execute_script("\n".join(script))

        except Exception as e:
            print(e)
            return [0], e
        ret = []
        n = 0
        file_name = f"response/{tag}.txt"
        with open(file_name, "a", encoding="utf-8") as response_file:
            json.dump(responses, response_file, indent=4)

            for i, response in enumerate(responses):
                uurl = response.get("url")
                for i in response.get("reviews"):
                    name = clean_text(i[0][1])
                    comment = clean_text(i[3])

                    owner_response = clean_text(
                        "-" if not (i[9] and i[9][1]) else i[9][1]
                    )
                    owner_response_time = clean_text(
                        "-"
                        if not (i[9] and i[9][3])
                        else datetime.datetime.fromtimestamp(i[9][3] / 1000.0).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    )
                    idc = clean_text(i[10])
                    star = clean_text(i[4])
                    extraction_date = clean_text(
                        datetime.datetime.today().strftime("%Y-%m-%d")
                    )
                    time = clean_text(
                        datetime.datetime.fromtimestamp(i[27] / 1000.0).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        if i[-5]
                        else ""
                    )
                    ret.append(
                        [
                            tag,
                            url,
                            extraction_date,
                            place,
                            total_reviews,
                            total_star,
                            star_1_percent,
                            star_2_percent,
                            star_3_percent,
                            star_4_percent,
                            star_5_percent,
                            idc,
                            name,
                            star,
                            time,
                            comment,
                            owner_response,
                            owner_response_time,
                            uurl,
                        ]
                    )  # parsing and storing

        return ret, None

    res, error = dater(data_url)
    return (res, url) if (len(res) == 0 or res[0] != 0) else f"{tag}|{url}|{error}"


def save_reviews(result):

    columns = [
        "Vendor Name",
        "Url",
        "Extraction Date",
        "Place",
        "Total reviews",
        "Total star",
        "1 star %",
        "2 star %",
        "3 star %",
        "4 star %",
        "5 star %",
        "Post Id",
        "Name",
        "Star",
        "Timestamp",
        "Review",
        "Owner response",
        "Owner response time",
        "Source",
    ]
    result = pd.DataFrame(result[0], columns=columns)
    result.to_csv(
        "data2.csv", mode="a", index=None, header=not os.path.exists("data.csv")
    )


if __name__ == "__main__":
    service = Service(DRIVER_EXECUTABLE_PATH)
    driver = webdriver.Chrome(
        service=service,
    )
    driver.get("https://www.google.com/maps/@4.8882198,6.9960933,15z")

    df = pd.read_csv("Vendors to scrape - Sheet1.csv")

    for i, query in enumerate(df["Vendor Name"].unique()[300:400]):
        print("=======" + str(i) + " " + query + "========")
        try:
            map_search(query)
            is_review = parse_search()
            url = driver.current_url

            result = getReviews(url, query, is_review)
            save_reviews(result)
            driver.get("https://www.google.com/maps/@4.8882198,6.9960933,15z")
        except:
            with open("error.txt", "a") as error:
                error.write(query)
                error.write("\n")
