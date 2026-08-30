import random
import re
import time
import json
import utils
import pathlib
from datetime import datetime
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import Select

PAGE_LOAD_TIMEOUT = 60
GET_RETRIES = 3
SYMPTOM_LIMIT = 50


def safe_get(browser: Chrome, url: str, retries: int = GET_RETRIES) -> bool:
    """
    Load a page with retries so one slow response does not stop the whole crawler.
    """
    for attempt in range(1, retries + 1):
        try:
            browser.get(url)
            return True
        except TimeoutException as e:
            print(f"Timeout loading page ({attempt}/{retries}): {url}")
            print(f"Error: {e}")
        except WebDriverException as e:
            print(f"WebDriver error loading page ({attempt}/{retries}): {url}")
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error loading page ({attempt}/{retries}): {url}")
            print(f"Error: {e}")

        try:
            browser.execute_script("window.stop();")
        except Exception:
            pass

        if attempt < retries:
            time.sleep(5 * attempt)

    return False


def get_paragraph(chrome: Chrome):
    """
    Get the paragraph from the current page of the browser.

    Args:
        chrome (Chrome): The Chrome browser instance.
    """
    for paragraph in chrome.find_elements(By.CSS_SELECTOR, "ul.QAunit"):
        try:
            subject = paragraph.find_element(By.CSS_SELECTOR, "li.subject").text
            asker_info = paragraph.find_element(By.CSS_SELECTOR, "li.asker").text

            match = re.search(r"／([男女])／.*?,(\d{4}/\d{2}/\d{2})", asker_info)
            gender = match.group(1)
            question_time = datetime.strptime(match.group(2), "%Y/%m/%d")

            question = paragraph.find_element(By.CSS_SELECTOR, "li.ask").text
            answer = paragraph.find_element(By.CSS_SELECTOR, "li.ans").text

            doctor_info = paragraph.find_element(By.CSS_SELECTOR, "li.doctor").text
            match_doctor = re.search(r"／.*?,\s*(\d{4}/\d{2}/\d{2})", doctor_info)
            answer_time = datetime.strptime(match_doctor.group(1), "%Y/%m/%d")

            data = dict(
                subject_id = int(subject.split(" ")[0].replace("#", "")),
                subject = "".join(subject.split(" ")[1:]),
                symptom = symptom,
                question = question,
                gender = gender,
                question_time = question_time,
                department = dataset["department"],
                answer = answer,
                answer_time = answer_time,                
            )
            yield data

        except Exception as e:
            print(f"Error processing paragraph: {e}")
            continue

if __name__ == "__main__":

    dataset_path = pathlib.Path(__file__).parent/"datasets.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        datasets = json.load(f)
    
    options = Options()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"user-agent={UserAgent().random}")
    options.page_load_strategy = "eager"
    browser = Chrome(options=options)
    browser.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    browser.maximize_window()
    browser.implicitly_wait(10)

    try:
        for dataset in datasets:
            dataset_results = []

            if not safe_get(browser, dataset["start_url"]):
                print(f"Skip dataset because start page failed: {dataset['department']}")
                continue

            print(f"Processing {dataset['department']}")

            symptom_select_menu = browser.find_element(By.CSS_SELECTOR, "select[name='q_type']")     
            symptom_list = [tmp.get_attribute("value") for tmp in symptom_select_menu.find_elements(
                By.TAG_NAME, "option") if tmp.get_attribute("value")]

            symptom_list_select = symptom_list
            if len(symptom_list) > SYMPTOM_LIMIT:
                symptom_list_select = random.sample(symptom_list, SYMPTOM_LIMIT)

            for (i, symptom) in enumerate(symptom_list_select):
                print(f"Processing {symptom}_{i}")
                url = (f"https://sp1.hso.mohw.gov.tw/doctor/Often_question/type_detail.php?"
                       f"UrlClass={dataset['department']}&q_like=0&q_type={symptom}")
                if not safe_get(browser, url):
                    print(f"Skip symptom because page failed: {symptom}")
                    continue
                datas = []
                page = 1

                while browser.find_elements(By.CSS_SELECTOR, "ul.QAunit"):
                    datas.extend(list(get_paragraph(browser)))

                    page += 1
                    tmp_url = url + f"&PageNo={page}"
                    time.sleep(random.randint(4, 8))
                    if not safe_get(browser, tmp_url):
                        print(f"Stop paging because page failed: {tmp_url}")
                        break

                dataset_results.extend(datas)

            if dataset_results:
                print("Start writing data into database~~")
                utils.insert_symptom_subject_datas(dataset_results)
                print(f"Inserted {len(dataset_results)} records for {dataset['department']}")

    finally:
        browser.quit()
