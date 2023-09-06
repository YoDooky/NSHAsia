import time

from selenium.webdriver.common.by import By

import driver_init
from aux_functions import AuxFunc
from db.controllers import XpathController
from db.models import Xpath
from exceptions import NoFoundedElement
from web.get_webdata import WebDataA


# DECORATOR
def select_xpath_decorator(has_exception: bool = True):
    """DECORATOR. Writes xpath for current topic to db"""

    def upper_wrapper(func):
        def wrapper(*args):
            topic_name = WebDataA().get_topic_name()
            driver = driver_init.BrowserDriver().browser

            # focus to frame
            if func.__name__ != 'iframe':
                AuxFunc().switch_to_frame(xpath=XpathResolver().iframe())

            # find xpath in db
            xpathdb_data = XpathController().read()
            for data in xpathdb_data:
                if data.topic != topic_name:
                    continue
                if data.element != func.__name__:
                    continue
                return data.xpath

            # find xpath in method and write it if it corrects to db
            masks = func(*args)
            for mask in masks:
                for i in range(3):
                    # validate xpath for correctness
                    try:
                        driver.find_element(By.XPATH, mask)
                        XpathController().write(Xpath(topic=topic_name, xpath=mask, element=func.__name__))
                        return mask
                    except Exception:
                        time.sleep(1)
            if has_exception:
                raise NoFoundedElement(func.__name__)

        return wrapper

    return upper_wrapper


class XpathResolver:
    """Base class for webelements"""

    @staticmethod
    @select_xpath_decorator(has_exception=True)
    def iframe():
        """iframe"""
        return [
            '//*[@class="content_frame"]'
        ]

    @staticmethod
    @select_xpath_decorator(has_exception=True)
    def results_button():
        """Button <СМОТРЕТЬ РЕЗУЛЬТАТЫ>"""
        return [
            '//*[@class="quiz-control-panel__container quiz-control-panel__container_right"]//'
            'button[@class="quiz-control-panel__button"]//*[contains(text(),"СМОТРЕТЬ РЕЗУЛЬТАТЫ")]',

            '//*[@class="quiz-control-panel__container quiz-control-panel__container_right"]'
            '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
            '//*[contains(text(),"СМОТРЕТЬ РЕЗУЛЬТАТЫ")]'
        ]

    @staticmethod
    @select_xpath_decorator(has_exception=False)
    def start_button():
        """Button <НАЧАТЬ ТЕСТ>"""
        return [
            '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
            '//*[contains(text(),"НАЧАТЬ ТЕСТ")]',

            '//button[@class="quiz-control-panel__button quiz-control-panel__button_right-arrow quiz-control-panel'
            '__button_show-arrow"]//*[contains(text(),"НАЧАТЬ ТЕСТ")]'
        ]

    @staticmethod
    @select_xpath_decorator(has_exception=True)
    def answer_button():
        """Button <ОТВЕТИТЬ>"""
        return [
            '//button[@class="quiz-control-panel__button"]//*[contains(text(),"ОТВЕТИТЬ")]',

            '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
            '//*[contains(text(),"ОТВЕТИТЬ")]'
        ]

    @staticmethod
    @select_xpath_decorator(has_exception=True)
    def continue_button():
        """Button <ПРОДОЛЖИТЬ> after click <ОТВЕТИТЬ> done"""
        return [
            '//button[@class="quiz-control-panel__button quiz-control-panel__button_right-arrow '
            'quiz-control-panel__button_show-arrow"]//*[contains(text(),"ПРОДОЛЖИТЬ")]',

            '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
            '//*[contains(text(),"ПРОДОЛЖИТЬ")]'
        ]

    @staticmethod
    @select_xpath_decorator(has_exception=True)
    def repeat_button():
        """Button <Повторить тест>"""
        return [
            '//*[@class="player-shape-view player-shape-view_button"]//*[contains(text(),"ПОВТОРИТЬ ТЕСТ")]'
        ]

    @staticmethod
    @select_xpath_decorator(has_exception=True)
    def popup_approve():
        """Button <Да> in pop-up window to resume quiz"""
        return [
            '//button[@class="message-box-buttons-panel__window-button"]'
        ]

    @staticmethod
    @select_xpath_decorator(has_exception=True)
    def next_theory():
        """Button <Далее> for the theory"""
        return [
            '//*[@class="universal-control-panel__button universal-control-panel__button_next '
            'universal-control-panel__button_right-arrow"]',

            '//*[@class="uikit-primary-button uikit-primary-button_size_medium navigation-controls__button '
            'uikit-primary-button_next navigation-controls__button_next"]'
        ]

    @staticmethod
    @select_xpath_decorator(has_exception=True)
    def questions_progress():
        """Questions amount label <Вопрос X из X>"""
        return [
            '//*[@class="quiz-top-panel__question-score-info quiz-top-panel__question-score-info_with-separator"]',

            '//*[@class="quiz-control-panel__question-score-info"]'
        ]

    @staticmethod
    @select_xpath_decorator(has_exception=True)
    def current_score():
        """Current topic score on the bottom of the page"""
        return [
            '//*[@class="quiz-top-panel__quiz-score-info quiz-top-panel__quiz-score-info_with-separator"]',
            '//*[@class="quiz-control-panel__quiz-score-info"]'
        ]

    @staticmethod
    @select_xpath_decorator(has_exception=True)
    def topic_score():
        """Question score label at the end of the topic"""
        return [
            '//*[@class="player-shape-view"]'
        ]

    @staticmethod
    @select_xpath_decorator(has_exception=True)
    def theory_progress():
        """Theory progress label <X из X>"""
        return [
            '//*[@class="progressbar__label"]',

            '//*[@class="navigation-controls__label"]'
        ]
