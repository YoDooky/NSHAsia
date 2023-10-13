import re
import time
from selenium.webdriver import ActionChains
import logging
# from typing import Type, Union

from log import print_log
from aux_functions import AuxFunc
import driver_init
from web.xpaths import XpathResolver

from logick import strat, question_solve


class TopicStrategy:
    def __init__(self):
        self.last_questions_left = None
        self.question_strategy = None
        self.has_next_button = True  # define if topic has <ПРОДОЛЖИТЬ> button after cliked <ОТВЕТИТЬ> button

    def main(self):
        self.question_strategy = None

        try:
            strat.TheorySolveStrategy(strat.TheoryA()).do_work()
        except Exception as ex:
            res = input(f"{ex}\n"
                        f"Перейди на экран с другим тестом и нажми <Enter>")
            if not res:
                self.main()

        if not self.solve_topic():
            AuxFunc().play_sound()
            res = input('Возникла ошибка при решении теста. Перейди на экран с тестом и нажми <Enter>.\n'
                        'Нажми <q> и после <Enter> для выхода')
            if not res:
                self.main()
        else:  # if current test is passed then check if there is next topic and run solving again
            if AuxFunc().try_click(xpath=XpathResolver().next_test_part(), try_numb=5, window_numb=1):
                print_log('В текущем топике найден еще тест, продолжаю решать')
                self.main()

    def solve_topic(self) -> bool:
        """Solve current topic"""
        print_log("--> Решаю тест")
        try:
            AuxFunc().switch_to_frame(xpath=XpathResolver().iframe())
            questions_left = self.get_questions_left()
            for i in range(questions_left + 1):
                self.solve_question(i)
            self.click_next_button(XpathResolver().results_button())

            if self.is_topic_passed():
                print_log('Решение темы завершено')
                self.question_strategy = None
                return True

            self.click_next_button(XpathResolver().repeat_button())
            return self.solve_topic()
        except Exception as ex:
            self.question_strategy = None
            print_log(f'Ошибка: {ex}. Возникла проблема при решении курса. Пробую еще раз')
            logging.exception("An error occurred during topic solving")

    def solve_question(self, num: int):
        """Solve current question"""
        if num != 0:
            if self.has_next_button is True:
                self.has_next_button = self.click_next_button(XpathResolver().continue_button())
            if not self.is_next_question(self.last_questions_left):  # if next question not loaded, reload page
                self.reboot_question_page()
        self.last_questions_left = self.get_questions_left()

        q_solve = question_solve.QuestionSolve(strategy=self.question_strategy, questions_left=self.last_questions_left)
        self.question_strategy = q_solve.solve_question()  # remember question solving strategy for current topic

    @staticmethod
    def click_next_button(mask: str):
        """Click button"""
        AuxFunc().switch_to_frame(xpath=XpathResolver().iframe())
        driver = driver_init.BrowserDriver().browser
        actions = ActionChains(driver)
        try_numb = 5
        for i in range(try_numb):
            actions.move_by_offset(0, 0).click().perform()
            if not AuxFunc().try_click(xpath=mask, scroll_to=False, try_numb=2):
                continue
            else:
                return True
        return False

    @staticmethod
    def is_topic_passed():
        text = AuxFunc().try_get_text(xpath=XpathResolver().topic_score(), amount=1)
        if ' не ' not in text:
            return True
        return False

    @staticmethod
    def get_questions_left() -> int:
        """Returns questions left from current topic"""
        text = AuxFunc().try_get_text(xpath=XpathResolver().questions_progress(), amount=1)
        number_list = [int(number) for number in re.findall(r'\d+', text)]
        return number_list[-1] - number_list[0]

    @staticmethod
    def reboot_question_page() -> None:
        """Reboot question page"""
        driver = driver_init.BrowserDriver().browser
        driver.refresh()
        driver.switch_to.alert.accept()
        AuxFunc().switch_to_frame(xpath=XpathResolver().iframe())
        AuxFunc().try_click(xpath=XpathResolver().popup_approve())

    def is_next_question(self, last_questions_left) -> bool:
        """Wait next question load"""
        for x in range(20):
            if last_questions_left == self.get_questions_left():
                time.sleep(1)
            else:
                return True
        return False


class TopicStrategyA(TopicStrategy):
    """Topic solve strategy for test where there is <ПРОДОЛЖИТЬ> button after clicked <ОТВЕТИТЬ> button"""

# class TopicStrategyB(TopicStrategy):
#     """Topic solve strategy for test where there is NO <ПРОДОЛЖИТЬ> button after clicked <ОТВЕТИТЬ> button"""
#
#     def solve_question(self, num: int):
#         """Solve current question"""
#         if num != 0:
#             if not self.is_next_question(self.last_questions_left):  # if next question not loaded, reload page
#                 self.reboot_question_page()
#         self.last_questions_left = self.get_questions_left()
#
#         q_solve = question_solve.QuestionSolve(self.question_strategy)
#         self.question_strategy = q_solve.solve_question()  # remember question solving strategy for current topic
