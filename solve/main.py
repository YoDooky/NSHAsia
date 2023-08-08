import time
from selenium.webdriver.remote.webelement import WebElement
from typing import List

import driver_init
from db.database import session
from db.models import WebData, WebAnswer, DbData, DbAnswer
from get_webdata import WebDataA
from aux_functions import AuxFunc


# wrong_answer = '//*[@class="quiz-feedback-panel"]'


def get_answers_links():
    webdata = session.query(WebData).all()
    answers = []
    for data in webdata:
        answers = [answer.text for answer in data.answers]
    return [WebDataA().get_link(answer) for answer in answers]


def click_answer(links: List[WebElement]):
    for link in links:
        link.click()
        time.sleep(1)


def click_approve_button() -> bool:
    """Click <Ответить> button"""
    mask = '//button[@class="quiz-control-panel__button"]//*[contains(text(),"ОТВЕТИТЬ")]'
    if not AuxFunc().try_click(xpath=mask):
        return False


def click_continue_button():
    """Click <Продолжить> button"""
    mask = '//button[@class="quiz-control-panel__button quiz-control-panel__button_right-arrow ' \
           'quiz-control-panel__button_show-arrow"]//*[contains(text(),"ПРОДОЛЖИТЬ")]'
    if not AuxFunc().try_click(xpath=mask):
        return False
    return True


def check_result() -> bool:
    """Check if answer is correct or not"""
    mask = '//*[@class="quiz-feedback-panel__header quiz-feedback-panel__header_correct"]'
    if AuxFunc().try_get_text(xpath=mask, amount=1, try_numb=2):
        return True


def solve_question():
    lks = get_answers_links()
    check_in_db()
    click_answer(lks)
    click_approve_button()
    if not check_result():
        print('WRONG')
        return False
    else:
        print('CORRECT')
        return True
