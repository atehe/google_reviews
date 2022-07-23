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
import datetime
import pandas as pd
import requests

DRIVER_EXECUTABLE_PATH = "./utils/chromedriver.exe"
os.makedirs("reviews_response", exist_ok=True)


def click(element, driver):
    """Use javascript click if selenium click method fails"""
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)


def parse_reviews(url, num_pages=3):
    """Extract and clean reviews from maps backend api"""
    url_split = url.split("!2m2!1i")
    review_data = []
    for review in range(num_pages):

        page_url = f'{url_split[0]}{"!2m2!1i"}{review}{url_split[-1]}'
        response = requests.get(page_url)

        # cleaning up and making response parseable
        response_text = response.text[5:]
        response_text = json.loads(response_text)

        reviews = response_text[2] or []

        page_review_dict = {"url": page_url, "reviews": []}
        for review in reviews:
            page_review_dict["reviews"].append(review)

        review_data.append(page_review_dict)

    return review_data


def map_search(query):
    print(f">>> Getting reviews for {query}")
    query_encoded = "+".join(query.split())

    driver.get(f"https://www.google.com/maps/place/{query_encoded}")
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@id="searchbox-searchbutton"]'))
    )
    click(search_button, driver)


def go_to_place_page():
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@role='feed']/div/div[@role='article']")
            )
        )
        search_result_items = driver.find_elements(
            by=By.XPATH, value="//div[@role='feed']/div/div[@role='article']"
        )
        print(">>> Moving to Vendor Page...")
        click(search_result_items[0], driver)
    except:
        pass


def go_to_review_page():

    try:

        more_reviews_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//button[contains(@jsaction,"moreReviews")]',
                )
            )
        )

        more_reviews_button2 = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//button[contains(@jsaction,"moreReviews")]',
                )
            )
        )

        print(">>> Moving to review page")
        click(more_reviews_button, driver)
        return True
    except:
        pass


def quick_search_to_review():
    review_page = False
    counter = 0
    while not review_page and counter < 2:
        counter += 1

        try:
            go_to_place_page()
            review_page = go_to_review_page()
            if review_page:
                return review_page
        except:
            continue

    return review_page


def clean_text(txt):
    try:
        txt = str(txt)
    except:
        pass
    if txt:
        txt = txt.replace("\n", "").replace("\r", "").replace("|", "").replace("\t", "")
        return txt


def get_review_stars(driver):
    # get percetage review stars
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.jANrlb > div.fontDisplayLarge",
                )
            )
        )
        total_star = driver.find_element(
            by=By.CSS_SELECTOR,
            value="#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.jANrlb > div.fontDisplayLarge",
        ).text
        total_reviews = int(
            driver.execute_script(
                """ return document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.jANrlb > div.fontBodySmall").textContent"""
            )
            .split(" ")[0]
            .replace(",", "")
        )
        num_5_stars = int(
            driver.execute_script(
                """ return document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.ExlQHd > table > tbody > tr:nth-child(1)").ariaLabel"""
            )
            .split(" ")[2]
            .replace(",", "")
        )
        num_4_stars = int(
            driver.execute_script(
                """ return document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.ExlQHd > table > tbody > tr:nth-child(2)").ariaLabel"""
            )
            .split(" ")[2]
            .replace(",", "")
        )
        num_3_stars = int(
            driver.execute_script(
                """ return document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.ExlQHd > table > tbody > tr:nth-child(3)").ariaLabel"""
            )
            .split(" ")[2]
            .replace(",", "")
        )
        num_2_stars = int(
            driver.execute_script(
                """ return document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.ExlQHd > table > tbody > tr:nth-child(4)").ariaLabel"""
            )
            .split(" ")[2]
            .replace(",", "")
        )
        num_1_stars = int(
            driver.execute_script(
                """ return document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PPCwl > div > div.ExlQHd > table > tbody > tr:nth-child(5)").ariaLabel"""
            )
            .split(" ")[2]
            .replace(",", "")
        )

        return {
            "num_5_stars": num_5_stars,
            "num_4_stars": num_4_stars,
            "num_3_stars": num_3_stars,
            "num_2_stars": num_2_stars,
            "num_1_stars": num_1_stars,
            "total_star": total_star,
            "total_reviews": total_reviews,
        }
    except Exception as e:
        print(f"Error: {e} in Extracting review counts")
        return {}


def get_reviews(query):

    map_search(query)

    # delete previous backend request to fecth new ones
    del driver.requests

    review_page = quick_search_to_review()

    if not review_page:
        return []

    url = driver.current_url
    # Get name of place extracted from screen
    try:
        extracted_place = driver.find_element(
            by=By.XPATH, value="//h1[contains(@class,'fontHeadlineLarge')]/span"
        ).text
        if not place:
            extracted_place = clean_text(
                url.split("place/")[1].split("/")[0].replace("+", " ")
            )
    except:
        extracted_place = clean_text(
            url.split("place/")[1].split("/")[0].replace("+", " ")
        )

    review_star_count = get_review_stars(driver)
    num_5_stars = review_star_count.get("num_5_stars", None)
    num_4_stars = review_star_count.get("num_4_stars", None)
    num_3_stars = review_star_count.get("num_3_stars", None)
    num_2_stars = review_star_count.get("num_2_stars", None)
    num_1_stars = review_star_count.get("num_1_stars", None)
    total_star = review_star_count.get("total_star", None)
    total_reviews = review_star_count.get("total_reviews", None)

    try:
        num_pages = 6 - int(float(total_star))
    except:
        num_pages = 2

    try:
        driver.execute_script(
            """b = document.querySelector("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf")
        b.scrollBy(0,10000)
        """
        )

        backend_api_url = None
        while not backend_api_url:
            backend_responses = driver.requests
            for backend_response in backend_responses:
                if "listentitiesreviews" in backend_response.url:
                    backend_api_url = backend_response.url
                    break
            time.sleep(0.5)  # wait for backend to recieve review api response

        print(">>> Extracted API URL")

        try:
            review_api_responses = parse_reviews(backend_api_url, num_pages) or []
        except Exception as e:
            review_api_responses = []
            print(f"ERROR: {e}")

        # saving review api response
        file_name = f"reviews_response/{query}.json"
        with open(file_name, "w", encoding="utf-8") as response_file:
            json.dump(review_api_responses, response_file, indent=4)

        reviews = []
        for review_page in review_api_responses:
            api_url = review_page.get("url")
            for review in review_page.get("reviews", []):
                name = clean_text(review[0][1])
                comment = clean_text(review[3])

                owner_response = clean_text(
                    None if not (review[9] and review[9][1]) else review[9][1]
                )
                owner_response_time = clean_text(
                    None
                    if not (review[9] and review[9][3])
                    else datetime.datetime.fromtimestamp(
                        review[9][3] / 1000.0
                    ).strftime("%Y-%m-%d %H:%M:%S")
                )
                star = clean_text(review[4])
                review_time = clean_text(
                    datetime.datetime.fromtimestamp(review[27] / 1000.0).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if review[-5]
                    else None
                )
                reviews.append(
                    [
                        query,
                        url,
                        extracted_place,
                        total_reviews,
                        total_star,
                        num_1_stars,
                        num_2_stars,
                        num_3_stars,
                        num_4_stars,
                        num_5_stars,
                        name,
                        star,
                        comment,
                        review_time,
                        owner_response,
                        owner_response_time,
                        api_url,
                    ]
                )
        return reviews
    except Exception as e:
        print(e)
        return []


def save_reviews(reviews, filename):
    if reviews:
        print("Saving Reviews")
    columns = [
        "query",
        "Review URL",
        "Extracted Vendor",
        "Number of Reviews",
        "Average Stars",
        "Number of 1 Star Reviews",
        "Number of 2 Stars Reviews",
        "Number of 3 Stars Reviews",
        "Number of 4 Stars Reviews",
        "Number of 5 Stars Reviews",
        "Name",
        "Number of Stars",
        "Comment",
        "Time",
        "Owner Response",
        "Owner Response Time",
        "API URL",
    ]
    df = pd.DataFrame(reviews, columns=columns)
    df.to_csv(filename, mode="a", index=None, header=not os.path.exists(filename))


if __name__ == "__main__":
    service = Service(DRIVER_EXECUTABLE_PATH)
    driver = webdriver.Chrome(
        service=service,
    )

    vendors_df = pd.read_csv("Vendors to scrape - Sheet1.csv")

    for i, place in enumerate(vendors_df["Vendor Name"].unique()[2:5]):
        print(f"=============== {i} ==================")
        reviews = get_reviews(place)
        save_reviews(reviews, "map_review.csv")
