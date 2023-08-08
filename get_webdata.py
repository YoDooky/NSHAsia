from typing import List

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

import aux_functions
import driver_init
import exceptions


class WebDataA:
    TOPIC_MASK = '//*[@id="contentItemTitle"]'
    QUESTION_MASK = '//*[@class="published-rich-text player-shape-view__shape-view-rich-text-view ' \
                    'published-rich-text_wrap-text player-shape-view__shape-view-rich-text-view_wrap-text"]'
    ANSWERS_MASK = '//*[@class="choice-view"]'

    def __init__(self):
        self.driver = driver_init.BrowserDriver().browser
        self.aux_func = aux_functions.AuxFunc()

    def get_topic_name(self) -> str:
        """Return current topic name"""
        self.aux_func.switch_to_frame()
        mask = self.TOPIC_MASK
        topic_name = self.aux_func.try_get_text(xpath=mask, amount=1)
        return topic_name

    def get_question(self) -> str:
        """Returns question text"""
        self.aux_func.switch_to_frame(xpath='//*[@class="content_frame"]')
        mask = self.QUESTION_MASK
        return self.aux_func.try_get_text(xpath=mask, amount=1)

    def get_answers(self) -> List[str]:
        """Returns answers list"""
        self.aux_func.switch_to_frame(xpath='//*[@class="content_frame"]')
        mask = f'{self.ANSWERS_MASK}//*[@class="choice-content"]'
        return [each for each in self.aux_func.try_get_text(xpath=mask)]

    def get_link(self, answer_text: str) -> WebElement | None:
        """Returns webelement of answer (to click on it)"""
        self.aux_func.switch_to_frame(xpath='//*[@class="content_frame"]')
        mask = f'{self.ANSWERS_MASK}//*[contains(text(),"{answer_text}")]'
        try:
            return self.driver.find_element(By.XPATH, mask)
        except NoSuchElementException:
            raise exceptions.NoFoundedElement(mask)

    def get_selectors_type(self) -> str:
        """Returns type of selectors via checking firs founded element (radiobutton or checkbox)"""
        self.aux_func.switch_to_frame(xpath='//*[@class="content_frame"]')
        mask = f'{self.ANSWERS_MASK}//*[@class="choice-view__mock-active-element"]'
        try:
            return self.driver.find_element(By.XPATH, mask).get_attribute('type')
        except NoSuchElementException:
            raise exceptions.NoFoundedElement(mask)

    def get_clicked_answers(self) -> List[str]:
        answers = self.get_answers()
        mask = 'empty selector mask'
        data = []
        try:
            for answer in answers:
                mask = f'//*[@class="choice-view"]//*[contains(text(),"{answer}")]/' \
                       f'ancestor::div[3]//*[@class="choice-view__mock-active-element"]'
                selector = self.driver.find_element(By.XPATH, mask)
                if selector.get_attribute('ariaChecked') == 'false':
                    continue
                data.append(answer)
            return data
        except NoSuchElementException:
            raise exceptions.NoFoundedElement(mask)

    @staticmethod
    def __clean_text(text: str) -> str:
        """Clean text from whitespaces and \n"""
        restricted_symbols = ['\n', '\t']
        for symbol in restricted_symbols:
            text = text.replace(symbol, ' ')
        return ' '.join(text.split())
