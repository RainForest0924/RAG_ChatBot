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

if __name__ == "__main__":

    dataset_path = pathlib.Path(__file__).parent/"datasets.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        datasets = json.load(f)
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"user-agent={UserAgent().random}")
    browser = Chrome(options=options)
    browser.maximize_window()