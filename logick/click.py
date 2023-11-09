import logging
import time
from typing import List

from selenium.webdriver.remote.webelement import WebElement

from exceptions import ImpossibleToClick
from logick.aux_funcs import RandomDelay


def click_answer(links: List[WebElement]) -> bool:
    """Click answer and check if it was clicked"""
    try_numb = 5
    for link in links:
        for i in range(try_numb):
            try:
                time.sleep(RandomDelay.get_question_delay())
                link.click()
                break
            except Exception as ex:
                print(f'Не удалось кликнуть по ответу. Попытка {i + 1} из {try_numb}')
                logging.exception(f"{ex}\nAn error occurred during click to answer")
            if i >= try_numb - 1:
                return False
    return True
