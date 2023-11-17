import time
from typing import Type

from playsound import playsound
from selenium.webdriver import ActionChains
import logging

from config import MUSIC_FILE_PATH
from exceptions import QuizEnded, NoFoundedElement
from log import print_log
from aux_functions import AuxFunc
from driver_init import driver
from web.xpaths import XpathResolver
from db import UserController, User

from logick.solve import question_solve
from logick.strat.theory_solve import TheoryStrategyA, TheoryStrategyB, TheorySolveStrategy

exception_topics = {
    'Буровые установки': ['Расставьте названия с верными номерами:'],
    'Транспортировка': ['Расставьте объекты по своим местам:']
}  # topics which some question cant be solved

video_topics = [
    'видеофильм',
    'видеоурок',
    'видеоинструкция',
    'видеолекция'
]  # topics with video only


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
        if all([topic not in self.topic_name.lower() for topic in video_topics]):
            theory_strategy = TheoryStrategyA(self.topic_name)
        else:
            theory_strategy = TheoryStrategyB()
        try:
            TheorySolveStrategy(theory_strategy).do_work()
        except Exception as ex:
            # AuxFunc().play_sound()
            print_log(
                message='-> Выпала ошибка при решении теории. Скорее всего она закончилась',
                exception=ex,
                silent=True
            )
            raise QuizEnded
        finally:
            self.update_db(theory_clicks=theory_strategy.theory_click_counter)

    def do_quiz(self):
        """Quiz"""

        # processing topics added to exception
        self.do_exception_question()

        if self.is_quiz():
            quiz_passed = self.solve_quiz()
            # if quiz not passed then call user to open new test
            if not quiz_passed:
                raise QuizEnded
            # if current test is passed then check if there is next topic and run solving again
            else:
                if AuxFunc().try_click(xpath=XpathResolver.next_test_part(), try_numb=5, window_numb=1):
                    print_log('В текущей теме найдена кнопка далее, продолжаю решать')
                    self.main()
        else:
            raise QuizEnded

    def solve_quiz(self) -> bool:
        """Solve current topic"""
        print_log("\n\n\n--> РЕШАЮ ТЕСТ")
        self.has_next_button = True
        AuxFunc().switch_to_frame(xpath=XpathResolver.iframe())
        # while there is question on page, continue solving
        question_num = 0
        while self.is_quiz():
            try:
                self.solve_question(question_num)
            except QuizEnded:
                break
            question_num += 1
        try:
            self.update_db(questions_amount=question_num)
            self.click_next_button(XpathResolver.results_button())

            if self.is_quiz_passed():
                print_log('Решение темы завершено')
                self.question_strategy = None
                return True

            self.click_next_button(XpathResolver.repeat_button())
            return self.solve_quiz()
        except Exception as ex:
            playsound(MUSIC_FILE_PATH)
            self.question_strategy = None
            print_log(message='[ERR] Возникла проблема при решении темы.', exception=ex)
            logging.exception("An error occurred during topic solving")
            input('-> Нажми Enter чтобы попробовать продолжить решение')
            self.main()

    def solve_question(self, num: int):
        """Solve current question"""
        if num != 0:
            if self.has_next_button is True:
                self.has_next_button = self.click_next_button(XpathResolver.continue_button())
            if not self.is_next_question(self.last_question_text):
                if AuxFunc().try_get_text(xpath=XpathResolver.continue_button(), try_numb=3):
                    raise QuizEnded
                if AuxFunc().try_get_text(xpath=XpathResolver.results_button(), try_numb=3):
                    raise QuizEnded

        q_solve = question_solve.QuestionSolve(strategy=self.question_strategy)
        self.last_question_text = AuxFunc().try_get_text(
            XpathResolver.question_text())  # remember last question page
        self.question_strategy = q_solve.solve_question()  # remember question solving strategy for current topic

    def do_exception_question(self):
        """Check if there is exceptions question and call user"""
        if self.topic_name not in exception_topics:
            return
        # check if there is question text
        try:
            question_text = AuxFunc().try_get_text(
                xpath=XpathResolver.question_text(),
                try_numb=2
            )
        except NoFoundedElement:
            return
        # checks if question text not empty
        if not question_text:
            return
        # checks if questions text contains exception question
        if question_text[0] not in exception_topics[self.topic_name]:
            return
        # call user if there is exception question
        playsound(MUSIC_FILE_PATH)
        print_log(message=f'\nТема: <{self.topic_name}> добавлена в исключения'
                          f'\nРеши вопрос сам и перейди к нормальному окну с вопросами')
        input('\nНажми Enter для продолжения')
        if not self.is_quiz():
            self.main()

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

    def is_quiz_passed(self):
        """Check if quiz solved"""
        # wait loading quiz_score
        for i in range(10):
            try:
                XpathResolver.quiz_score()
                break
            except NoFoundedElement:
                time.sleep(1)
                continue

        text = AuxFunc().try_get_text(xpath=XpathResolver.quiz_score(), amount=10)
        if text is None:
            playsound(MUSIC_FILE_PATH)
            print_log('-> Не прогрузился экран с результатами.')
            input('-> Перейди на экран с результатами и нажми Enter')
            self.is_quiz_passed()
        if ' не ' not in text:
            return True
        return False

    @staticmethod
    def is_next_question(last_questions_text: str) -> bool:
        """Wait next question load"""
        for i in range(1, 5):
            current_question_text = AuxFunc().try_get_text(XpathResolver.question_text())
            if current_question_text is None:
                return False
            if last_questions_text == current_question_text:
                time.sleep(1)
            else:
                return True
            # if i % 5 == 0:  # every 5 try reload page
            #     self.reboot_question_page()
        return False

    @staticmethod
    def is_quiz() -> bool:
        """Check if there is quiz question"""
        try:
            question_text = AuxFunc().try_get_text(
                xpath=XpathResolver.question_text(),
                try_numb=2
            )
            answer_text = AuxFunc().try_get_text(
                xpath=XpathResolver.answer_text(),
                try_numb=2
            )
        except NoFoundedElement:
            return False
        if question_text is None or answer_text is None:
            return False
        if len(question_text) > 1:
            return False
        return True

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
