import re
import time
from selenium.webdriver import ActionChains
import logging

from log import print_log
from aux_functions import AuxFunc
from logick.question_solve import QuestionSolve
import driver_init
from web.xpaths import XpathResolver
from logick.strategy import TheorySolveStrategy
from logick.skip_theory import TheoryA


class TopicSolve:
    def __init__(self):
        self.topic_xpath = XpathResolver()

    def main(self):
        input('Перейди на экран с выбранной темой и нажми <Enter>')

        AuxFunc().switch_to_frame(xpath=self.topic_xpath.iframe())

        TheorySolveStrategy(TheoryA()).do_work()
        if not self.solve_topic():
            AuxFunc().play_sound()
            res = input('Возникла ошибка при решении теста. Перейди на экран с тестом и нажми <Enter>.\n'
                        'Нажми <q> и после <Enter> для выхода')
            if not res:
                self.main()

    def solve_topic(self) -> bool:
        """Solve current topic"""
        try:
            AuxFunc().switch_to_frame(xpath=self.topic_xpath.iframe())
            questions_left = self.get_questions_left()
            for i in range(questions_left + 1):
                self.solve_question(i)
            self.click_next_button(self.topic_xpath.results_button())

            if self.is_topic_passed():
                print_log('Решение темы завершено')
                return True

            self.click_next_button(self.topic_xpath.repeat_button())
            self.solve_topic()
        except Exception as ex:
            print_log(f'Ошибка: {ex}. Возникла проблема при решении курса. Пробую еще раз')
            logging.exception("An error occurred during topic solving")
            # reboot_question_page()
            # solve_topic()

    def solve_question(self, num: int):
        """Solve current question"""
        if num != 0:
            last_questions_left = self.get_questions_left()
            self.click_next_button(self.topic_xpath.continue_button())
            if not self.wait_next_question(last_questions_left):
                self.reboot_question_page()
        QuestionSolve().solve_question()

    def click_next_button(self, mask: str):
        """Click button"""
        AuxFunc().switch_to_frame(xpath=self.topic_xpath.iframe())
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

    def is_topic_passed(self):
        text = AuxFunc().try_get_text(xpath=self.topic_xpath.topic_score(), amount=1)
        # current_score = int(re.findall(r'\d+', text[-1])[0])
        # pass_score = int(re.findall(r'\d+', text[-3])[0])
        if ' не ' not in text:
            return True
        return False

    def get_questions_left(self) -> int:
        """Returns questions left from current topic"""
        text = AuxFunc().try_get_text(xpath=self.topic_xpath.questions_progress(), amount=1)
        number_list = [int(number) for number in re.findall(r'\d+', text)]
        return number_list[-1] - number_list[0]

    def reboot_question_page(self) -> None:
        """Reboot question page"""
        driver = driver_init.BrowserDriver().browser
        driver.refresh()
        driver.switch_to.alert.accept()
        AuxFunc().switch_to_frame(xpath=self.topic_xpath.iframe())
        AuxFunc().try_click(xpath=self.topic_xpath.popup_approve())

    def wait_next_question(self, last_questions_left) -> bool:
        """Wait next question load"""
        for x in range(20):
            if last_questions_left == self.get_questions_left():
                time.sleep(1)
            else:
                return True
        return False
