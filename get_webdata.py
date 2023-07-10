from typing import List

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

import aux_functions
import driver_init
import exceptions
from app_types import WebData


class WebpageData:
    def __init__(self):
        self.driver = driver_init.BrowserDriver().browser
        self.aux_func = aux_functions.AuxFunc(self.driver)

    def get_question(self) -> List[str]:
        """Получаем текст вопросов"""
        question_mask = '//*[@class="question-text"]'
        self.aux_func.wait_element_load(question_mask)
        question_element = self.driver.find_elements(By.XPATH, question_mask)
        return [each.text for each in question_element]  # возвращаем список вопросов

    def get_id(self) -> List[int]:
        """Получаем id вопросов"""
        id_mask = '//*[contains(@class, "question choice-question")]'
        self.aux_func.wait_element_load(id_mask)
        id_element = self.driver.find_elements(By.XPATH, id_mask)
        return [int(each.get_attribute('data-quiz-uid')) for each in id_element]  # возвращаем список id

    def get_answer(self, q_id: List[int]) -> List[List]:
        """Получаем текст ответов"""
        answer_mask = [f'//*[@data-quiz-uid={each}]//div//table//tbody//tr//td//div'
                       for each in q_id]
        self.aux_func.wait_element_load(answer_mask[0])
        answer_element = [self.driver.find_elements(By.XPATH, each) for each in answer_mask]
        answer_list = []
        for num, answer in enumerate(answer_element):
            answers = [each.text for each in answer]
            answer_list.append(answers)
        return answer_list  # возвращаем словарь с вопросами

    def get_link(self, q_id: List[int]) -> List:
        """Получаем линки до ответов"""
        link_mask = [f'//*[@data-quiz-uid={each}]//div//table//tbody//tr//td//div//span'
                     for each in q_id]
        self.aux_func.wait_element_load(link_mask[0])
        link_element = [self.driver.find_elements(By.XPATH, each) for each in link_mask]
        link_list = []
        for num, link in enumerate(link_element):
            links = [each for each in link]
            link_list.append(links)
        return link_list  # возвращаем словарь с ссылками для клика на ответ

    def get_checkbox(self, q_id: List[int]) -> List[List]:
        """Получаем состояния чекбоксов"""
        checkbox_mask = [f'//*[@data-quiz-uid={each}]//tbody//*[@class[contains(.,"check-control")]]'
                         for each in q_id]
        self.aux_func.wait_element_load(checkbox_mask[0])
        checkbox_element = [self.driver.find_elements(By.XPATH, each) for each in checkbox_mask]
        checkbox_list = []
        for num, checkbox in enumerate(checkbox_element):
            checkboxes = ['1' if each.get_attribute('class') == 'check-control checked' or each.get_attribute(
                'class') == 'check-control  checked'
                          else '0'
                          for each in checkbox]
            checkbox_list.append(checkboxes)
        return checkbox_list  # возвращаем словарь с ссылками для клика на ответ

    def get_checkbox_type(self, q_id: List[int]) -> List[int]:
        """Checkbox type (true = radiobutton, false = selector)"""
        type_mask = [f'//*[@data-quiz-uid={each}]' for each in q_id]  # list of masks of questions id
        self.aux_func.wait_element_load(type_mask[0])
        type_element = [self.driver.find_element(By.XPATH, each) for each in type_mask]
        return [1 if 'single' in each.get_attribute('class') else 0 for each in type_element]

    def get_data(self, username: str = '') -> List[WebData]:
        """Получаем данные от страницы с тестом"""
        questions = self.get_question()
        q_numb = [num for num in range(1, len(questions) + 1)]
        q_id = self.get_id()
        answers = self.get_answer(q_id)
        checkbox_state = self.get_checkbox(q_id)
        checkbox_type = self.get_checkbox_type(q_id)

        data = []
        for num, question in enumerate(questions):
            data.append(WebData(user=username,
                                question=question,
                                question_num=q_numb[num],
                                question_id=q_id[num],
                                answer=' || '.join(answers[num]),
                                answer_checkbox=' || '.join(checkbox_state[num]),
                                is_radiobutton=checkbox_type[num])
                        )
        return data


class WebDataA:
    def __init__(self):
        self.driver = driver_init.BrowserDriver().browser
        self.aux_func = aux_functions.AuxFunc(self.driver)

    def get_question(self) -> str:
        """Returns question text"""
        mask = '//*[@class="published-rich-text player-shape-view__shape-view-rich-text-view ' \
               'published-rich-text_wrap-text player-shape-view__shape-view-rich-text-view_wrap-text"]'
        return self.__clean_text(self.aux_func.try_get_text(xpath=mask, amount=1))

    def get_answer(self) -> List[str]:
        """Returns answers list"""
        mask = '//*[@class="choice-view"]'
        return [self.__clean_text(each) for each in self.aux_func.try_get_text(xpath=mask)]

    def get_link(self, answer_text: str) -> WebElement | None:
        """Returns webelement of answer (to click on it)"""
        mask = f'//*[@class="choice-view"]//*[contains(text(),"{answer_text}")]'
        try:
            return self.driver.find_element(By.XPATH, mask)
        except NoSuchElementException:
            raise exceptions.NoFoundedElement(answer_text)

    @staticmethod
    def __clean_text(text: str) -> str:
        """Clean text from whitespaces and \n"""
        restricted_symbols = ['\n', '\t']
        for symbol in restricted_symbols:
            text = text.replace(symbol, ' ')
        return ' '.join(text.split())
