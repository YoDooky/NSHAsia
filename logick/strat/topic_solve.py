import time
from typing import Type
from playsound import playsound

from app_types import TopicData, TopicType, UserMessages, PageType
from config import MUSIC_FILE_PATH
from exceptions import QuizEnded, NoFoundedElement, CantFindResultPage
from log import print_log
from aux_functions import AuxFunc
from driver_init import driver
from logick.strat import utils
from web.xpaths import XpathResolver
from db import UserController, User

from logick.solve import question_solve
from logick.strat.theory_solve import (
    TheorySolveStrategy,
    TheoryStrategy,
    TheoryStrategyA,
    TheoryStrategyB,
    TheoryStrategyC, TheoryStrategyD
)

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
    def __init__(self, topic_data: TopicData):
        self.question_strategy = None
        self.theory_strategy = None
        self.theory_solver = None  # TheorySolveStrategy object

        self.topic = topic_data
        self.last_question_text = None
        self.has_next_button = True  # define if topic has <ПРОДОЛЖИТЬ> button after cliked <ОТВЕТИТЬ> button
        self.page_type = None

    def main(self):
        self.question_strategy = None
        self.page_type = self._define_page_type()
        if self.page_type == PageType.theory:
            self.do_theory()
            self.do_quiz()
        elif self.page_type == PageType.quiz:
            AuxFunc().try_click(
                xpath=XpathResolver.continue_button(),
                focus_on=True,
                click_on=True,
                scroll_to=False,
                try_numb=3
            )
            if AuxFunc().try_click(
                xpath=XpathResolver.results_button(),
                focus_on=True,
                click_on=True,
                scroll_to=False,
                try_numb=3
            ):
                AuxFunc().try_click(
                    xpath=XpathResolver.repeat_button(),
                    focus_on=True,
                    click_on=True,
                    scroll_to=False,
                    try_numb=3
                )
            self.do_quiz()
        elif self.page_type == PageType.result_page:
            self.repeat_quiz_solve()

    def _define_page_type(self) -> PageType:
        """
        Define page type (quiz/theory/result_page)
        :return: PageType (quiz/theory/result_page)
        """
        if utils.is_quiz():
            return PageType.quiz
        # if theory_strategy is None its means that topic opened first time in this session
        # so there is not a page with quiz results
        elif self.theory_strategy is None:
            if AuxFunc.try_get_text(xpath=XpathResolver.quiz_result()):
                return PageType.result_page
        return PageType.theory

    def do_theory(self):
        """Theory"""
        # try to click start button to define topic type after
        AuxFunc().try_click(xpath=XpathResolver.start_button(), try_numb=8)
        time.sleep(5)
        if self.theory_strategy is None:
            self.theory_strategy = self._get_theory_strategy()
        try:
            if self.theory_solver is None:
                self.theory_solver = TheorySolveStrategy(self.theory_strategy)
            self.theory_solver.do_work()
        except Exception as ex:
            print_log(
                message='-> Выпала ошибка при решении теории. Скорее всего она закончилась',
                exception=ex,
                silent=True
            )
            raise QuizEnded
        finally:
            self.update_db(theory_clicks=self.theory_strategy.theory_click_counter)

    def do_quiz(self):
        """Quiz"""
        # processing topics added to exceptions
        self.do_exception_question()
        # if current topic is not quiz then topic is ended
        if not utils.is_quiz():
            raise QuizEnded
        # solving quiz
        self.solve_quiz()
        # if current test is passed then check if there is next topic and run solving again
        if self.is_quiz_passed():
            if AuxFunc().try_click(
                    xpath=XpathResolver.next_test_part(),
                    try_numb=5,
                    focus_on=True,
                    click_on=True
            ):
                print_log('В текущей теме найдена кнопка <Далее>, продолжаю решать')
                self.main()
            else:
                print_log('Решение темы завершено')
                self.question_strategy = None
                return
        # if quiz is not passed then try again
        else:
            time.sleep(3)
            self.repeat_quiz_solve()

    def solve_quiz(self):
        """Solve current topic"""
        print_log("\n\n\n--> РЕШАЮ ТЕСТ")
        self.has_next_button = True
        AuxFunc().switch_to_frame(xpath=XpathResolver.iframe())
        question_num = 0
        # while there is question on page, continue solving
        while utils.is_quiz():
            try:
                self.solve_question(question_num)
            except QuizEnded:
                break
            question_num += 1
        self.update_db(questions_amount=question_num)
        self.end_quiz_solve()

    def end_quiz_solve(self):
        """
        Go to quiz result page
        :return:
        """
        if not AuxFunc().try_click(
                xpath=XpathResolver.results_button(),
                focus_on=True,
                click_on=True,
                scroll_to=False,
                try_numb=5
        ):
            playsound(MUSIC_FILE_PATH)
            self.question_strategy = None
            print_log(message=UserMessages.cant_go_to_result_page)
            raise CantFindResultPage
            # input('-> Нажми Enter чтобы попробовать продолжить решение')
            # self.main()

    def repeat_quiz_solve(self):
        """
        # If there is <Повторить тест> button then click it, else reboot page and repeat
        solve from theory.
        :return:
        """
        repeat_button_mask = XpathResolver.repeat_button()
        if repeat_button_mask:
            print_log('-> Не набрано нужное количество баллов. Пробую нажать кнопку <Повторить тест>')
            AuxFunc().try_click(
                xpath=XpathResolver.repeat_button(),
                focus_on=True,
                click_on=True,
                scroll_to=False,
                try_numb=5
            )
            self.do_quiz()
        else:
            print_log('-> Не набрано нужное количество баллов. Пробую перезагрузить тест')
            driver.refresh()
            utils.close_alert()
            utils.set_popup(False)
            UserController().clear_table()
            # repeat solving from theory
            self.main()

    def solve_question(self, num: int):
        """Solve current question"""
        if num != 0:
            if self.has_next_button is True:
                self.has_next_button = AuxFunc().try_click(
                    xpath=XpathResolver.continue_button(),
                    focus_on=True,
                    click_on=True,
                    scroll_to=False,
                    try_numb=5
                )
            if not self.is_next_question(self.last_question_text):
                if AuxFunc().try_get_text(xpath=XpathResolver.results_button(), try_numb=3):
                    raise QuizEnded
                if AuxFunc().try_get_text(xpath=XpathResolver.continue_button(), try_numb=3):
                    if AuxFunc().try_get_text(xpath=XpathResolver.quiz_result(), try_numb=3):
                        raise QuizEnded

        q_solve = question_solve.QuestionSolve(strategy=self.question_strategy)
        self.last_question_text = AuxFunc().try_get_text(
            XpathResolver.question_text())  # remember last question page
        self.question_strategy = q_solve.solve_question()  # remember question solving strategy for current topic

    def _get_theory_strategy(self) -> TheoryStrategy:
        """Returns theory type"""
        if self.topic.type in [TopicType.page, TopicType.study_material]:
            return TheoryStrategyA()
        if self.topic.type in [TopicType.video]:
            return TheoryStrategyB()
        if not all([topic not in self.topic.name.lower() for topic in video_topics]):
            return TheoryStrategyB()
        elif AuxFunc().try_get_text(xpath=XpathResolver.quiz_form(), amount=1):
            return TheoryStrategyC()
        elif AuxFunc().try_get_text(xpath=XpathResolver.pdf_book(), amount=1):
            return TheoryStrategyD()
        else:
            return TheoryStrategyA()

    def do_exception_question(self):
        """Check if there is exceptions question and call user"""
        if self.topic.name not in exception_topics:
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
        if question_text[0] not in exception_topics[self.topic.name]:
            return
        # call user if there is exception question
        playsound(MUSIC_FILE_PATH)
        print_log(message=f'\nТема: <{self.topic.name}> добавлена в исключения'
                          f'\nРеши вопрос сам и перейди к нормальному окну с вопросами')
        input('\nНажми Enter для продолжения')
        if not utils.is_quiz():
            self.main()

    def is_quiz_passed(self):
        """Check if quiz solved"""
        text = ''
        for i in range(10):
            try:
                text = AuxFunc().try_get_text(xpath=XpathResolver.quiz_result(), amount=1)
                if text:
                    break
            except NoFoundedElement:
                time.sleep(1)
                continue
        if text in [None, '']:
            playsound(MUSIC_FILE_PATH)
            print_log('-> Не прогрузился экран с результатами.')
            raise CantFindResultPage
            # input('-> Перейди на экран с результатами и нажми Enter')
            # self.is_quiz_passed()
        if ' не ' in text:
            return False
        return True

    @staticmethod
    def is_next_question(last_questions_text: str) -> bool:
        """Wait next question load"""
        for i in range(5):
            current_question_text = AuxFunc().try_get_text(XpathResolver.question_text())
            if current_question_text is None:
                return False
            if last_questions_text == current_question_text:
                time.sleep(1)
            else:
                return True
        return False

    def update_db(self, questions_amount: int = 0, theory_clicks: int = 0):
        """Updates user data in db for current topic"""
        if self.topic.name not in [data.topic_name for data in UserController().read()]:
            UserController().write(User(topic_name=self.topic.name))
        if questions_amount == 0 and theory_clicks == 0:  # if no data to update return
            return
        data_id = 1
        for data in UserController().read():
            if data.topic_name == self.topic.name:
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

    def do_work(self, topic_data: TopicData):
        return self.strategy(topic_data).main()
