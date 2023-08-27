import logging
import re
import time

from selenium.webdriver.remote.webelement import WebElement
from typing import List

from exceptions import ImpossibleToClick
from db.controllers import DbDataController, WebDataController, TempDbDataController, DbAnswerController, \
    write_webdata_to_db
from db.models import WebData, DbData, DbAnswer, TempDbData
from get_webdata import WebDataA
from aux_functions import AuxFunc
from log import print_log
from solve.aux_funcs import GenerateVariant, CalculateVariants, get_random_delay


def click_answer(links: List[WebElement]):
    """Click answer and check if it was clicked"""
    try_numb = 5
    for link in links:
        for i in range(try_numb):
            try:
                time.sleep(get_random_delay())
                link.click()
            except Exception:
                print(f'Не удалось кликнуть по ответу. Попытка {i + 1} из {try_numb}')
                logging.exception("An error occurred during click to answer")
            finally:
                return
    raise ImpossibleToClick


def click_approve_button() -> bool:
    """Click <Ответить> button"""
    mask = '//button[@class="quiz-control-panel__button"]//*[contains(text(),"ОТВЕТИТЬ")]'
    if not AuxFunc().try_click(xpath=mask):
        return False


def get_score():
    """Returns current topic score"""
    mask = '//*[@class="quiz-top-panel__quiz-score-info quiz-top-panel__quiz-score-info_with-separator"]'
    topic_score_text = AuxFunc().try_get_text(xpath=mask, amount=1, try_numb=2)
    return re.findall(r'\d+', topic_score_text)[0]


def validate_db_data(main_data: WebData | DbData | TempDbData, comp_data: WebData | DbData | TempDbData) -> bool:
    """Checks if there is same data in both data"""
    if main_data.question != comp_data.question:
        return False
    comp_data_answers = [answer.text for answer in comp_data.answers]
    for answer in main_data.answers:
        if answer.text not in comp_data_answers:
            return False
    return True


class AnswerChoice:
    @staticmethod
    def get_answers_from_temp_db() -> List[WebElement]:
        """Returns answers from temp db if exist"""
        web_data = WebDataController().read_data()
        temp_data = TempDbDataController().read_data()
        for temp in temp_data:
            if not validate_db_data(main_data=temp, comp_data=web_data[0]):
                continue
            next_answers = CalculateVariants().get_next_variants(data=temp,
                                                                 prev_variant_num=temp.last_answer_combination)
            print_log(f'--> Вопрос найден во временной базе: \n {temp.question}'
                      f'\n-> Выбираю ответы на вопрос из временной базы: \n {next_answers}')
            return [WebDataA().get_link(answer) for answer in next_answers]
        first_answer = GenerateVariant().generate(web_data[0])
        print_log(f'--> Вопроса нет в базах: \n {web_data[0].question}'
                  f'\n-> Выбираю от пизды (нет) ответ: \n {first_answer}')
        return [WebDataA().get_link(first_answer)]

    @staticmethod
    def get_right_answers_from_db(db_data: List[DbData]) -> List[str]:
        web_data = WebDataController().read_data()
        for db in db_data:
            if not validate_db_data(main_data=db, comp_data=web_data[0]):
                continue
            return [answer.text for answer in db.answers]

    def get_right_answers_links(self) -> List[WebElement]:
        """If no data in DBData then returns first answer link"""
        db_data = DbDataController().read_data()
        web_data = WebDataController().read_data()
        for db in db_data:
            if not validate_db_data(main_data=db, comp_data=web_data[0]):
                continue
            right_answers = self.get_right_answers_from_db(db_data)
            print_log(f'--> Вопрос найден в базе: \n {db.question}'
                      f'\n-> Выбираю ответы на вопрос из базы: \n {[answer.text for answer in db.answers]}')
            return [WebDataA().get_link(answer) for answer in right_answers]
        return self.get_answers_from_temp_db()


class QuestionSolve:
    def solve_question(self):
        write_webdata_to_db()
        links = AnswerChoice().get_right_answers_links()
        start_score = get_score()

        click_answer(links)
        click_approve_button()

        # check results
        if start_score == get_score():
            self.write_if_wrong_result()
        elif start_score < get_score():
            self.write_if_correct_result()

    @staticmethod
    def write_if_wrong_result():
        """Update answer combination in temp db"""
        print_log('X  Ответ неверный')
        web_data = WebDataController().read_data()
        temp_data = TempDbDataController().read_data()
        for temp in temp_data:
            if not validate_db_data(main_data=temp, comp_data=web_data[0]):
                continue
            TempDbDataController().update_data(id_=temp.id,
                                               data={'last_answer_combination': temp.current_answer_combination})

    def write_if_correct_result(self):
        """Writes corrects data to db and delete it from temp db"""
        print_log('✔  Ответ правильный')
        web_data = WebDataController().read_data()
        if not self.validate_data(web_data):
            return
        correct_answers = self.__get_correct_answers()
        if not correct_answers:
            self.clear_temp_db_question(web_data)
            return
        db_data = DbData(question=web_data[0].question, topic=web_data[0].topic)
        DbDataController().write_data(db_data)
        for answer in correct_answers:
            DbAnswerController.write_data(DbAnswer(text=answer, dbdata=db_data))
        self.clear_temp_db_question(web_data)

    @staticmethod
    def __get_correct_answers() -> List[str] | bool:
        # temp_data = TempDbDataController().read_data()
        write_webdata_to_db()
        web_data = WebDataController().read_data()
        correct_answers = [answer.text for answer in web_data[0].answers if answer.is_selected]
        return correct_answers

    @staticmethod
    def clear_temp_db_question(web_data):
        """Check for same data in temp db and delete it"""
        temp_data = TempDbDataController().read_data()
        for temp in temp_data:
            if not validate_db_data(main_data=temp, comp_data=web_data[0]):
                continue
            TempDbDataController().delete_data(temp.id)

    @staticmethod
    def validate_data(web_data):
        """Check for same data in db with correct answers"""
        db_data = DbDataController().read_data()
        for db in db_data:
            if not validate_db_data(main_data=db, comp_data=web_data[0]):
                continue
            return False
        return True
