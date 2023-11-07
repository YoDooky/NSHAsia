import time

from selenium.webdriver import ActionChains
import logging

import log
from exceptions import QuizEnded, NoFoundedElement
from log import print_log
from aux_functions import AuxFunc
from driver_init import driver
from web.xpaths import XpathResolver

from logick import strat, question_solve


class TopicStrategy:
    def __init__(self):
        self.last_question_text = None
        self.question_strategy = None
        self.has_next_button = True  # define if topic has <ПРОДОЛЖИТЬ> button after cliked <ОТВЕТИТЬ> button

    def main(self):
        self.question_strategy = None

        try:
            theory_strategy = strat.TheoryA()
            strat.TheorySolveStrategy(theory_strategy).do_work()
        except Exception as ex:
            AuxFunc().play_sound()
            print_log(message=f'{ex}', silent=True)
            res = input("\nПерейди на экран с другим тестом и нажми <Enter>")
            if not res:
                self.main()

        if self.is_quiz():
            quiz_passed = self.solve_topic()
            if not quiz_passed:
                res = input('Перейди на экран с другим тестом и нажми <Enter>\n')
                if not res:
                    self.main()
            else:  # if current test is passed then check if there is next topic and run solving again
                if AuxFunc().try_click(xpath=XpathResolver().next_test_part(), try_numb=5, window_numb=1):
                    print_log('В текущем топике найден еще тест, продолжаю решать')
                    self.main()
        else:
            AuxFunc().play_sound()
            res = input('\nВ теме нет теста. Перейди на экран с другим тестом и нажми <Enter>\n')
            if not res:
                self.main()

    def solve_topic(self) -> bool:
        """Solve current topic"""
        print_log("\n\n\n--> РЕШАЮ ТЕСТ")
        try:
            question_num = 0
            self.has_next_button = True
            AuxFunc().switch_to_frame(xpath=XpathResolver().iframe())

            # while there is question on page, continue solving
            while AuxFunc().try_get_text(
                    xpath=XpathResolver().question_text(),
                    amount=1,
                    try_numb=2
            ) and len(AuxFunc().try_get_text(
                xpath=XpathResolver().question_text(),
                try_numb=2
            )) == 1:
                try:
                    self.solve_question(question_num)
                except QuizEnded:
                    break
                question_num += 1

            self.click_next_button(XpathResolver().results_button())

            if self.is_topic_passed():
                print_log('Решение темы завершено')
                self.question_strategy = None
                return True

            self.click_next_button(XpathResolver().repeat_button())
            return self.solve_topic()
        except Exception as ex:
            self.question_strategy = None
            print_log(f'Ошибка: {ex}. Возникла проблема при решении темы.')
            logging.exception("An error occurred during topic solving")

    def solve_question(self, num: int):
        """Solve current question"""
        if num != 0:
            if self.has_next_button is True:
                self.has_next_button = self.click_next_button(XpathResolver().continue_button())
            if not self.is_next_question(self.last_question_text):  # if next question not loaded, reload page
                if AuxFunc().try_get_text(xpath=XpathResolver().continue_button(), try_numb=3):
                    raise QuizEnded
                if AuxFunc().try_get_text(xpath=XpathResolver().results_button(), try_numb=3):
                    raise QuizEnded

        q_solve = question_solve.QuestionSolve(strategy=self.question_strategy)

        self.last_question_text = AuxFunc().try_get_text(
            XpathResolver().question_text())  # remember last question page
        # if self.question_strategy is None:
        self.question_strategy = q_solve.solve_question()  # remember question solving strategy for current topic

    @staticmethod
    def click_next_button(mask: str):
        """Click button"""
        AuxFunc().switch_to_frame(xpath=XpathResolver().iframe())
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
    def reboot_question_page() -> None:
        """Reboot question page"""
        driver.refresh()
        driver.switch_to.alert.accept()
        AuxFunc().switch_to_frame(xpath=XpathResolver().iframe())
        AuxFunc().try_click(xpath=XpathResolver().popup_approve())

    def is_next_question(self, last_questions_text: str) -> bool:
        """Wait next question load"""
        for x in range(1, 4):
            current_question_text = AuxFunc().try_get_text(XpathResolver().question_text())
            if current_question_text is None:
                return False
            if last_questions_text == current_question_text:
                time.sleep(1)
            else:
                return True
            if x % 5 == 0:  # every 5 try reload page
                self.reboot_question_page()
        return False

    @staticmethod
    def is_quiz() -> bool:
        """Check if there is quiz question"""
        try:
            question_text = XpathResolver().question_text()
            if question_text:
                return True
        except NoFoundedElement:
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
