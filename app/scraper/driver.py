from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import config


def create_driver(language: str = "fr-FR") -> webdriver.Chrome:
    options = Options()
    options.add_argument("--window-size=1440,1000")
    options.add_argument(f"--lang={language}")
    options.add_argument("--disable-notifications")
    if config.HEADLESS:
        options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT_SECONDS)
    return driver
