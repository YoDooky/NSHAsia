import time
from typing import Type

from selenium.webdriver import ActionChains
import logging

from exceptions import QuizEnded, NoFoundedElement
from log import print_log
from aux_functions import AuxFunc
from driver_init import driver
from web.xpaths import XpathResolver
from db import UserController, User

from logick.solve import question_solve
from logick.strat.theory_solve import TheoryStrategyA, TheorySolveStrategy


class TopicStrategy:
    def __init__(self, topic_name: str):
        self.topic_name = topic_name
        self.last_question_text = None
        self.question_strategy = None
        self.has_next_button = True  # define if topic has <ПРОДОЛЖИТЬ> button after cliked <ОТВЕТИТЬ> button

    def main(self):
        self.question_strategy = None
        self.do_theory()
        self.do_quiz()

    def do_theory(self):
        """Theory"""
        theory_strategy = TheoryStrategyA()
        try:
            TheorySolveStrategy(theory_strategy).do_work()
        except Exception as ex:
            # AuxFunc().play_sound()
            print_log(message=f'{ex}', silent=True)
            raise QuizEnded
        finally:
            self.update_db(theory_clicks=theory_strategy.theory_click_counter)

            # res = input("\nПерейди на экран с другим тестом и нажми <Enter>")
            # if not res:
            #     self.main()

    def do_quiz(self):
        """Quiz"""
        if self.is_quiz():
            quiz_passed = self.solve_quiz()
            # if quiz not passed then call user to open new test
            if not quiz_passed:
                # AuxFunc().play_sound()
                # res = input('Перейди на экран с другим тестом и нажми <Enter>\n')
                # if not res:
                #     self.main()
                raise QuizEnded
            # if current test is passed then check if there is next topic and run solving again
            else:
                if AuxFunc().try_click(xpath=XpathResolver.next_test_part(), try_numb=5, window_numb=1):
                    print_log('В текущей теме найдена кнопка далее, продолжаю решать')
                    self.main()
        else:
            # AuxFunc().play_sound()
            # res = input('\nВ теме нет теста. Перейди на экран с другим тестом и нажми <Enter>\n')
            # if not res:
            #     self.main()
            raise QuizEnded

    def solve_quiz(self) -> bool:
        """Solve current topic"""
        print_log("\n\n\n--> РЕШАЮ ТЕСТ")

        try:
            question_num = 0
            self.has_next_button = True
            AuxFunc().switch_to_frame(xpath=XpathResolver.iframe())
            # while there is question on page, continue solving
            while self.is_quiz():
                try:
                    self.solve_question(question_num)
                except QuizEnded:
                    break
                question_num += 1
            self.update_db(questions_amount=question_num)
            self.click_next_button(XpathResolver.results_button())

            if self.is_quiz_passed():
                print_log('Решение темы завершено')
                self.question_strategy = None
                return True

            self.click_next_button(XpathResolver.repeat_button())
            return self.solve_quiz()
        except Exception as ex:
            self.question_strategy = None
            print_log(f'Ошибка: {ex}. Возникла проблема при решении темы.')
            logging.exception("An error occurred during topic solving")

    def solve_question(self, num: int):
        """Solve current question"""
        if num != 0:
            if self.has_next_button is True:
                self.has_next_button = self.click_next_button(XpathResolver.continue_button())
            if not self.is_next_question(self.last_question_text):  # if next question not loaded, reload page
                if AuxFunc().try_get_text(xpath=XpathResolver.continue_button(), try_numb=3):
                    raise QuizEnded
                if AuxFunc().try_get_text(xpath=XpathResolver.results_button(), try_numb=3):
                    raise QuizEnded

        q_solve = question_solve.QuestionSolve(strategy=self.question_strategy)

        self.last_question_text = AuxFunc().try_get_text(
            XpathResolver.question_text())  # remember last question page
        # if self.question_strategy is None:
        self.question_strategy = q_solve.solve_question()  # remember question solving strategy for current topic

    @staticmethod
    def click_next_button(mask: str):
        """Click button"""
        AuxFunc().switch_to_frame(xpath=XpathResolver.iframe())
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
    def reboot_question_page() -> None:
        """Reboot question page"""
        driver.refresh()
        driver.switch_to.alert.accept()
        AuxFunc().switch_to_frame(xpath=XpathResolver.iframe())
        AuxFunc().try_click(xpath=XpathResolver.popup_approve())

    @staticmethod
    def is_quiz_passed():
        """Check if quiz solved"""
        text = AuxFunc().try_get_text(xpath=XpathResolver.topic_score(), amount=1)
        if ' не ' not in text:
            return True
        return False

    def is_next_question(self, last_questions_text: str) -> bool:
        """Wait next question load"""
        for x in range(1, 4):
            current_question_text = AuxFunc().try_get_text(XpathResolver.question_text())
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
            question_text = AuxFunc().try_get_text(
                xpath=XpathResolver.question_text(),
                try_numb=2
            )
        except NoFoundedElement:
            return False
        if question_text is None:
            return False
        if question_text[0] and len(question_text) == 1:
            return True
        return False

    def update_db(self, questions_amount: int = 0, theory_clicks: int = 0):
        """Updates user data in db for current topic"""
        if self.topic_name not in [data.topic_name for data in UserController().read()]:
            UserController().write(User(topic_name=self.topic_name))
        if questions_amount == 0 and theory_clicks == 0:  # if no data to update return
            return
        data_id = 1
        for data in UserController().read():
            if data.topic_name == self.topic_name:
                data_id = data.id
                theory_clicks += data.theory_clicks
                questions_amount += data.questions_amount
        UserController().update(
            id_=data_id,
            data={'questions_amount': questions_amount, 'theory_clicks': theory_clicks}
        )


class TopicStrategyA(TopicStrategy):
    """Topic solve strategy for test where there is <ПРОДОЛЖИТЬ> button after clicked <ОТВЕТИТЬ> button"""


class TopicSolveStrategy:
    """Strategy for solving topic"""

    def __init__(self, strategy: Type[TopicStrategy]):
        self.strategy = strategy

    def do_work(self, topic_name: str):
        return self.strategy(topic_name).main()
