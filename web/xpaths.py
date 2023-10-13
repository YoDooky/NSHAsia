import time

from selenium.webdriver import ActionChains
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from typing import List

from aux_functions import AuxFunc
import db
from exceptions import NoFoundedElement

import driver_init


# DECORATOR
def xpath_decorator(has_exception: bool = True):
    """DECORATOR. Writes xpath for current topic to db"""

    def upper_wrapper(func):
        def wrapper(*args):
            driver = driver_init.BrowserDriver().browser
            driver.switch_to.window(driver.window_handles[-1])
            topic_url = WebDataA().get_topic_url()

            # focus to frame
            if func.__name__ != 'iframe':
                AuxFunc().switch_to_frame(xpath=XpathResolver().iframe())

            # find xpath in db
            xpathdb_data = db.XpathController().read()
            for data in xpathdb_data:
                if data.url != topic_url:
                    continue
                if data.element != func.__name__:
                    continue
                return data.xpath

            # perform click
            actions = ActionChains(driver)
            actions.move_by_offset(0, 0).click().perform()

            # find xpath in method and write it if it corrects to db
            masks = func(*args)
            for mask in masks:
                for i in range(3):
                    # validate xpath for correctness
                    try:
                        driver.find_element(By.XPATH, mask)
                        db.XpathController().write(db.Xpath(url=topic_url, xpath=mask, element=func.__name__))
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
    @xpath_decorator(has_exception=True)
    def iframe():
        """iframe"""
        return [
            '//*[@class="content_frame"]',

            '//*[@class="scorm_content"]//iframe'
        ]

    @staticmethod
    @xpath_decorator(has_exception=True)
    def results_button():
        """Button <СМОТРЕТЬ РЕЗУЛЬТАТЫ>"""
        return [
            '//*[@class="quiz-control-panel__container quiz-control-panel__container_right"]//'
            'button[@class="quiz-control-panel__button"]'
            '//*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"СМОТРЕТЬ РЕЗУЛЬТАТЫ")]',

            '//*[@class="quiz-control-panel__container quiz-control-panel__container_right"]'
            '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
            '//*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"СМОТРЕТЬ РЕЗУЛЬТАТЫ")]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=False)
    def start_button():
        """Button <НАЧАТЬ ТЕСТ>"""
        return [
            '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
            '//*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"НАЧАТЬ ТЕСТ")]',

            '//button[@class="quiz-control-panel__button quiz-control-panel__button_right-arrow quiz-control-panel'
            '__button_show-arrow"]'
            '//*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"НАЧАТЬ ТЕСТ")]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=True)
    def answer_button():
        """Button <ОТВЕТИТЬ>"""
        return [
            '//button[@class="quiz-control-panel__button"]'
            '//*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"ОТВЕТИТЬ")]',

            '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
            '//*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"ОТВЕТИТЬ")]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=False)
    def continue_button():
        """Button <ПРОДОЛЖИТЬ> after click <ОТВЕТИТЬ> done"""
        return [
            '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium" '
            'and not(@style="display: none;")]'
            '//*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"ПРОДОЛЖИТЬ")]',

            '//button[@class="quiz-control-panel__button quiz-control-panel__button_right-arrow '
            'quiz-control-panel__button_show-arrow"]'
            '//*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"ПРОДОЛЖИТЬ")]',

            '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
            '//*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"ПРОДОЛЖИТЬ")]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=True)
    def repeat_button():
        """Button <Повторить тест>"""
        return [
            '//*[@class="player-shape-view player-shape-view_button"]'
            '//*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"ПОВТОРИТЬ ТЕСТ")]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=True)
    def popup_approve():
        """Button <Да> in pop-up window to resume quiz"""
        return [
            '//button[@class="message-box-buttons-panel__window-button"]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=False)
    def next_theory():
        """Button <Далее> for the theory"""
        return [
            '//*[@class="universal-control-panel__button universal-control-panel__button_next '
            'universal-control-panel__button_right-arrow"]',

            '//*[@class="uikit-primary-button uikit-primary-button_size_medium navigation-controls__button '
            'uikit-primary-button_next navigation-controls__button_next"]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=False)
    def next_test_part():
        """Button <ДАЛЕЕ> for topics where is many theory and test"""
        return [
            '//*[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"][last()]'
            '//*[contains(text(),"ДАЛЕЕ")]',

            '//*[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
            '//*[contains(text(),"ДАЛЕЕ")]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=True)
    def questions_progress():
        """Questions amount label <Вопрос X из X>"""
        return [
            '//*[@class="quiz-top-panel__question-score-info quiz-top-panel__question-score-info_with-separator"]',

            '//*[@class="quiz-control-panel__question-score-info"]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=False)
    def current_score():
        """Current topic score"""
        return [
            '//*[@class="quiz-top-panel__quiz-score-info quiz-top-panel__quiz-score-info_with-separator"]',

            '//*[@class="quiz-control-panel__quiz-score-info"]',

            '//*[@class="quiz-top-panel__quiz-score-info"]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=False)
    def answer_result():
        """Answer result (correct or not correct)"""
        return [
            '//*[@class="quiz-feedback-panel"]',

            '//*[@class="quiz-feedback-panel__header"]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=True)
    def topic_score():
        """Question score label at the end of the topic"""
        return [
            '//*[@class="player-shape-view"]'
            '//*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"ТЕСТ")]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=False)
    def theory_progress():
        """Theory progress label <X из X>"""
        return [
            '//*[@class="progressbar__label"]',

            '//*[@class="navigation-controls__label"]'
        ]

    # WebData
    @staticmethod
    # @select_xpath_decorator(has_exception=True)
    def topic_name():
        """Name of current topic"""
        return '//*[@id="contentItemTitle"]'

    @staticmethod
    @xpath_decorator(has_exception=True)
    def question_text():
        """Question of current topic"""
        return [
            '//*[@class="published-rich-text player-shape-view__shape-view-rich-text-view '
            'published-rich-text_wrap-text player-shape-view__shape-view-rich-text-view_wrap-text"]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=True)
    def answer_text():
        """Answers of current topic"""
        return [
            '//*[@class="choice-view"]//*[@class="choice-content"]',

            '//*[@class="choice-view__choice-container"]//*[@class="choice-content"]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=True)
    def answer_choice_type():
        """Type of answers selectors of current topic"""
        return [
            '//*[@class="choice-view"]//*[@class="choice-view__mock-active-element"]',

            '//*[@class="choice-view__choice-container"]//*[@class="choice-view__mock-active-element"]'
        ]


class WebDataA:

    def __init__(self):
        self.driver = driver_init.BrowserDriver().browser
        self.aux_func = AuxFunc()

    def get_topic_name(self) -> str:
        """Return current topic name"""
        self.aux_func.switch_to_frame()
        mask = XpathResolver.topic_name()
        return self.__clean_text(self.aux_func.try_get_text(xpath=mask, amount=1))

    def get_topic_url(self) -> str:
        """Return topic URL"""
        self.aux_func.switch_to_frame()
        mask = XpathResolver.topic_name()
        return self.aux_func.try_get_attribute(xpath=mask, attribute='baseURI')

    def get_question(self) -> str:
        """Returns question text"""
        self.aux_func.switch_to_frame(xpath=XpathResolver.iframe())
        mask = XpathResolver.question_text()
        return self.__clean_text(self.aux_func.try_get_text(xpath=mask, amount=1))

    def get_answers(self) -> List[str]:
        """Returns answers list"""
        self.aux_func.switch_to_frame(xpath=XpathResolver.iframe())
        mask = XpathResolver.answer_text()
        return [self.__clean_text(each) for each in self.aux_func.try_get_text(xpath=mask)]

    def get_link(self, answer_text: str) -> WebElement | None:
        """Returns webelement of answer (to click on it)"""
        self.aux_func.switch_to_frame(xpath=XpathResolver.iframe())
        driver = driver_init.BrowserDriver().browser
        mask = XpathResolver.answer_text()
        try:
            for element in driver.find_elements(By.XPATH, mask):
                if self.__clean_text(element.text) == answer_text:
                    return element
        except NoSuchElementException:
            raise NoFoundedElement(mask)

    def get_selectors_type(self) -> str:
        """Returns type of selectors via checking firs founded element (radiobutton or checkbox)"""
        self.aux_func.switch_to_frame(xpath=XpathResolver.iframe())
        mask = XpathResolver.answer_choice_type()
        try:
            return self.driver.find_element(By.XPATH, mask).get_attribute('type')
        except NoSuchElementException:
            raise NoFoundedElement(mask)

    def get_clicked_answers(self) -> List[str]:
        answers = self.get_answers()
        data = []
        driver = driver_init.BrowserDriver().browser
        answer_text_mask = XpathResolver.answer_text()
        answer_choice_mask = XpathResolver.answer_choice_type()
        answers_data = zip(answers,
                           driver.find_elements(By.XPATH, answer_text_mask),
                           driver.find_elements(By.XPATH, answer_choice_mask))
        try:
            for answer in answers_data:
                if self.__clean_text(answer[1].text) != answer[0]:
                    continue
                if answer[2].get_attribute('ariaChecked') == 'false':
                    continue
                data.append(answer[0])
            return data
        except NoSuchElementException:
            raise NoFoundedElement(answer_choice_mask)

    @staticmethod
    def __clean_text(text: str) -> str:
        spec_symbols_accord = {'\xa0': ' ', '\u200B': ''}
        for symbol in spec_symbols_accord:
            text = text.replace(symbol, spec_symbols_accord.get(symbol))
        return ' '.join(text.split())
