import time

from selenium.webdriver import ActionChains
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from typing import List

# from aux_functions import AuxFunc
import aux_functions as af
import db
from exceptions import NoFoundedElement

from driver_init import driver


# DECORATOR
def xpath_decorator(has_exception: bool = True):
    """DECORATOR. Writes xpath for current topic to db"""

    def upper_wrapper(func):
        def wrapper(*args):
            driver.switch_to.window(driver.window_handles[-1])
            topic_url = TopicWebData().get_topic_url()

            # focus to frame
            if func.__name__ != 'iframe':
                af.AuxFunc().switch_to_frame(xpath=XpathResolver.iframe())

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
            try:
                actions.move_by_offset(0, driver.execute_script("return window.innerHeight;")).click().perform()
            except Exception:
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
        """Button <НАЧАТЬ ТЕСТ> or <ПРИСТУПИТЬ К ТЕСТИРОВАНИЮ>"""
        return [
            '//button[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
            '//*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"НАЧАТЬ ТЕСТ")]',

            '//button[@class="quiz-control-panel__button quiz-control-panel__button_right-arrow quiz-control-panel'
            '__button_show-arrow"]'
            '//*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"НАЧАТЬ ТЕСТ")]',

            '//*[@class="complete-section-content-container"]/button',  # button <Завершить> similar to <НАЧАТЬ ТЕСТ>
        ]

    @staticmethod
    @xpath_decorator(has_exception=False)
    def goto_quiz_button():
        """Button <ПЕРЕЙТИ К ТЕСТИРОВАНИЮ> or <ПРИСТУПИТЬ К ТЕСТИРОВАНИЮ>"""
        return [
            '//span[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"), '
            '"ТЕСТИРОВАНИЮ")]'  # button <ПЕРЕЙТИ К ТЕСТИРОВАНИЮ> or <ПРИСТУПИТЬ К ТЕСТИРОВАНИЮ>
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
            'quiz-control-panel__button_show-arrow" and not(@style="display: none;")]'
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
    @xpath_decorator(has_exception=False)
    def popup_approve():
        """Button <Да> in pop-up window to resume quiz"""
        return [
            '//button[@class="message-box-buttons-panel__window-button" '
            'and contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"НЕТ")]',

            '//button[@class="uikit-primary-button '
            'uikit-primary-button_size_medium message-box-buttons__window-button"]'
            '/*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"НЕТ")]'
        ]

    @staticmethod
    def close_quiz():
        """Close quiz button in right top corner"""
        return '//*[@class="toolbar_button js_toolbar_button close"]'

    @staticmethod
    @xpath_decorator(has_exception=False)
    def next_theory():
        """Button <Далее> for the theory"""
        return [
            '//*[@class="universal-control-panel__button universal-control-panel__button_next '
            'universal-control-panel__button_right-arrow"]',

            '//*[@class="uikit-primary-button uikit-primary-button_size_medium '
            'navigation-controls__button uikit-primary-button_next navigation-controls__button_next" '
            'and not(@disabled)]',

            '//*[@class="next-section-content-container"]/button'
        ]

    @staticmethod
    @xpath_decorator(has_exception=False)
    def next_test_part():
        """Button <ДАЛЕЕ> for topics where is many theory and test"""
        return [
            '//*[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"][last()]'
            '//*[contains(text(),"ДАЛЕЕ")]',

            '//*[@class="quiz-uikit-primary-button quiz-uikit-primary-button_size_medium"]'
            '//*[contains(text(),"ДАЛЕЕ")]',

            '//*[@class="quiz-control-panel__button quiz-control-panel__button_right-arrow '
            'quiz-control-panel__button_show-arrow" and not(@style="display: none;")]'
            '/*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
            '"ДАЛЕЕ")]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=True)
    def questions_progress():
        """Questions amount label <Вопрос X из X>"""
        return [
            '//*[@class="quiz-top-panel__question-score-info quiz-top-panel__question-score-info_with-separator" '
            'and not(@style="display: none;")]',

            '//*[@class="quiz-control-panel__question-score-info"]'
        ]

    @staticmethod
    @xpath_decorator(has_exception=False)
    def current_score():
        """Current topic score"""
        return [
            '//*[@class="quiz-top-panel__quiz-score-info quiz-top-panel__quiz-score-info_with-separator"]',

            '//*[@class="quiz-control-panel__quiz-score-info"]',

            '//*[@class="quiz-top-panel__quiz-score-info"]',

            '//*[@class="quiz-top-panel__quiz-score-info quiz-top-panel__quiz-score-info_only-quiz-score"]'
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
    def quiz_score():
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
    def course_name() -> str:
        """Course name"""
        return '//*[@class[contains(.,"title_dir_ltr")]]'

    @staticmethod
    def topic_name() -> str:
        """Name of current topic"""
        return '//*[@id="contentItemTitle"]'

    @staticmethod
    def topic_status() -> str:
        """Topic status (Завершен, Пройден на X%, В процессе, Не начат"""
        return '//*[@class="xed2c2__text xed2c2__text_type_none"]'

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


class TopicWebData:

    def get_topic_name(self) -> str:
        """Return current topic name"""
        af.AuxFunc().switch_to_frame()
        mask = XpathResolver.topic_name()
        return self.__clean_text(af.AuxFunc().try_get_text(xpath=mask, amount=1))

    @staticmethod
    def get_topic_url() -> str:
        """Return topic URL"""
        af.AuxFunc().switch_to_frame()
        mask = XpathResolver.topic_name()
        return af.AuxFunc().try_get_attribute(xpath=mask, attribute='baseURI')

    def get_question(self) -> str:
        """Returns question text"""
        af.AuxFunc().switch_to_frame(xpath=XpathResolver.iframe())
        mask = XpathResolver.question_text()
        return self.__clean_text(af.AuxFunc().try_get_text(xpath=mask, amount=1))

    def get_answers(self) -> List[str]:
        """Returns answers list"""
        af.AuxFunc().switch_to_frame(xpath=XpathResolver.iframe())
        mask = XpathResolver.answer_text()
        return [self.__clean_text(each) for each in af.AuxFunc().try_get_text(xpath=mask)]

    def get_link(self, answer_text: str) -> WebElement | None:
        """Returns webelement of answer (to click on it)"""
        af.AuxFunc().switch_to_frame(xpath=XpathResolver.iframe())
        mask = XpathResolver.answer_text()
        try:
            for element in driver.find_elements(By.XPATH, mask):
                if self.__clean_text(element.text) == answer_text:
                    return element
        except NoSuchElementException:
            raise NoFoundedElement(mask)

    @staticmethod
    def get_selectors_type() -> str:
        """Returns type of selectors via checking firs founded element (radiobutton or checkbox)"""
        af.AuxFunc().switch_to_frame(xpath=XpathResolver.iframe())
        mask = XpathResolver.answer_choice_type()
        try:
            return driver.find_element(By.XPATH, mask).get_attribute('type')
        except NoSuchElementException:
            raise NoFoundedElement(mask)

    def get_clicked_answers(self) -> List[str]:
        answers = self.get_answers()
        data = []
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


class CourseWebData:
    # def get_courses_name(self) -> List[str]:
    #     return [course.get_attribute('innerText') for course in self._get_courses()]

    @staticmethod
    def get_course_name(course: WebElement) -> str:
        return course.get_attribute('innerText')

    @staticmethod
    def get_course_topics() -> List[WebElement]:
        mask = XpathResolver.course_name()
        return driver.find_elements(By.XPATH, mask)
