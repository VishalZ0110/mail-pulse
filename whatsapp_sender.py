from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains

import time
import config

PROFILE_PATH = r'./chrome_session'


def start_browser(headless=False):

    options = webdriver.ChromeOptions()

    options.add_argument(f"--user-data-dir={PROFILE_PATH}")
    options.add_argument("--profile-directory=Default")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    if headless:
        options.add_argument("--headless=new")


    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get("https://web.whatsapp.com")

    time.sleep(20)

    return driver


def send_multiline_message(driver, message):

    lines = message.split("\n")

    actions = ActionChains(driver)

    for i, line in enumerate(lines):
        actions.send_keys(line)

        if i < len(lines) - 1:
            actions.key_down(Keys.SHIFT)
            actions.send_keys(Keys.ENTER)
            actions.key_up(Keys.SHIFT)

    actions.send_keys(Keys.ENTER)
    actions.perform()


def send_message(driver, message):

    search_box = driver.find_element(
        By.XPATH, '//input[@aria-label="Search or start a new chat"]')

    search_box.clear()
    search_box.send_keys(config.WHATSAPP_CONTACT_NAME)

    time.sleep(2)

    search_box.send_keys(Keys.ENTER)

    time.sleep(2)

    msg_box = driver.find_element(
        By.XPATH, '//div[@contenteditable="true"][@aria-placeholder="Type a message"]')

    send_multiline_message(driver, message)
    msg_box.send_keys(Keys.ENTER)
    # wait for atleast 20 seconds
    time.sleep(20)
