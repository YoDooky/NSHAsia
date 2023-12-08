import time
from dataclasses import dataclass
from typing import Type, List
from playsound import playsound

from app_types import UserMessages
from config import MUSIC_FILE_PATH
from db import UserController
from driver_init import driver
from aux_functions import AuxFunc
from exceptions import QuizEnded
from log import print_log
from logick.solve.topic_solve import TopicSolve
from logick.strat import utils
from logick.strat.decorators import FunctionTry
from web import CourseWebData, XpathResolver


@dataclass
class UserData:
    topic_name: str
    questions_amount: int
    theory_clicks: int


class CourseStrategy:
    MAX_TOPIC_ATTEMPS = 4  # maximum topic solve attemps

    def __init__(self):
        self.course_url = driver.current_url
        self.topic_attemps = 0
        self.topic_bad_status = ['не начат', 'в процессе', 'не пройден']
        self.course_topics = None
        self.current_topic = None

    def main(self):
        topics = CourseWebData().get_course_topics()
        print_log(f'{UserMessages.founded_next_topics}')
        for num, topic in enumerate(topics):
            print_log(f'*{num + 1}* {CourseWebData().get_topic_name(topic)}')

        # for topic_num in self.get_unsolved_topics():
        for topic_num in self.get_topics_from_user():
            self.topic_attemps = 0
            self.solve(topic_num)
            if not self.is_topic_solved(topic_num):
                self.repeat_solve(topic_num)
        user_data = self.get_user_data()
        print_log(f'\n***************************** ИТОГ *********************************'
                  f'\nВсего вопросов: {user_data.questions_amount}'
                  f'\nВсего кликнутых теорий: {user_data.theory_clicks}')

    def solve(self, topic_num: int):
        """Solving demand topic"""
        self.course_topics = CourseWebData().get_data()
        if not self.is_topic_solved(topic_num - 1):
            print_log(f'{UserMessages.try_solve_topic_again}'
                      f'\n{self.course_topics[topic_num - 1].name}')
            self.solve(topic_num - 1)
        self.current_topic = self.course_topics[topic_num - 1]
        AuxFunc().try_webclick(self.current_topic.link)
        print_log(f'{UserMessages.choose_topic} {self.current_topic.name}')
        time.sleep(10)
        try:
            utils.set_popup(True)
            TopicSolve().main(self.current_topic)
            self.end_solve()
            self.print_summary()
        except QuizEnded:
            self.end_solve()
            self.print_summary()
            return
        except Exception as ex:
            print_log(message=UserMessages.cant_solve_topic_try_again, exception=ex)
            self.repeat_solve(topic_num)

    def get_unsolved_topics(self) -> List[int]:
        """Returns all unsolved topics num"""
        topics = CourseWebData().get_data()
        unsolved_topics_num = []
        for topic_num, topic in enumerate(topics):
            if topic.status == '':
                unsolved_topics_num.append(topic_num + 1)
                continue
            if all([status not in topic.status.lower() for status in self.topic_bad_status]):
                continue
            unsolved_topics_num.append(topic_num + 1)
        return unsolved_topics_num

    @staticmethod
    def get_topics_from_user() -> List[int]:
        """Return user selected courses"""
        user_input = input(UserMessages.input_topics_nums)
        str_mod = user_input.split(',')
        str_comma = [int(s.strip()) for s in str_mod if '-' not in s]

        def get_str_dash(string_input: List[str]) -> List[int]:
            """Returns numbers with dashes as number list as range from and before dash"""
            str_dash = []
            for num in string_input:
                if '-' not in num:
                    continue
                str_dash.extend(
                    [i for i in range(int(num.split('-')[0].strip()),
                                      int(num.split('-')[1].strip()) + 1)]
                )
            return str_dash

        str_comma.extend(get_str_dash(str_mod))
        str_comma.sort()
        return str_comma

    def is_topic_solved(self, topic_num: int) -> bool:
        """Returns True if last topic has been solved"""
        if topic_num <= 1:
            return True
        topics_status = None
        for i in range(10):
            driver.switch_to.window(driver.window_handles[-1])
            topics_status = AuxFunc().try_get_text(XpathResolver.topic_status())
            if topics_status:
                break
        if topics_status is None:
            print_log(f'{UserMessages.cant_fint_topic_status}'
                      f'\n {self.course_topics[topic_num - 1]}')
            return False
        try:
            topic_status = topics_status[topic_num - 1]
        except IndexError:
            return False
        if not all([status not in topic_status.lower() for status in self.topic_bad_status]):
            print_log(f'{UserMessages.cant_solve_topic}'
                      f'\n{self.course_topics[topic_num - 1].name}')
            return False
        return True

    def repeat_solve(self, topic_num: int):
        """Repeat topic solve"""
        self.end_solve()
        driver.get(self.course_url)
        time.sleep(10)
        self.topic_attemps += 1
        # if number of attemps is too much then call user
        if self.topic_attemps > self.MAX_TOPIC_ATTEMPS:
            playsound(MUSIC_FILE_PATH)
            self.topic_attemps = 0
            input(UserMessages.max_solve_attempts_exceed)
            return
        self.solve(topic_num)

    @FunctionTry(message_to_user=UserMessages.cant_end_topic)
    def end_solve(self):
        """Close topic window and got to course topics"""
        time.sleep(10)
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            utils.close_alert()
            driver.close()
            time.sleep(1)
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(self.course_url)
        utils.close_alert()
        time.sleep(10)

    def print_summary(self):
        """Print topics summary"""
        user_data = self.get_user_data(self.current_topic.name)
        print_log(f'\n********************************************************************'
                  f'\nТема: {user_data.topic_name}'
                  f'\nКол-во вопросов: {user_data.questions_amount}'
                  f'\nКол-во кликнутых теорий: {user_data.theory_clicks}')

    @staticmethod
    def get_user_data(topic_name: str = '') -> UserData:
        """Returns user topic, questions amount in topic and theory clicks amount from db"""
        # count course sum questions and theory clicks
        if not topic_name:
            overall_questions = 0
            overall_theory_clicks = 0
            for data in UserController().read():
                overall_questions += data.questions_amount
                overall_theory_clicks += data.theory_clicks
            return UserData(
                topic_name='',
                questions_amount=overall_questions,
                theory_clicks=overall_theory_clicks,
            )
        # collect current topic data
        for data in UserController().read():
            if data.topic_name == topic_name:
                return UserData(
                    topic_name=data.topic_name,
                    questions_amount=data.questions_amount,
                    theory_clicks=data.theory_clicks
                )


class CourseStrategyA(CourseStrategy):
    """Basic course strategy"""


class CourseSolveStrategy:
    """Strategy for solving course"""

    def __init__(self, strategy: Type[CourseStrategy]):
        self.strategy = strategy

    def do_work(self):
        return self.strategy().main()
