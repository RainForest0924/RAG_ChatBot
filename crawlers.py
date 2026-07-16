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
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import Select

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
    options.add_argument("--headless")
    options.add_argument(f"user-agent={UserAgent().random}")
    browser = Chrome(options=options)
    browser.maximize_window()
    browser.implicitly_wait(10)

    results = []

    for dataset in datasets:
        browser.get(dataset["start_url"])

        print(f"Processing {dataset['department']}")
        
        symptom_select_menu = browser.find_element(By.CSS_SELECTOR, "select[name='q_type']")     
        symptom_list = [tmp.get_attribute("value") for tmp in symptom_select_menu.find_elements(
            By.TAG_NAME, "option") if tmp.get_attribute("value")]
        
        for symptom in symptom_list:
            print(f"Processing {symptom}")
            url = (f"https://sp1.hso.mohw.gov.tw/doctor/Often_question/type_detail.php?"
                   f"UrlClass={dataset['department']}&q_like=0&q_type={symptom}")
            browser.get(url)
            datas = []
            page = 1

            while browser.find_elements(By.CSS_SELECTOR, "ul.QAunit"):
                datas.extend(list(get_paragraph(browser)))

                page += 1
                tmp_url = url + f"&PageNo={page}"
                time.sleep(random.randint(4, 8))
                browser.get(tmp_url)

            results.extend(datas)
    
    browser.quit()
    utils.insert_symptom_subject_datas(results)
