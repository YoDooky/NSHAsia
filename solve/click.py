import time

from selenium.webdriver.remote.webelement import WebElement
from typing import List


def click_answer(answer_link: List[WebElement]):
    for link in answer_link:
        link.click()
        time.sleep(1)
