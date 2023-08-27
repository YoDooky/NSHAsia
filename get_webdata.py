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
        return self.__clean_text(self.aux_func.try_get_text(xpath=mask, amount=1))

    def get_question(self) -> str:
        """Returns question text"""
        self.aux_func.switch_to_frame(xpath='//*[@class="content_frame"]')
        mask = self.QUESTION_MASK
        return self.__clean_text(self.aux_func.try_get_text(xpath=mask, amount=1))

    def get_answers(self) -> List[str]:
        """Returns answers list"""
        self.aux_func.switch_to_frame(xpath='//*[@class="content_frame"]')
        mask = f'{self.ANSWERS_MASK}//*[@class="choice-content"]'
        return [self.__clean_text(each) for each in self.aux_func.try_get_text(xpath=mask)]

    def get_link(self, answer_text: str) -> WebElement | None:
        """Returns webelement of answer (to click on it)"""
        self.aux_func.switch_to_frame(xpath='//*[@class="content_frame"]')
        driver = driver_init.BrowserDriver().browser
        mask = f'{self.ANSWERS_MASK}//*[@class="choice-content"]'
        try:
            for element in driver.find_elements(By.XPATH, mask):
                if element.text == answer_text:
                    return element
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
        data = []
        driver = driver_init.BrowserDriver().browser
        answer_text_mask = '//*[@class="choice-view"]//*[@class="choice-content"]'
        answer_choice_mask = '//*[@class="choice-view"]//*[@class="choice-view__mock-active-element"]'
        answers_data = zip(answers,
                           driver.find_elements(By.XPATH, answer_text_mask),
                           driver.find_elements(By.XPATH, answer_choice_mask))
        try:
            for answer in answers_data:
                if answer[1].text != answer[0]:
                    continue
                if answer[2].get_attribute('ariaChecked') == 'false':
                    continue
                data.append(answer[0])
            return data
        except NoSuchElementException:
            raise exceptions.NoFoundedElement(answer_choice_mask)

    @staticmethod
    def __clean_text(text: str) -> str:
        spec_symbols_accord = {'\xa0': ' ', '\u200b': ''}
        for symbol in spec_symbols_accord:
            text = text.replace(symbol, spec_symbols_accord.get(symbol))
        return ' '.join(text.split())
