import time
from dataclasses import dataclass
from typing import Type, List

from playsound import playsound
from selenium.common import NoAlertPresentException
from selenium.webdriver.remote.webelement import WebElement

from config import MUSIC_FILE_PATH
from db import UserController
from driver_init import driver
from aux_functions import AuxFunc
from exceptions import QuizEnded
from log import print_log
from logick.solve.topic_solve import TopicSolve
from web import CourseWebData, XpathResolver


@dataclass
class UserData:
    topic_name: str
    questions_amount: int
    theory_clicks: int


class CourseStrategy:
    MAX_TOPIC_ATTEMPS = 3  # maximum topic solve attemps

    def __init__(self):
        self.course_url = driver.current_url
        self.topic_attemps = 0

    def main(self):
        topics = CourseWebData().get_course_topics()
        print_log('--> В курсе найдены следующие темы:')
        for num, topic in enumerate(topics):
            print_log(f'*{num + 1}* {CourseWebData().get_course_name(topic)}')

        for topic_num in self.get_topics_from_user():
            self.topic_attemps = 0
            self.solve(topic_num)

        user_data = self.get_user_data()
        print_log(f'\n***************************** ИТОГ *********************************'
                  f'\nВсего вопросов: {user_data.questions_amount}'
                  f'\nВсего кликнутых теорий: {user_data.theory_clicks}')

    def solve(self, topic_num: int):
        """Solving demand topic"""
        topic = self.get_next_topic_link(topic_num)
        topic.click()
        time.sleep(5)
        topic_name = CourseWebData().get_course_name(topic)
        print_log(f'\n\n---> Выбираю тему: <{topic_name}>')
        try:
            self.continue_solve()
            TopicSolve().main(topic_name)
        except QuizEnded:
            self.end_solve()
            return
        except Exception as ex:
            self.end_solve()
            driver.get(self.course_url)
            time.sleep(5)
            print_log(f'[ERR]{ex}\n Не смог решить тему.\n'
                      f'Пробую еще раз')
            self.topic_attemps += 1
            # if number of attemps is too much then call user
            if self.topic_attemps > self.MAX_TOPIC_ATTEMPS:
                playsound(MUSIC_FILE_PATH)
                self.topic_attemps = 0
                input('Реши сам кожаный мешок и нажми <Enter>')
                return
            self.solve(topic_num)
        finally:
            user_data = self.get_user_data(topic_name)
            print_log(f'\n********************************************************************'
                      f'\nТема: {user_data.topic_name}'
                      f'\nКол-во вопросов: {user_data.questions_amount}'
                      f'\nКол-во кликнутых теорий: {user_data.theory_clicks}')

    @staticmethod
    def get_topics_from_user() -> List[int]:
        """Return user selected courses"""
        user_input = input('\nВведи номера курсов для решения через запятую, либо '
                           'через тире если нужно решить несколько подряд:')
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

    @staticmethod
    def get_next_topic_link(topic_num: int) -> WebElement:
        """Returns webelement by topic number"""
        driver.switch_to.window(driver.window_handles[0])
        topic_link = CourseWebData().get_course_topics()[topic_num - 1]
        return topic_link

    @staticmethod
    def continue_solve():
        """Intercepts pop-up window which asks to continue quiz"""
        try:
            # driver.switch_to.alert.accept()
            AuxFunc().switch_to_frame(xpath=XpathResolver.iframe())
            AuxFunc().try_click(xpath=XpathResolver.popup_approve(), try_numb=3)
            time.sleep(3)
        except NoAlertPresentException:
            pass

    def end_solve(self):
        """Close quiz window"""
        # for i in range(3):
        #     try:
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            driver.close()
        driver.switch_to.window(driver.window_handles[0])
        driver.get(self.course_url)
        # driver.find_element(By.XPATH, XpathResolver.close_quiz()).click()
        #     break
        # except Exception:
        #     time.sleep(1)
        #     continue
        time.sleep(3)

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
