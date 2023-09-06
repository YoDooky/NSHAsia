# IFRAME = [
#     '//*[@class="content_frame"]'
# ]
# RESULTS_BUTTON = [
#     '//*[@class="quiz-control-panel__container quiz-control-panel__container_right"]//'
#     'button[@class="quiz-control-panel__button"]//*[contains(text(),"СМОТРЕТЬ РЕЗУЛЬТАТЫ")]',
#
#     '//*[@class="quiz-control-panel__container quiz-control-panel__container_right"]'
#     '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
#     '//*[contains(text(),"СМОТРЕТЬ РЕЗУЛЬТАТЫ")]',
# ]
# ANSWER_BUTTON = [
#     '//button[@class="quiz-control-panel__button"]//*[contains(text(),"ОТВЕТИТЬ")]',
#
#     '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
#     '//*[contains(text(),"ОТВЕТИТЬ")]'
# ]
# CONTINUE_BUTTON = [
#     '//button[@class="quiz-control-panel__button quiz-control-panel__button_right-arrow '
#     'quiz-control-panel__button_show-arrow"]//*[contains(text(),"ПРОДОЛЖИТЬ")]',
#
#     '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
#     '//*[contains(text(),"ПРОДОЛЖИТЬ")]'
# ]
# REPEAT_BUTTON = [
#     '//*[@class="player-shape-view player-shape-view_button"]//*[contains(text(),"ПОВТОРИТЬ ТЕСТ")]'
# ]
# POPUP_APPROVE = [
#     '//button[@class="message-box-buttons-panel__window-button"]'
# ]
import time

from selenium.webdriver.common.by import By

import driver_init
from aux_functions import AuxFunc
from db.controllers import XpathController
from db.models import Xpath
from exceptions import NoFoundedElement
from web.get_webdata import WebDataA


class XpathResolver:
    """Base class for webelements"""

    # def __init__(self):
    #     self.__themes = {
    #         'Эксплуатация буровых насосов серии F и УНБТ': XpathA,
    #         'Буровые насосы плунжерные': XpathA,
    #         'Эксплуатация дизельных двигателей': XpathA,
    #         '5. Эксплуатация автоматических коробок переключения передач': XpathB,
    #     }
    #
    # def get(self, theme_name: str):
    #     demand_class = self.__themes.get(theme_name)
    #     if demand_class is None:
    #         return self
    #     return demand_class

    def __init__(self):
        self.topic_name = WebDataA().get_topic_name()
        self.driver = driver_init.BrowserDriver().browser

    # DECORATOR
    def write_path(self, func):
        """DECORATOR. Writes xpath for current topic to db"""
        xpathdb_data = XpathController().read()
        for data in xpathdb_data:
            if data.topic == self.topic_name:
                return data.xpath

        def wrapper():
            masks = func()
            for mask in masks:
                for i in range(5):
                    try:
                        self.driver.find_element(By.XPATH, mask)
                        XpathController().write(Xpath(topic=self.topic_name, xpath=mask, element=func.__name__))
                        return mask
                    except Exception:
                        time.sleep(1)
            raise NoFoundedElement(func.__name__)

        return wrapper

    @staticmethod
    @write_path
    def iframe():
        """iframe"""
        return [
            '//*[@class="content_frame"]'
        ]
        # for mask in masks:
        #     if not AuxFunc().switch_to_frame(xpath=mask):
        #         continue
        #     XpathController().write(Xpath(topic=self.topic_name, text=mask, element=self.iframe.__name__))

    def results_button(self):
        """Button <СМОТРЕТЬ РЕЗУЛЬТАТЫ>"""
        return [
            '//*[@class="quiz-control-panel__container quiz-control-panel__container_right"]//'
            'button[@class="quiz-control-panel__button"]//*[contains(text(),"СМОТРЕТЬ РЕЗУЛЬТАТЫ")]',

            '//*[@class="quiz-control-panel__container quiz-control-panel__container_right"]'
            '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
            '//*[contains(text(),"СМОТРЕТЬ РЕЗУЛЬТАТЫ")]'
        ]

    def answer_button(self):
        """Button <ОТВЕТИТЬ>"""
        return [
            '//button[@class="quiz-control-panel__button"]//*[contains(text(),"ОТВЕТИТЬ")]',

            '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
            '//*[contains(text(),"ОТВЕТИТЬ")]'
        ]

    def continue_button(self):
        """Button <ПРОДОЛЖИТЬ> after click <ОТВЕТИТЬ> done"""
        return [
            '//button[@class="quiz-control-panel__button quiz-control-panel__button_right-arrow '
            'quiz-control-panel__button_show-arrow"]//*[contains(text(),"ПРОДОЛЖИТЬ")]',

            '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
            '//*[contains(text(),"ПРОДОЛЖИТЬ")]'
        ]

    def repeat_button(self):
        """Button <Повторить тест>"""
        return [
            '//*[@class="player-shape-view player-shape-view_button"]//*[contains(text(),"ПОВТОРИТЬ ТЕСТ")]'
        ]

    def popup_approve(self):
        """Button <Да> in pop-up window to resume quiz"""
        return [
            '//button[@class="message-box-buttons-panel__window-button"]'
        ]

    def next_theory(self):
        """Button <Далее> for the theory"""
        return [
            '//*[@class="universal-control-panel__button universal-control-panel__button_next '
            'universal-control-panel__button_right-arrow"]',

            '//*[@class="uikit-primary-button uikit-primary-button_size_medium navigation-controls__button '
            'uikit-primary-button_next navigation-controls__button_next"]'
        ]

    def questions_progress(self):
        """Questions amount label <Вопрос X из X>"""
        return [
            '//*[@class="quiz-top-panel__question-score-info quiz-top-panel__question-score-info_with-separator"]',

            '//*[@class="quiz-control-panel__question-score-info"]'
        ]

    def topic_score(self):
        """Question score label at the end of the topic"""
        return [
            '//*[@class="player-shape-view"]'
        ]

    def theory_progress(self):
        """Theory progress label <X из X>"""
        return [
            '//*[@class="progressbar__label"]',

            '//*[@class="navigation-controls__label"]'
        ]

#
# class XpathA(Xpath):
#     """Webelements for next themes:
#     <Эксплуатация буровых насосов серии F и УНБТ>
#     <Буровые насосы плунжерные>
#     <Эксплуатация дизельных двигателей>
#     """
#     pass
#
#
# class XpathB(Xpath):
#     """Webelements for next themes:
#         <5. Эксплуатация автоматических коробок переключения передач>
#         """
#
#     @staticmethod
#     def answer_button():
#         return '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]' \
#                '//*[contains(text(),"ОТВЕТИТЬ")]'
#
#     @staticmethod
#     def continue_button():
#         return '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]' \
#                '//*[contains(text(),"ПРОДОЛЖИТЬ")]'
#
#     @staticmethod
#     def results_button():
#         return '//*[@class="quiz-control-panel__container quiz-control-panel__container_right"]' \
#                '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]' \
#                '//*[contains(text(),"СМОТРЕТЬ РЕЗУЛЬТАТЫ")]'
#
#     @staticmethod
#     def questions_progress():
#         return '//*[@class="quiz-control-panel__question-score-info"]'
#
#     @staticmethod
#     def theory_progress():
#         return '//*[@class="navigation-controls__label"]'
#
#     @staticmethod
#     def next_theory():
#         return '//*[@class="uikit-primary-button uikit-primary-button_size_medium navigation-controls__button ' \
#                'uikit-primary-button_next navigation-controls__button_next"]'
